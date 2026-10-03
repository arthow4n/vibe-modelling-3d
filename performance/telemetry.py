"""Explicit, bounded local Codex OTLP capture. Never persist raw OTLP bodies.

Numerical fields and fixed enums survive an allowlist; relationship keys are
pseudonymous. Foreground capture is optional. --install explicitly enables a
local user service and machine defaults for Remote Control/ordinary Codex launches.
"""
import argparse
from collections import Counter
import hashlib
import hmac
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import math
import os
from pathlib import Path
import secrets
import subprocess
import time

from performance.sessions import effort_name, model_name, nonnegative, timestamp

MAX_BYTES = 16 * 1024 * 1024
MAX_BODY = 4 * 1024 * 1024
MAX_RECORDS = 100_000
NAMES = {'run_turn', 'run_sampling_request', 'try_run_sampling_request',
         'stream_request', 'receiving_stream', 'handle_responses', 'receiving',
         'created', 'completed', 'text_delta', 'tool_input_delta',
         'reasoning', 'reasoning_summary_delta', 'reasoning_content_delta',
         'reasoning_summary_done', 'reasoning_summary_part_added', 'agent_message',
         'message_from_assistant', 'function_call', 'custom_tool_call',
         'server_model', 'rate_limits'}
LOG_NAMES = {'codex.conversation_starts', 'codex.api_request', 'codex.sse_event',
             'codex.websocket_request', 'codex.websocket_event'}
KINDS = {'response.created', 'response.completed', 'response.failed',
         'response.in_progress', 'response.output_item.added',
         'response.output_item.done', 'response.output_text.delta',
         'response.reasoning_text.delta', 'response.reasoning_summary_text.delta',
         'response.function_call_arguments.delta', 'unknown', 'parse_error'}
NUMBERS = {'duration_ms', 'ttft_ms', 'attempt', 'status', 'input_token_count',
           'output_token_count', 'cached_token_count', 'reasoning_token_count',
           'gen_ai.usage.input_tokens', 'gen_ai.usage.cache_read.input_tokens',
           'gen_ai.usage.output_tokens', 'codex.usage.reasoning_output_tokens'}
IDS = {'conversation.id': 'session', 'conversation_id': 'session',
       'thread_id': 'session', 'turn_id': 'turn'}


def scalar(value):
    if not isinstance(value, dict):
        return None
    for name in ('stringValue', 'intValue', 'doubleValue', 'boolValue'):
        if name in value:
            return value[name]
    return None


def number(value):
    if isinstance(value, str) and len(value) < 40:
        try:
            value = float(value)
        except ValueError:
            return None
    return nonnegative(value)


def attributes(rows):
    return {r['key']: scalar(r.get('value')) for r in rows
            if isinstance(r, dict) and isinstance(r.get('key'), str)}


def pseudonym(value, key, domain):
    if not isinstance(value, str) or not value or len(value) > 256:
        return None
    return hmac.new(key, (domain+':'+value).encode(), hashlib.sha256).hexdigest()[:32]


def approved(attrs, key):
    out = {}
    if (at := timestamp(attrs.get('event.timestamp'))) is not None:
        out['at'] = at
    for name in NUMBERS:
        n = number(attrs.get(name))
        if n is not None:
            out[name] = n
    for name in ('model', 'slug'):
        if name in attrs:
            out[name] = model_name(attrs[name])
    for name in ('model_reasoning_effort', 'codex.request.reasoning_effort', 'effort'):
        if name in attrs:
            out[name] = effort_name(attrs[name])
    version = attrs.get('app.version', attrs.get('service.version'))
    if isinstance(version, str):
        import re
        if re.fullmatch(r'\d+\.\d+\.\d+', version):
            out['version'] = version
    for name, domain in IDS.items():
        if ident := pseudonym(attrs.get(name), key, domain):
            out[domain+'_key'] = ident
    if 'event.name' in attrs:
        out['event_name'] = attrs['event.name'] if attrs['event.name'] in LOG_NAMES else 'other'
    if 'event.kind' in attrs:
        out['event_kind'] = attrs['event.kind'] if attrs['event.kind'] in KINDS else 'other'
    if isinstance(attrs.get('success'), bool):
        out['success'] = attrs['success']
    # Presence is the only approved part of errors; never keep exception text.
    if 'error.message' in attrs:
        out['has_error'] = True
    return out


def normalize(payload, signal, key):
    """OTLP JSON/protobuf-JSON input; no bodies, resources, names or free text escape."""
    resource_field, scope_field, item_field = (
        ('resourceSpans', 'scopeSpans', 'spans') if signal == 'traces'
        else ('resourceLogs', 'scopeLogs', 'logRecords'))
    for resource in payload.get(resource_field, []):
        resource_attrs = attributes(resource.get('resource', {}).get('attributes', []))
        for scope in resource.get(scope_field, []):
            for item in scope.get(item_field, []):
                attrs = resource_attrs | attributes(item.get('attributes', []))
                out = {'type': 'span' if signal == 'traces' else 'log', **approved(attrs, key)}
                for source, dest, domain in (('traceId', 'trace_key', 'trace'),
                                             ('spanId', 'span_key', 'span'),
                                             ('parentSpanId', 'parent_key', 'span')):
                    if ident := pseudonym(item.get(source), key, domain):
                        out[dest] = ident
                if signal == 'traces':
                    name = item.get('name')
                    out['name'] = name if name in NAMES else 'other'
                    for source, dest in (('startTimeUnixNano', 'start'), ('endTimeUnixNano', 'end')):
                        if (n := number(item.get(source))) is not None:
                            out[dest] = n/1e9
                    out['error_status'] = item.get('status', {}).get('code') in (2, 'STATUS_CODE_ERROR')
                    out['events'] = []
                    for event in item.get('events', []):
                        ev = approved(attributes(event.get('attributes', [])), key)
                        if (n := number(event.get('timeUnixNano'))) is not None:
                            ev['at'] = n/1e9
                        if ev:
                            out['events'].append(ev)
                else:
                    if out.get('event_name') not in LOG_NAMES:
                        continue
                    if (n := number(item.get('timeUnixNano'))) is not None:
                        out['at'] = n/1e9
                yield out


def decode(body, signal, content_type):
    if content_type.split(';')[0] == 'application/x-protobuf':
        from google.protobuf.json_format import MessageToDict
        if signal == 'traces':
            from opentelemetry.proto.collector.trace.v1.trace_service_pb2 import ExportTraceServiceRequest
            message = ExportTraceServiceRequest()
        else:
            from opentelemetry.proto.collector.logs.v1.logs_service_pb2 import ExportLogsServiceRequest
            message = ExportLogsServiceRequest()
        message.ParseFromString(body)
        return MessageToDict(message)
    if content_type.split(';')[0] != 'application/json':
        raise ValueError('Unsupported content type')
    data = json.loads(body)
    if not isinstance(data, dict):
        raise ValueError('Expected an object')
    return data


def config_text(port, token):
    return ('[otel]\nlog_user_prompt = false\nmetrics_exporter = "none"\n'
            f'exporter = {{ otlp-http = {{ endpoint = "http://127.0.0.1:{port}/v1/logs", protocol = "json", headers = {{ "x-workflow-capture" = "{token}" }} }} }}\n'
            f'trace_exporter = {{ otlp-http = {{ endpoint = "http://127.0.0.1:{port}/v1/traces", protocol = "json", headers = {{ "x-workflow-capture" = "{token}" }} }} }}\n')


class Capture(HTTPServer):
    def __init__(self, directory, port=0, control=None):
        self.key = bytes.fromhex(control['key']) if control else secrets.token_bytes(32)
        self.token = control['token'] if control else secrets.token_hex(24)
        self.counts = Counter()
        self.written = 0
        self.directory = directory
        directory.mkdir(parents=True, mode=0o700)
        self.output = (directory/'records.jsonl').open('x')
        (directory/'records.jsonl').chmod(0o600)
        super().__init__(('127.0.0.1', port), Handler)
        self.timeout = .25
        self.started = time.time()

    def append(self, rows):
        for row in rows:
            content = json.dumps(row, separators=(',', ':'))+'\n'
            size = len(content.encode())
            if self.written+size > MAX_BYTES or self.counts['records'] >= MAX_RECORDS:
                self.counts['limit_reached'] += 1
                return
            self.output.write(content)
            self.written += size
            self.counts['records'] += 1
        self.output.flush()

    def manifest(self, duration, active):
        data = {'schema': 1, 'source': 'codex-native-otel', 'key': self.key.hex(),
                'port': self.server_port, 'pid': os.getpid(), 'started': self.started,
                'expires': self.started+duration, 'active': active,
                'counts': dict(self.counts), 'bytes': self.written}
        path = self.directory/'capture.json'
        temporary = self.directory/'capture.tmp'
        with temporary.open('w') as f:
            json.dump(data, f)
        temporary.chmod(0o600)
        temporary.replace(path)


def install(repo, parent, disable=False):
    """Explicit machine-local activation; user config/service never enter Git."""
    home = Path(os.environ.get('CODEX_HOME', Path.home()/'.codex'))
    config = home/'config.toml'
    unit = Path.home()/'.config/systemd/user/codex-workflow-telemetry.service'
    remote_dropin = unit.parent/'codex-remote-control.service.d/50-workflow-telemetry.conf'
    begin = '# BEGIN managed workflow telemetry\n'
    end = '# END managed workflow telemetry\n'
    content = config.read_text() if config.exists() else ''
    if begin in content:
        before, rest = content.split(begin, 1)
        _, after = rest.split(end, 1)
        content = before+after
    if disable:
        config.write_text(content); config.chmod(0o600)
        subprocess.run(['systemctl', '--user', 'disable', '--now', unit.name], check=True, capture_output=True)
        if remote_dropin.exists() and remote_dropin.read_text().startswith('# Managed by performance.telemetry'):
            remote_dropin.unlink()
        subprocess.run(['systemctl', '--user', 'daemon-reload'], check=True, capture_output=True)
        return
    import tomllib
    if 'otel' in tomllib.loads(content):
        raise ValueError('Existing unmanaged OTel settings: merge deliberately before activation')
    control_path = parent/'otel-control.json'
    if control_path.exists():
        control = json.loads(control_path.read_text())
    else:
        import socket
        with socket.socket() as sock:
            sock.bind(('127.0.0.1', 0)); port = sock.getsockname()[1]
        control = {'port': port, 'key': secrets.token_hex(32), 'token': secrets.token_hex(24)}
        control_path.write_text(json.dumps(control)); control_path.chmod(0o600)
    repo = repo.resolve()
    if any(c in str(repo) for c in ('\n','\r')):
        raise ValueError('Unsupported newline in installation path')
    # systemd quoting, never shell interpolation. These are installation paths only.
    def quote(path):
        return '"'+str(path).replace('\\', '\\\\').replace('"', '\\"').replace('%', '%%')+'"'
    unit.parent.mkdir(parents=True, exist_ok=True)
    unit.write_text('[Unit]\nDescription=Local filtered Codex workflow telemetry\n'
                    '[Service]\nType=notify\nTimeoutStartSec=15\n'
                    'WorkingDirectory='+str(repo).replace('\\','\\\\').replace(' ', '\\x20').replace('%','%%')+'\n'
                    f'ExecStart={quote(repo/".venv/bin/python")} -m performance.telemetry --repo {quote(repo)} --control {quote(control_path)} --duration 28800\n'
                    'Restart=always\nRestartSec=3\nUMask=0077\n'
                    'NoNewPrivileges=true\nStandardOutput=null\nStandardError=journal\n'
                    '[Install]\nWantedBy=default.target\n')
    remote = subprocess.run(['systemctl','--user','cat','codex-remote-control.service'],capture_output=True)
    if remote.returncode == 0:
        remote_dropin.parent.mkdir(parents=True, exist_ok=True)
        remote_dropin.write_text('# Managed by performance.telemetry\n[Unit]\n'
                                 'Wants=codex-workflow-telemetry.service\n'
                                 'After=codex-workflow-telemetry.service\n')
    subprocess.run(['systemctl', '--user', 'daemon-reload'], check=True, capture_output=True)
    subprocess.run(['systemctl', '--user', 'enable', '--now', unit.name], check=True, capture_output=True)
    subprocess.run(['systemctl', '--user', 'restart', unit.name], check=True, capture_output=True)
    # Check actual readiness, not just systemctl's successful job submission.
    import urllib.request
    ready = False
    for _ in range(60):
        try:
            request = urllib.request.Request(f'http://127.0.0.1:{control["port"]}/v1/traces',
                data=b'{"resourceSpans":[]}', headers={'Content-Type':'application/json','x-workflow-capture':control['token']})
            with urllib.request.urlopen(request, timeout=.2) as response:
                ready = response.status == 200
            if ready: break
        except OSError:
            time.sleep(.05)
    if not ready:
        raise ValueError('Local receiver did not become ready; inspect the user service journal')
    # Write native configuration only once the receiver is running.
    block = config_text(control['port'], control['token'])
    config.write_text(content.rstrip()+'\n\n'+begin+block+end); config.chmod(0o600)


def prune(parent, current):
    """Enforce retention on startup too, including bundles left by a killed process."""
    import shutil
    old = sorted((d for d in parent.glob('otel-*') if d.is_dir() and not d.is_symlink()),
                 key=lambda d: d.stat().st_mtime, reverse=True)
    for d in old[20:]:
        if d != current:
            shutil.rmtree(d)


class Handler(BaseHTTPRequestHandler):
    def setup(self):
        super().setup()
        self.connection.settimeout(3)

    def log_message(self, *args):
        pass

    def do_POST(self):
        server = self.server
        if not hmac.compare_digest(self.headers.get('x-workflow-capture', ''), server.token):
            self.send_error(403); return
        if self.path not in ('/v1/logs', '/v1/traces'):
            self.send_error(404); return
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if not 0 < length <= MAX_BODY or self.headers.get('Content-Encoding', 'identity') != 'identity':
                self.send_error(413); return
            body = self.rfile.read(length)
            signal = self.path.rsplit('/', 1)[-1]
            data = decode(body, signal, self.headers.get('Content-Type', ''))
            server.append(normalize(data, signal, server.key))
            server.counts['accepted_batches'] += 1
        except Exception:
            # Never print decoder exceptions, which may quote a private payload.
            server.counts['rejected_batches'] += 1
            self.send_error(400); return
        response = b'{}' if 'json' in self.headers.get('Content-Type', '') else b''
        self.send_response(200)
        self.send_header('Content-Type', self.headers.get('Content-Type', 'application/json'))
        self.send_header('Content-Length', str(len(response)))
        self.end_headers()
        self.wfile.write(response)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[1])
    p.add_argument('--duration', type=int, default=7200, help='Foreground capture seconds (1..86400)')
    p.add_argument('--port', type=int, default=0, help='Loopback port; default chooses a free port')
    p.add_argument('--stop', type=Path, help='Request shutdown of this local capture bundle')
    p.add_argument('--install', action='store_true', help='Enable the local user service and native machine defaults')
    p.add_argument('--disable', action='store_true', help='Remove managed defaults and stop/disable the user service')
    p.add_argument('--control', type=Path, help=argparse.SUPPRESS)
    args = p.parse_args(argv)
    if not 1 <= args.duration <= 86400 or not 0 <= args.port <= 65535:
        p.error('Select bounded duration and a valid port')
    from performance.workflow import local_directory
    root = args.control.resolve().parents[1] if args.control else Path(os.environ.get('ENGINEERING_DATA', args.repo/'.execution'))
    parent = local_directory(root, args.repo)
    if args.install or args.disable:
        install(args.repo, parent, args.disable)
        print(json.dumps({'native_machine_telemetry': 'disabled' if args.disable else 'enabled',
                          'service': 'codex-workflow-telemetry.service'}))
        return 0
    if args.stop:
        target = args.stop.resolve()
        if target.parent != parent.resolve() or not (target/'capture.json').is_file():
            p.error('Stop requires a capture directly beneath the ignored analysis directory')
        (target/'stop').touch(mode=0o600)
        return 0
    directory = parent/('otel-'+secrets.token_hex(8))
    control = json.loads(args.control.read_text()) if args.control else None
    server = Capture(directory, control['port'] if control else args.port, control)
    import signal
    stopping = False
    def stop_signal(signum, frame):
        nonlocal stopping
        stopping = True
    signal.signal(signal.SIGTERM, stop_signal)
    try:
        server.manifest(args.duration, True)
        prune(parent, directory)
        # Make the Remote Control dependency wait for a listening receiver,
        # rather than only for Python's process to have started.
        if address := os.environ.get('NOTIFY_SOCKET'):
            import socket
            address = '\0'+address[1:] if address.startswith('@') else address
            with socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM) as notifier:
                notifier.connect(address); notifier.sendall(b'READY=1')
        print(json.dumps({'local_capture': str(directory), 'port': server.server_port,
                          'expires_in_seconds': args.duration}), flush=True)
        deadline = time.monotonic()+args.duration
        last_count = -1
        while not stopping and time.monotonic() < deadline and not server.counts['limit_reached'] and not (directory/'stop').exists():
            server.handle_request()
            if last_count != server.counts['accepted_batches']+server.counts['rejected_batches']:
                server.manifest(args.duration, True)
                last_count = server.counts['accepted_batches']+server.counts['rejected_batches']
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close(); server.output.close(); server.manifest(args.duration, False)
        prune(parent, directory)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

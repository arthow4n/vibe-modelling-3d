"""Best-effort OpenTelemetry spans and local versioned performance records.

No SDK/global provider mutation; per-process exporters survive fresh/forked workers.
No output, environment values, argument values or exception messages are retained.
"""
import base64
from contextlib import contextmanager
import contextvars
import json
import os
from pathlib import Path
import platform
import resource
import threading
import time
import uuid
from .identity import ROOT, digest, fingerprint

_active = contextvars.ContextVar('engineering_run', default=None)
_providers = {}
_lock = threading.Lock()


def data_root():
    return Path(os.environ.get('ENGINEERING_DATA', ROOT/'.execution'))


def _hex_ids(value):
    if isinstance(value, dict):
        for k, v in value.items():
            if k in ('traceId', 'spanId', 'parentSpanId') and v:
                value[k] = base64.b64decode(v).hex()
            else:
                _hex_ids(v)
    elif isinstance(value, list):
        for item in value:
            _hex_ids(item)


def _tracer(run_id):
    key = (os.getpid(), run_id)
    if key in _providers:
        return _providers[key].get_tracer('engineering.execution', '1')
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace.export import SimpleSpanProcessor, SpanExporter, SpanExportResult
    from opentelemetry.exporter.otlp.proto.common.trace_encoder import encode_spans
    from google.protobuf.json_format import MessageToDict

    class LocalExporter(SpanExporter):
        def export(self, spans):
            try:
                path = data_root()/'traces'/f'{run_id}-{os.getpid()}.otlp.jsonl'
                path.parent.mkdir(parents=True, exist_ok=True)
                data = MessageToDict(encode_spans(spans))
                _hex_ids(data)
                with _lock, path.open('a') as output:
                    output.write(json.dumps(data, separators=(',', ':'))+'\n')
                return SpanExportResult.SUCCESS
            except Exception:
                return SpanExportResult.FAILURE
        def shutdown(self):
            pass
    provider = TracerProvider(resource=Resource({'service.name': 'engineering.execution',
        'engineering.schema_version': 1, 'engineering.run_id': run_id, 'process.pid': os.getpid()}))
    provider.add_span_processor(SimpleSpanProcessor(LocalExporter()))
    _providers[key] = provider
    # Do not retain providers for every command in long-lived processes.
    if len(_providers) > 64:
        _providers.pop(next(iter(_providers))).shutdown()
    return provider.get_tracer('engineering.execution', '1')


@contextmanager
def span(name, **attributes):
    if os.environ.get('ENGINEERING_TRACE') == '0':
        yield None
        return
    run_id = _active.get() or os.environ.get('ENGINEERING_RUN_ID')
    if not run_id:
        yield None
        return
    try:
        from opentelemetry import trace
        from opentelemetry.propagate import extract
        tracer = _tracer(run_id)
        parent = None
        if not trace.get_current_span().get_span_context().is_valid:
            parent = extract({'traceparent': os.environ.get('ENGINEERING_TRACEPARENT', '')})
        manager = tracer.start_as_current_span(name, context=parent, attributes=attributes,
            record_exception=False, set_status_on_exception=False)
        current = manager.__enter__()
    except Exception:
        yield None
        return
    try:
        yield current
    except BaseException as exc:
        current.set_attribute('failure.type', type(exc).__name__)
        current.set_status(trace.Status(trace.StatusCode.ERROR))
        raise
    finally:
        try:
            manager.__exit__(None, None, None)
        except Exception:
            pass


def child_environment(env=None):
    values = dict(env or os.environ)
    from .resources import inherited_budget,current_affinity
    budget=inherited_budget()
    if budget:values['ENGINEERING_LEASE_THREADS']=str(budget)
    affinity=current_affinity()
    if affinity:values['ENGINEERING_AFFINITY']=affinity
    if _active.get():
        values['ENGINEERING_RUN_ID'] = _active.get()
    try:
        from opentelemetry.propagate import inject
        carrier = {}; inject(carrier)
        if carrier.get('traceparent'):
            values['ENGINEERING_TRACEPARENT'] = carrier['traceparent']
    except Exception:
        pass
    return values


def write_record(run_id, record):
    try:
        path = data_root()/'runs'/f'{run_id}.json'
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(f'.{os.getpid()}.tmp')
        temporary.write_text(json.dumps({'schema_version': 1, **record}, separators=(',', ':'))+'\n')
        temporary.replace(path)
    except Exception:
        pass


def retain(max_runs=500, days=14):
    """Bound normal run groups; protect active/recent files from concurrent cleanup."""
    try:
        cutoff = time.time()-days*86400
        runs = sorted((data_root()/'runs').glob('*.json'), key=lambda p: p.stat().st_mtime, reverse=True)
        for i, p in enumerate(runs):
            if (i >= max_runs or p.stat().st_mtime < cutoff) and p.stat().st_mtime < time.time()-3600:
                for directory in ('traces', 'resources', 'profiles'):
                    for artifact in (data_root()/directory).glob(f'{p.stem}*'):
                        artifact.unlink(missing_ok=True)
                p.unlink(missing_ok=True)
    except Exception:
        pass


@contextmanager
def run(name, source=None, strategy='isolated', argv=()):
    run_id = uuid.uuid4().hex
    token = _active.set(run_id)
    started = time.time_ns(); clock = time.monotonic()
    before = resource.getrusage(resource.RUSAGE_SELF)
    record = dict(run_id=run_id, operation=name, strategy=strategy, start_unix_ns=started,
        source_sha256=digest(source) if source and Path(source).is_file() else None,
        source=str(source) if source else None, arguments_sha256=fingerprint(argv),
        python=platform.python_version(), platform=" ".join((platform.system(),platform.release(),platform.machine())),
        lock_sha256=digest(ROOT/'uv.lock'), status='running')
    try:
        with span(name, strategy=strategy) as current:
            if current:
                record['trace_id'] = format(current.get_span_context().trace_id, '032x')
            yield record
            record.setdefault('exit_code', 0)
            record['status'] = record.get('status') if record.get('status') != 'running' else ('completed' if record['exit_code'] == 0 else 'failed')
    except BaseException as exc:
        record['status'] = 'interrupted' if isinstance(exc, KeyboardInterrupt) else 'failed'
        record['failure_type'] = type(exc).__name__
        raise
    finally:
        after = resource.getrusage(resource.RUSAGE_SELF)
        record.update(elapsed_seconds=time.monotonic()-clock,
            observer_cpu_seconds=(after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime),
            observer_max_rss_kib=after.ru_maxrss)
        write_record(run_id, record)
        retain()
        _active.reset(token)


def operation(name):
    """Instrument a controlled API; create a run when called outside a shared command."""
    from functools import wraps
    def decorate(function):
        @wraps(function)
        def wrapped(*args, **kwargs):
            if _active.get() or os.environ.get('ENGINEERING_RUN_ID'):
                with span(name):
                    return function(*args, **kwargs)
            with run(name) as record:
                answer=function(*args, **kwargs)
                if isinstance(answer,int):record["exit_code"]=answer
                return answer
        return wrapped
    return decorate

"""Durable metadata for interrupted work; never automatically replay side effects."""
import json
import os
from pathlib import Path
import time
from .identity import fingerprint
from .telemetry import data_root


def update(request,status,**details):
    try:
        folder=data_root()/'jobs';folder.mkdir(parents=True,exist_ok=True)
        path=folder/f'{request["run_id"]}.json'
        previous=json.loads(path.read_text()) if path.is_file() else {}
        record=dict(previous)
        record.update(schema_version=1,run_id=request['run_id'],kind=request['kind'],
            source=request['source'],source_sha256=request['source_sha256'],
            arguments_sha256=fingerprint(request.get('arguments',[])),identity=request.get('identity'),
            owner_pid=os.getpid(),updated_unix_ns=time.time_ns())
        record.update(status=status,**details)
        temporary=path.with_suffix('.tmp');temporary.write_text(json.dumps(record)+'\n');temporary.replace(path)
    except Exception:pass


def check_restart(run_id,source,arguments):
    path=data_root()/'jobs'/f'{run_id}.json'
    record=json.loads(path.read_text())
    from .identity import digest
    if record['source_sha256']!=digest(source) or record['arguments_sha256']!=fingerprint(list(arguments)):
        raise ValueError('Restart inputs differ from the retained run; use an ordinary new execution for changed inputs')
    return record

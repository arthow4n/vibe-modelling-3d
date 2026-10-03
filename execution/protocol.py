"""Private Unix socket JSON protocol; stdio descriptors preserve streaming/stdin."""
import array
import hashlib
import json
import os
from pathlib import Path
import socket
import struct
import tempfile
from .identity import ROOT

MAX_MESSAGE=16*1024*1024


def socket_path():
    identity=hashlib.sha256(str(ROOT).encode()).hexdigest()[:16]
    folder=Path(tempfile.gettempdir())/f'engineering-{os.getuid()}-{identity}'
    folder.mkdir(mode=0o700,exist_ok=True)
    if folder.stat().st_uid!=os.getuid() or folder.stat().st_mode&0o077:
        raise PermissionError('Execution socket directory is not private')
    return folder/'coordinator.sock'


def send(connection, value, fds=()):
    data=json.dumps(value,separators=(',',':')).encode()
    if len(data)>MAX_MESSAGE:raise ValueError('Execution message exceeds limit')
    packet=struct.pack('!I',len(data))+data
    if fds:
        sent=connection.sendmsg([packet],[(socket.SOL_SOCKET,socket.SCM_RIGHTS,array.array('i',fds))])
        connection.sendall(packet[sent:])
    else:connection.sendall(packet)


def receive(connection, descriptors=False):
    if descriptors:
        header,ancillary,flags,_=connection.recvmsg(4,socket.CMSG_SPACE(3*array.array('i').itemsize))
        fds=[]
        for level,kind,data in ancillary:
            if level==socket.SOL_SOCKET and kind==socket.SCM_RIGHTS:
                values=array.array('i');values.frombytes(data[:len(data)//values.itemsize*values.itemsize]);fds.extend(values)
        if flags&socket.MSG_CTRUNC:raise ValueError('Truncated file descriptors')
    else:
        header=connection.recv(4);fds=[]
    while len(header)<4:
        chunk=connection.recv(4-len(header))
        if not chunk:raise EOFError('Execution connection closed')
        header+=chunk
    size=struct.unpack('!I',header)[0]
    if size>MAX_MESSAGE:raise ValueError('Execution message exceeds limit')
    parts=[];remaining=size
    while remaining:
        data=connection.recv(min(65536,remaining))
        if not data:raise EOFError('Execution connection closed')
        parts.append(data);remaining-=len(data)
    value=json.loads(b''.join(parts))
    return (value,fds) if descriptors else value

"""Build the narrowly scoped native restart-check correction as a FEBio plugin.

Invoke through execute.py; SDK and output are explicit external directories.
The original installed runtime is never changed.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
from execution.process import run


COMMIT = '3ef37856289269674827e1748313b6224c4041a7'
SDK_HEADER_TREE_SHA256 = '4d89d82ed8fc0f56e21570bcc71c3b43326aeb6d37e897d7c6ed2d6e1f388fd3'
SDK_HASHES = {
    'NumCore/FGMRESSolver.cpp':'d35dbb1b5a25ae6506f57b1e5813ea18129fb0d03736cdb4420d5adfd8218967',
    'NumCore/FGMRESSolver.h':'fe0d0608dbbf2fe7d76b81bc9d567ea78df338234850b890b3a42c50bb8b20d9',
    'FECore/version.h':'54c642d2426221028c203c1f65b86d84cb998c1eeae5598b9f00c2fea43a3184',
}
# This experiment targets the inspected official Linux runtime, not arbitrary ABI
# compatibility. Another build needs its own reviewed source/runtime association.
RUNTIME_HASHES = {
    'bin/febio4':'c00b733dccf86f6696c504c739dda6dc9f42e63b9cf651e8149985ff783fb4b0',
    'lib/libnumcore.so':'3057297e029a344388a5018847ecd7eaa2423f57a60bbabcfaa35a0e3ae3b3f2',
    'lib/libfecore.so':'7fd1f21a0efb9a9a26782b85015cc3b8666b8e477a94f6084e576258f0b8e035',
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build(sdk, runtime, output):
    for root, expected in ((sdk,SDK_HASHES),(runtime,RUNTIME_HASHES)):
        for name, value in expected.items():
            if digest(root/name)!=value:
                raise ValueError(f'Unreviewed source/runtime identity: {root/name}')
    headers={str(p.relative_to(sdk)):digest(p) for folder in ('FECore','NumCore')
             for p in sorted((sdk/folder).rglob('*')) if p.suffix in ('.h','.hpp','.inl')}
    header_digest=hashlib.sha256(json.dumps(headers,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    if header_digest!=SDK_HEADER_TREE_SHA256:
        raise ValueError('Unreviewed FEBio SDK header tree')
    output.mkdir(parents=True,exist_ok=False)
    local=Path(__file__).resolve().parent
    for name in ('FGMRESSolver.cpp','FGMRESSolver.h'):
        shutil.copyfile(sdk/'NumCore'/name,output/name)
    run(['patch','--batch','--forward','--input',str(local/'recheck.patch')],cwd=output,check=True)
    for suffix in ('cpp','h'):
        source=output/f'FGMRESSolver.{suffix}'
        text=source.read_text().replace('FGMRESSolver','RestartFGMRESSolver')
        if suffix=='cpp':
            old='#include "mkl_rci.h"\n#include "mkl_blas.h"\n#include "mkl_spblas.h"'
            if text.count(old)!=1:raise ValueError('Unexpected native MKL includes')
            text=text.replace(old,'#include "mkl_rci_abi.h"')
        (output/f'RestartFGMRESSolver.{suffix}').write_text(text)
    for name in ('mkl_rci_abi.h','plugin.cpp'):
        shutil.copyfile(local/name,output/name)
    library=output/'libfgmres_restart_checked.so'
    command=['g++','-std=c++17','-O2','-fPIC','-shared','-DMKL_ISS',f'-I{sdk}',f'-I{sdk/"NumCore"}',
             str(output/'RestartFGMRESSolver.cpp'),str(output/'plugin.cpp'),f'-L{runtime/"lib"}',
             f'-Wl,-rpath,{runtime/"lib"}','-lfecore','-lnumcore','-o',str(library)]
    run(command,check=True)
    manifest=dict(commit=COMMIT,sdk_hashes=SDK_HASHES,sdk_header_tree_sha256=header_digest,runtime_hashes=RUNTIME_HASHES,
        sdk=str(sdk),runtime=str(runtime),command=command,
        compiler=subprocess.check_output(['g++','--version'],text=True),
        recipe_sha256={p.name:digest(p) for p in sorted(local.iterdir()) if p.is_file()},
        generated_source_sha256={p.name:digest(p) for p in sorted(output.glob('*')) if p.suffix in ('.cpp','.h')},
        plugin_sha256=digest(library))
    (output/'build_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(dict(plugin=str(library),sha256=digest(library))))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sdk',type=Path,required=True)
    parser.add_argument('--runtime',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    build(args.sdk.resolve(),args.runtime.resolve(),args.output.resolve())

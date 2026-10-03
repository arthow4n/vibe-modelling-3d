"""Fresh editable source imports while retaining locked dependency bytecode."""
import importlib.abc
import importlib.machinery
from pathlib import Path
import sys
import sysconfig


class FreshLoader(importlib.machinery.SourceFileLoader):
    def get_code(self,fullname):
        return self.source_to_code(self.get_data(self.path),self.path)


class FreshFinder(importlib.abc.MetaPathFinder):
    def __init__(self):
        self.environments=tuple(Path(sysconfig.get_path(p)).resolve() for p in ('purelib','platlib','stdlib','platstdlib'))

    def find_spec(self,fullname,path=None,target=None):
        spec=importlib.machinery.PathFinder.find_spec(fullname,path,target)
        if spec and isinstance(spec.loader,importlib.machinery.SourceFileLoader):
            # Most imports are locked dependencies. Avoid resolving every path's
            # symlinks and stat'ing its ancestors before rejecting those imports.
            import os
            if any(spec.origin.startswith(str(p)+os.sep) for p in self.environments):return None
            origin=Path(spec.origin).resolve()
            if not any(origin.is_relative_to(p) for p in self.environments):
                spec.loader=FreshLoader(fullname,spec.origin)
                return spec
        return None


def install(source):
    sys.meta_path[:]=[f for f in sys.meta_path if not isinstance(f,FreshFinder)]
    sys.meta_path.insert(0,FreshFinder())

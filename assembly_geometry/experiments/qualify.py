"""Run assembly qualification within the existing admitted execution budget."""
from pathlib import Path
import sys
import pytest

ROOT = Path(__file__).resolve().parents[2]
if __name__ == '__main__':
    sys.exit(pytest.main(['-q', str(ROOT/'tests/test_assembly_geometry.py'),
                         str(ROOT/'tests/test_assembly_consumers.py'), *sys.argv[1:]]))

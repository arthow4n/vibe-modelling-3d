"""Synthetic closed/open/corrupt STL cases; no CadQuery dependency."""
from pathlib import Path
import struct
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from check_exports import mesh_components

TETRA = [((0,0,0),(0,1,0),(1,0,0)), ((0,0,0),(1,0,0),(0,0,1)),
         ((0,0,0),(0,0,1),(0,1,0)), ((1,0,0),(0,1,0),(0,0,1))]

def binary(triangles):
    return b' '*80 + struct.pack('<I',len(triangles)) + b''.join(
        struct.pack('<12fH',0,0,0,*(v for p in tri for v in p),0) for tri in triangles)

class MeshTests(unittest.TestCase):
    def run_mesh(self, data):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'fixture.stl';path.write_bytes(data)
            return mesh_components(path)

    def test_two_components_and_translated_volume(self):
        moved=[tuple(tuple(p[k]+(10 if k==0 else 0) for k in range(3)) for p in tri) for tri in TETRA]
        result=self.run_mesh(binary(TETRA+moved))
        self.assertEqual(len(result),2)
        for component in result:
            self.assertAlmostEqual(component['volume_mm3'],1/6)

    def test_rejects_missing_face(self):
        with self.assertRaisesRegex(ValueError,'Open or nonmanifold'):
            self.run_mesh(binary(TETRA[:-1]))

    def test_rejects_reversed_face(self):
        with self.assertRaisesRegex(ValueError,'winding'):
            self.run_mesh(binary([tuple(reversed(TETRA[0]))]+TETRA[1:]))

    def test_rejects_degenerate(self):
        with self.assertRaisesRegex(ValueError,'Degenerate'):
            self.run_mesh(binary([((0,0,0),(0,0,0),(1,0,0))]))

    def test_rejects_nonfinite(self):
        with self.assertRaisesRegex(ValueError,'Nonfinite'):
            self.run_mesh(binary([((float('nan'),0,0),(0,1,0),(1,0,0))]))

    def test_rejects_truncation_and_ascii(self):
        for raw in (binary(TETRA)[:-1],b'solid tetra\nendsolid tetra'):
            with self.assertRaises(ValueError):self.run_mesh(raw)

if __name__=='__main__':unittest.main()

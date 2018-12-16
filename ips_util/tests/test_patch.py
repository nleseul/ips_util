from unittest import TestCase
import os
import tempfile

from ips_util import Patch

class TestPatch(TestCase):

    def setUp(self):
        self.source = bytes([0] * 10)
        self.target = bytes([0, 0, 0, 1, 1, 0, 2, 2, 2, 2])

        self.patch = Patch()
        self.patch.add_record(0x3, bytes([1, 1]))
        self.patch.add_rle_record(0x6, bytes([2]), 4)

    def test_patch_core(self):
        result = self.patch.apply(self.source)
        self.assertEqual(result, self.target)

    def test_patch_encode_decode(self):
        encoded_patch = self.patch.encode()

        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(encoded_patch)
            f.close()

            decoded_patch = Patch.load(f.name)

            result = decoded_patch.apply(self.source)
            self.assertEqual(result, self.target)

            os.unlink(f.name)

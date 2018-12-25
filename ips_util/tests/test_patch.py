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
        temp_patch = TestPatch.__save_and_reload(self.patch)

        result = temp_patch.apply(self.source)
        self.assertEqual(result, self.target)

    def test_patch_padding(self):
        self.patch.add_record(0x20, bytes([1]))

        temp_patch = TestPatch.__save_and_reload(self.patch)
        result = temp_patch.apply(self.source)

        self.assertEqual(len(result), 0x21)

    def test_patch_truncation(self):
        self.patch.set_truncate_length(0x5)

        temp_patch = TestPatch.__save_and_reload(self.patch)
        result = temp_patch.apply(self.source)

        self.assertEqual(len(result), 0x5)

    def test_patch_eof_edge_case(self):
        eof_value = int.from_bytes(b'EOF', byteorder='big')
        with self.assertRaises(RuntimeError):
            self.patch.add_record(eof_value, bytes([1]))

    def test_create_eof_edge_case(self):
        eof_value = int.from_bytes(b'EOF', byteorder='big')

        source = bytes(eof_value + 10)
        target = bytearray(bytes(eof_value + 10))
        target[eof_value - 1] = 2
        target[eof_value] = 1

        patch = Patch.create(source, target)

        temp_patch = TestPatch.__save_and_reload(patch)
        result = temp_patch.apply(source)

        self.assertEqual(len(result), eof_value + 10)
        self.assertEqual(result[eof_value - 1], 2)
        self.assertEqual(result[eof_value], 1)

    def test_create_equal_length(self):
        created_patch = Patch.create(self.source, self.target)

        temp_patch = TestPatch.__save_and_reload(self.patch)
        result = temp_patch.apply(self.source)

        self.assertEqual(result, self.target)

    def test_create_padded_length(self):
        target_with_padding = self.target + bytes([0] * 10) + bytes([1])
        created_patch = Patch.create(self.source, target_with_padding)

        temp_patch = TestPatch.__save_and_reload(created_patch)
        result = temp_patch.apply(self.source)

        self.assertEqual(result, target_with_padding)

    def test_create_padded_length_all_zero(self):
        target_with_padding = self.target + bytes([0] * 10)
        created_patch = Patch.create(self.source, target_with_padding)

        temp_patch = TestPatch.__save_and_reload(created_patch)
        result = temp_patch.apply(self.source)

        self.assertEqual(result, target_with_padding)

    def test_create_truncated_length(self):
        target_truncated = self.target[:5]
        created_patch = Patch.create(self.source, target_truncated)

        temp_patch = TestPatch.__save_and_reload(created_patch)
        result = temp_patch.apply(self.source)

        self.assertEqual(result, target_truncated)

    @staticmethod
    def __save_and_reload(patch):
        encoded_patch = patch.encode()
        decoded_patch = None

        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(encoded_patch)
            f.close()

            decoded_patch = Patch.load(f.name)

            os.unlink(f.name)

        return decoded_patch


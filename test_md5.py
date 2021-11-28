import unittest
import md5


class TestMain(unittest.TestCase):
    def test_convert_to_bytes(self):
        for x, n, expected in [(0x3b, 2, b'\x3b\x00'), (0x608c, 4, b'\x8c\x60\x00\x00')]:
            with self.subTest(x=x, n=n, expected=expected):
                self.assertEqual(md5.convert_to_bytes(x, n), expected)

    def test_get_padding_len(self):
        for len_input, expected in [(8, 48), (100, 20), (184, 64)]:
            with self.subTest(len_input=len_input, expected=expected):
                self.assertEqual(md5.get_padding_len(len_input), expected)

    def test_get_padding_bytes(self):
        self.assertEqual(md5.get_padding_bytes(49), b'\x80\x00\x00\x00\x00\x00\x00')

    def test_split_bytes(self):
        self.assertEqual(md5.split_bytes(b'\x00\x01\x02\x03\x04', 2), [b'\x00\x01', b'\x02\x03', b'\x04'])

    def test_convert_to_ints(self):
        ary = b'\x00\x00\x00\x00\x02\x00\x00\x00\x34\x12\x00\x00'
        self.assertEqual(md5.convert_to_ints(ary), [0x00, 0x02, 0x1234])

    def test_rotate_left_bit(self):
        for x, n, expected in [(0x1, 8, 0x100), (0x80000000, 3, 0x4)]:
            with self.subTest(x=x, n=n):
                self.assertEqual(md5.rotate_left_bit(x, n), expected)

    def test_move_right(self):
        for l, expected in [([0, 1, 2, 3], [3, 0, 1, 2]), ([2, 4, 6], [6, 2, 4])]:
            with self.subTest(l=l, expected=expected):
                self.assertEqual(md5.move_right(l), expected)

    def test_get_joined_hex(self):
        self.assertEqual(md5.get_joined_hex([0, 1, 2]), "000000000100000002000000")

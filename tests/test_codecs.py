"""Offline regression checks. No HA, USB or serial dependency."""
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import runtime_codec as short
import protocol_reference as extended


class CodecTests(unittest.TestCase):
    def test_known_crc_vectors(self):
        self.assertEqual(short.crc16(b'123456789'), 0x4B37)
        self.assertEqual(extended.crc32_raw(b'123456789'), 0x2DFD2D88)

    def test_captured_extended_packet(self):
        known = bytes.fromhex('5a a5 00 00 0b 66 04 20 00 00 00 02 00 00 08 a3')
        self.assertEqual(extended.runtime_extended(0x66, 0x04200000, bytes.fromhex('00020000')), known)

    def test_short_read_layout(self):
        body = short.decode(short.read_words())
        self.assertEqual(body, bytes.fromhex('03 06 38 00 02'))

    def test_energy_slots_and_signature_not_overwritten(self):
        packets = short.write_frames(['1234', '-50', '75', '24.0', '8.2', '1.7', 'OFFLINE'])
        self.assertEqual(len(packets), 7)
        for i, packet in enumerate(packets):
            body = short.decode(packet)
            self.assertEqual(body[0], 0x10)
            self.assertEqual(int.from_bytes(body[1:3], 'big'), 0x600 + 8 * i)
            self.assertEqual(len(body[3:]), 16)
            self.assertEqual(body[-1], 0)

    def test_corruption_rejected(self):
        packet = bytearray(short.read_words())
        packet[4] ^= 1
        with self.assertRaises(ValueError): short.decode(packet)
        with self.assertRaises(ValueError): short.decode(bytes(packet[:-1]))

    def test_reject_outside_runtime_block(self):
        for address, count in ((0x5FF, 1), (0x63A, 1), (0x639, 2), (0x600, 0), (0x600, 9)):
            with self.subTest(address=address, count=count):
                with self.assertRaises(ValueError): short.read_words(address, count)

    def test_reject_invalid_strings(self):
        for value in ('x' * 16, '\n', '\u041f'):
            with self.subTest(value=value):
                with self.assertRaises(ValueError): short.encode_strings([value] + ['--'] * 6)


if __name__ == '__main__':
    unittest.main()

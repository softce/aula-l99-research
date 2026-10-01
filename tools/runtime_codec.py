"""Offline examples for the matching custom energy UI. No device access.

SPDX-License-Identifier: GPL-2.0-only
"""
import struct

BASE = 0x0600
WORDS = 56
SIGNATURE_ADDRESS = BASE + WORDS
SIGNATURE = (0x454E, 0x4531)


def crc16(data):
    crc = 0xFFFF
    for value in data:
        crc ^= value
        for _ in range(8):
            crc = (crc >> 1) ^ (0xA001 if crc & 1 else 0)
    return crc


def frame(body):
    if not 1 <= len(body) <= 253:
        raise ValueError('Invalid short frame body length')
    return b'\x5a\xa5' + bytes([len(body) + 2]) + body + struct.pack('<H', crc16(body))


def decode(packet):
    if len(packet) < 6 or packet[:2] != b'\x5a\xa5' or len(packet) != packet[2] + 3:
        raise ValueError('Invalid short frame')
    body = packet[3:-2]
    if crc16(body) != int.from_bytes(packet[-2:], 'little'):
        raise ValueError('CRC mismatch')
    return body


def read_words(address=SIGNATURE_ADDRESS, count=2):
    if type(address) is not int or type(count) is not int or not 1 <= count <= 8:
        raise ValueError('Invalid address/count')
    if not BASE <= address < address + count <= SIGNATURE_ADDRESS + 2:
        raise ValueError('Outside documented energy block')
    return frame(b'\x03' + struct.pack('>HH', address, count))


def encode_strings(items):
    if len(items) != 7:
        raise ValueError('Expected seven strings')
    result = bytearray()
    for text in items:
        data = text.encode('ascii')
        if len(data) > 15 or any(v < 32 or v > 126 for v in data):
            raise ValueError('Expected printable ASCII, max 15 bytes')
        result.extend(data.ljust(16, b'\0'))
    return bytes(result)


def write_frames(items):
    """Encode only; a real client must verify layout and read back every chunk."""
    data = encode_strings(items)
    return [frame(b'\x10' + struct.pack('>H', BASE + offset // 2) + data[offset:offset + 16])
            for offset in range(0, len(data), 16)]


if __name__ == '__main__':
    print('OFFLINE ONLY: synthetic values; no serial/USB access')
    print('signature read:', read_words().hex(' '))
    for packet in write_frames(['1234', '-50', '75', '24.0', '8.2', '1.7', 'HA 12:34:56']):
        print('write example:', packet.hex(' '))

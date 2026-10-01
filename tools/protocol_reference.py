"""Offline reference from LT7689 sources and AULA updater static analysis.

No USB/serial access. Boot packets are NOT a complete, verified flasher.
Runtime extended framing is validated against 1269 recorded packets.
"""
import struct
import zlib


def crc16_modbus(data: bytes) -> int:
    crc = 0xffff
    for byte in data:
        crc ^= byte
        for _ in range(8):
            crc = (crc >> 1) ^ (0xa001 if crc & 1 else 0)
    return crc


def crc32_raw(data: bytes) -> int:
    """Reflected IEEE polynomial, init=0, xorout=0 (not default zlib CRC)."""
    return (zlib.crc32(data, 0xffffffff) ^ 0xffffffff) & 0xffffffff


def runtime_extended(opcode: int, address: int, data: bytes) -> bytes:
    body = bytes([opcode]) + struct.pack('>I', address) + data
    length = len(body) + 2
    if length > 0xffff:
        raise ValueError('extended frame too long')
    return b'\x5a\xa5\x00' + struct.pack('>H', length) + body + struct.pack('<H', crc16_modbus(body))


def external_read_candidate(address: int, count: int = 16) -> bytes:
    """SDK command 0x65. Not tested on live L99; only encodes a request."""
    if not 1 <= count <= 2048:
        raise ValueError('SDK read count must be 1..2048')
    return runtime_extended(0x65, address, struct.pack('>H', count))


def decode_runtime_extended(packet: bytes) -> dict:
    if len(packet) < 12 or packet[:3] != b'\x5a\xa5\x00':
        raise ValueError('not an extended address frame')
    length = int.from_bytes(packet[3:5], 'big')
    if len(packet) != 5 + length:
        raise ValueError('length mismatch')
    if crc16_modbus(packet[5:-2]) != int.from_bytes(packet[-2:], 'little'):
        raise ValueError('CRC mismatch')
    return {'opcode': packet[5], 'address': int.from_bytes(packet[6:10], 'big'), 'data': packet[10:-2]}


def boot_mcu_data_reference(offset: int, data: bytes) -> bytes:
    """Encoding only. Function VA varies by updater; offset depends on boot state."""
    if not 1 <= len(data) <= 2048:
        raise ValueError('use the observed updater chunk range 1..2048')
    body = b'\x4a\x30' + struct.pack('<IH', offset, len(data)) + data
    return body + struct.pack('<I', crc32_raw(body))


def boot_external_data_reference(address: int, flag: int, data: bytes) -> bytes:
    """Encoding only; flag semantics and device state require further analysis."""
    if not 1 <= len(data) <= 2048:
        raise ValueError('use the observed updater chunk range 1..2048')
    body = b'\x6c' + struct.pack('<IBH', address, flag, len(data)) + data
    return body + struct.pack('<I', crc32_raw(body))


if __name__ == '__main__':
    # Known request from capture_red_picture.pcapng, offset 0x70866c.
    known = bytes.fromhex('5a a5 00 00 0b 66 04 20 00 00 00 02 00 00 08 a3')
    assert runtime_extended(0x66, 0x04200000, struct.pack('>I', 0x20000)) == known
    assert decode_runtime_extended(known)['address'] == 0x04200000
    assert crc16_modbus(b'123456789') == 0x4b37
    assert crc32_raw(b'123456789') == 0x2dfd2d88
    # Exercise carry at the point the upstream length packing wraps.
    packet = runtime_extended(0x64, 0x041e0000, bytes(250))
    assert packet[3:5] == b'\x01\x01'
    assert decode_runtime_extended(packet)['data'] == bytes(250)
    print('Offline reference checks passed; no device opened.')

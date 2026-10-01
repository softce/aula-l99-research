"""Offline extraction only. Does not open USB/COM, launch an updater, or flash anything.

Usage: python extract_l99_reset_assets.py path/to/L99_reset_20260525.zip output_directory
Offsets apply only to the exact SHA256-verified screen updater below.
"""
import hashlib
import json
from pathlib import Path
import sys
import zipfile

EXPECTED = '8d52849afefeadf3a5d28a5e226f2c7a372a9376e1286f35c286d9b820d1ae84'
FILES = {
    'UartTFT-II_Flash.bin': (0x03FDD1B4, 0x079B01C4, '4cb3fa5c77eea973a2b62ca61873f071692694f4c9a1832507fe2c8c9ba582b4'),
    'HFD_Code_V2.2.bin': (0x003685BA, 305800, '432e358cac96fb930ab680ada6f953c9005027c58b31b7ee3bb6bc7868ef35cf'),
    'HFD_Code_V2.3.bin': (0x003B3042, 313652, 'a76806ada9648d2672bbebead8a9bb396c0bc6f3a0a071e22e99001ac3359d03'),
}

def main():
    archive, destination = map(Path, sys.argv[1:3])
    with zipfile.ZipFile(archive) as z:
        candidates = [i for i in z.infolist() if i.file_size == 194946048]
        if len(candidates) != 1:
            raise ValueError('Expected exactly one 194946048-byte screen container')
        data = z.read(candidates[0])
    if hashlib.sha256(data).hexdigest() != EXPECTED:
        raise ValueError('Container SHA256 mismatch; refusing offset-based extraction')
    verified = {}
    for name, (offset, size, expected) in FILES.items():
        raw = data[offset:offset + size]
        if len(raw) != size or hashlib.sha256(raw).hexdigest() != expected:
            raise ValueError(f'Payload verification failed: {name}')
        verified[name] = raw
    destination.mkdir(parents=True, exist_ok=True)
    for name, raw in verified.items():
        path = destination / name
        if path.exists() and path.read_bytes() != raw:
            raise FileExistsError(f'Refusing to overwrite different file: {path}')
        path.write_bytes(raw)
    print(json.dumps({name: {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}
                      for name, raw in verified.items()}, indent=2))

if __name__ == '__main__':
    main()

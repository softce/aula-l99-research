# Protocols, MCUs, and addresses

[Contents](../README.md) · [Русская версия](ru/protocol.md)

## Screen runtime variables: the path actually used

The bridge opens USB Serial `EEEF:268A` at 115200, standard 8N1, with DTR/RTS disabled. Writes begin only after reading the expected UI signature. The signature checks agreement between the application and resource layout; it is not cryptographic attestation of the entire firmware.

Short runtime frame:

```text
5A A5 | length:u8 | body | CRC16(body):LE16
length = len(body) + 2
CRC16: reflected polynomial 0xA001, init 0xFFFF

read body:  03 | word_address:BE16 | word_count:BE16
write body: 10 | word_address:BE16 | word_0:BE16 | word_1:BE16 | ...
```

In the client used here, a read response starts with the request body, followed by BE16 word values. Writes were sent in chunks of up to eight words and verified by reading them back. Absence of a write ACK alone does not establish success. This channel updates runtime RAM; it is not ISP flashing.

The addresses below are **16-bit runtime word indices**, not UI-file offsets or CPU pointers:

| Address | Content |
|---|---|
| `0x0600` | Current PV power |
| `0x0608` | Grid power |
| `0x0610` | Battery charge |
| `0x0618` | Floor temperature |
| `0x0620` | Daily PV energy |
| `0x0628` | Daily grid import |
| `0x0630` | Status / last-update time |
| `0x0638..0x0639` | Signature: words `0x454E, 0x4531` — `ENE1` |

Each text field occupies eight words, or 16 bytes. An ASCII string of at most 15 bytes is zero-padded to 16. Seven fields total 56 words. ASCII-byte pairs are packed as BE16 words in the data representation and wire encoding. Run `python tools/runtime_codec.py` for synthetic examples; it only prints bytes and sends nothing.

On connection failure, the application attempts to write `--` and `OFFLINE` if the screen remains available. When the sender stops, old numbers can remain on the device: the native widget does not know their age. A timestamp helps identify stale readings.

## Three distinct packet families

1. The short `5A A5` runtime frames above address UI variables.
2. Extended runtime frames use `5A A5 00`, a BE16 length, and a BE32 address. Examples are in `tools/protocol_reference.py`. Not every SDK command has been tested on L99.
3. Updater ISP packets, such as `4A 30`, use another mode and address interpretation. The offline codec is not a complete erase/program/finish sequence.

In the inspected ISP_V2.2 EXE with SHA256 `64ebb98d66af0fc03484e0528a9467bdce410d0d86305e6d757246d4889df476`, the function at VA `0x00403EA0` builds:

```text
4A 30 | offset:LE32 | payload_length:LE16 | payload | CRC32:LE32
```

CRC32 uses the reflected IEEE polynomial, init=0, xorout=0, over the prefix and payload. It is not an unadjusted `zlib.crc32(data)` call. `123456789` produces `0x2DFD2D88`; CRC16/MODBUS of the same string is `0x4B37`.

In this updater version, a `6D 01 selector` query and comparison of the flash ID against `0x00EFAA21` select HFD V2.2/V2.3. `Flash.ini` maps `EFAA21` to W25N01GV. This is analysis of software and its supported-chip list, not a measurement of the flash on our specimen. Do not choose V2.3 merely because its number is higher.

## Why LT7689 was a misleading initial lead

The LT7689 SDK uses the same USB ID, but the updater supports multiple families. Startup code in the extracted HFD `.bin` images disassembles correctly as little-endian M*Core:

```text
V2.2: base/VBR 0x6000A000, entry 0x60011620
V2.3: base/VBR 0x60010000, entry 0x600174B0
startup SP: 0x00874FFC
```

The first word is the entry address, not an ARM initial MSP. Instructions such as `mtcr ... vbr`, startup behavior, and the memory map are consistent with LT168. Check the exact hash before applying offsets: identically named HFD_Code files can contain different bytes.

The **LT168 family** map from the manufacturer's documentation:

| Region | CPU address |
|---|---|
| Boot ROM, 8 KiB | `0x00000000..0x00001FFF` |
| SRAM, 768 KiB | `0x00800000..0x008BFFFF` |
| QSPI0 / QSPI1 / QSPI2 mapping | `0x60000000 / 0x70000000 / 0x80000000` |
| USB controller / watchdog | `0x40160000 / 0x40130000` |

This is not a measured L99 flash layout. We have neither a bootloader dump nor independently verified hardware recovery for our specimen. A teardown of another L99 reports HFD168BDP, HFD80CP100, and GT911; equivalence between HFD168BDP and a specific LT168 pinout remains a hypothesis. The LT7689 SDK helps compare UI protocols, but is not a ready CPU/linker target for our board.

## Main keyboard: the important resource 4000 correction

The keyboard reset EXE contains both a ZIP with `SN32F290.hex` and a separate PE `RT_RCDATA` resource **4000**. Looking only for HEX misses a significant image.

| Field | Value |
|---|---|
| Keyboard EXE SHA256 | `0a946a5d41a872f32e3f3cbdd0d73f9dd7058ea17d3f2a89b2b1bf5c3ed6b217` |
| Resource file offset / RVA | `0x1BAA4C / 0x1C764C` |
| Size | 262144 bytes |
| Resource SHA256 | `e5e43f6babdcc3e1e6390026e8ae5b66dffc40535105cb38be019a95a5bfde00` |
| Initial SP / reset vector | `0x20002F60 / 0x00007F95` |
| USB descriptor offset | `0x14160`: `0C45:800A`, bcdDevice `0106` |
| AULA L99 UTF-16 string | `0x14314` |

The stock updater does load this PE resource. Boot PID `0C45:7140` was found in its executable SN32F290 table. This is stronger evidence than the earlier inactive INI template, but still not live identification of our specimen's bootloader. The exact MCU and matrix wiring needed for QMK have not been established. A related Ajazz port is not L99 firmware.

## From a screen code to HID: why entering F13 is not enough

Screen-side addresses below refer to the official HFD V2.3 with SHA256 `a76806ada9648d2672bbebead8a9bb396c0bc6f3a0a071e22e99001ac3359d03`:

- `0x6002248C..0x600224B4`: constructs `41 FF FF key_hi key_lo` and calls transmitter `0x60049D98`.
- Keyboard resource 4000 parses the header / `41 FF FF` branch at `0x127EA..0x1281E`.
- Codes `0x30..0x40` select counters in RAM at `0x200022C4`; function `0x688..0x6CA` generates key-down/key-up.
- The key table is at **`0x19D7C`**; the serializer is at `0x2596`.

Codes `0x003B/0x003C` select HID usages `0x59/0x5A`, NumPad1/2. Writing `0x0068/0x0069` into the UI does not turn them into F13/F14: that screen code does not produce the desired event in the inspected branch.

A candidate using screen codes 1/2 and changing two bytes of the **keyboard** table at `0x19D8D/0x19D8E` to HID usages `0x68/0x69` worked in limited emulation. Real functions were executed, F13/F14 buffers were produced, and 254 other low-byte codes were checked. However, the full boot/main loop, MMIO, and actual USB transmission were not modeled; possible dynamic conflicts were not completely excluded. This candidate was never flashed to the keyboard.

The stock keyboard updater audit found 4096 blocks of 64 bytes: **256 KiB starting at address 0**, even for a two-byte change. The checksum is a sum of LE16 words modulo 65536, not a signature or full readback. The working project therefore retained numpad interception, which delivered an HA panel without an experimental replacement of the main keyboard's code.

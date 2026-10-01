# AULA L99 screen and Home Assistant research

[Full Russian write-up](README.md)

This is a documentation-first account of turning an AULA L99 touchscreen into a 12-button Home Assistant panel and a live energy display. The experiments were tested on one keyboard in September 2026; this public write-up was prepared on October 1, 2026.

## The idea

We modified UI resources and page/touch records in `UartTFT-II_Flash.bin`, while retaining the stock executable MCU logic. Touch buttons reuse the screen's known keypad commands. The keyboard emits numpad events, a Windows background application suppresses those events, and an explicitly configured Home Assistant action runs on the PC.

The return path is different: the PC reads HA sensors and writes bounded ASCII strings to screen runtime variables over its USB serial interface. Native text widgets render the values; static Cyrillic labels are bitmaps. The clock and energy page share the same data block.

## Key findings

- Keyboard runtime USB: `0C45:800A`; screen USB serial: `EEEF:268A`.
- The inspected HFD screen executables contain little-endian **M*Core** code consistent with **LT168**, not evidence of an LT7689 Cortex-M4 target. USB IDs alone do not establish CPU identity.
- The 127,599,044-byte UI image contains 30 pages and several embedded projects. Their file offsets are not MCU addresses.
- The keyboard reset EXE has both a legacy `SN32F290.hex` and a distinct 256 KiB **PE resource 4000**. The latter contains the matching L99 descriptors and screen-key handler.
- F13/F14 remapping was exercised in a limited emulator only. It is not a hardware-tested firmware release.
- The Windows numpad workaround works without Num Lock but cannot distinguish another physical numpad. The top number row is unaffected.
- Factory recovery worked for incorrect typing on our specimen, but arbitrary bootloader failure recovery remains unverified.

## Reading and tools

The detailed Russian chapters cover [architecture](docs/architecture.md), [image format](docs/image-format.md), [runtime/ISP and MCU analysis](docs/protocol.md), [recovery and failed experiments](docs/recovery.md), and [offline reproduction](docs/reproduce.md). Tables, addresses and packet layouts are usable independently of the language.

The included Python tools only process local files/bytes: an SHA-256-gated extractor, UI inspector and protocol example codec. No updater is launched, no USB/COM device is opened. See `docs/reproduce.md` for commands. This is **not a ready-to-flash HOME release**: vendor images, SDK, updater binaries, personal settings and the private application build are not included.

Thanks to [gavindi/Aula_L99_Linux](https://github.com/gavindi/Aula_L99_Linux), [HuldaLloyd/lt7689](https://github.com/HuldaLloyd/lt7689), [Salamor/aula-l99-open-widgets](https://github.com/Salamor/aula-l99-open-widgets) and the hardware/protocol researchers credited in [sources](docs/sources.md). Our tools and write-up are GPL-2.0-only; third-party firmware and extracted artwork retain their original rights.

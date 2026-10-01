# Reproduction: start without connecting a keyboard

[Contents](../README.md) · [Русская версия](ru/reproduce.md)

Every tool in this repository operates on files or bytes. None reads HA configuration, opens USB/COM, launches an EXE, or flashes a device.

## Setup

Local validation used Python 3.12. From the repository root:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m unittest discover -s tests -v
.venv\Scripts\python.exe tools/protocol_reference.py
.venv\Scripts\python.exe tools/runtime_codec.py
```

On Linux, use `.venv/bin/python` instead. The offline codec tests require only the standard library; Pillow and numpy are needed by the inspector.

## Extract an official package you obtained separately

Get the archive from the manufacturer link in [recovery.md](recovery.md), keep it separately, and check its size and SHA256. Do not run the updater merely to extract its files.

With the virtual environment active, or using its interpreter explicitly:

```powershell
Get-FileHash -Algorithm SHA256 .\input\L99-reset.zip
python tools/extract_l99_reset_assets.py input/L99-reset.zip extracted
python tools/inspect_l99_ui.py extracted/UartTFT-II_Flash.bin inspection
```

The extractor locates a container of exactly the expected size, verifies its SHA256, then extracts three files at recorded offsets and independently verifies each hash. It does not guess how a different or newer version is laid out. An existing output file with different contents is not overwritten.

The inspector accepts only the stock SHA256 documented in the article. It is not intended to parse every modified image without adaptation. Outputs include `manifest.json`, `touch_zones.csv`, `overview.jpg`, images under `pages/` and `assets/`, and a `viewer_data.js` model. This public version does not include the separate HTML viewer: open images with a normal image viewer and inspect metadata in JSON/CSV.

Tables are located through header addresses and records are checked for integrity. Problematic descriptors appear in `decode_issues`. The input is unchanged, but the output directory is populated/updated. Use a new empty output directory. Do not enable Python `-O`: some checks in the original research parser use `assert`. Its intended input is the known hash-verified base, not an arbitrary untrusted file.

## What the protocol examples check

`protocol_reference.py` provides reference encoding for extended runtime and selected ISP formats. It only encodes/decodes; it is not a flashing sequence. The external-read command is labeled as an SDK candidate and was not tested on live L99 hardware in this investigation.

`runtime_codec.py` is a bounded example of short RAM frames for the energy block, with synthetic readings, a signature, and CRC. It does not import serial or send packets. Its addresses apply to the matching custom UI, not an arbitrary stock image.

## Building on the findings

For a custom UI, inspect a known base, start with one icon, preserve commands and touch geometry, build a separate file, and independently check the diff. For HA integration, begin with a local PC indicator responding to screen touches, then one explicitly assigned entity, followed by background operation and autostart.

This publication does not include an automatically buildable version of our HOME firmware package or Windows application. The tools reproduce **inspection of the factory image and packet formats**, not installation of every described feature with one command. This distinction keeps a research publication from being mistaken for a supported finished product.

Generated BIN files, extracted images, logs, and personal configuration remain local. `.gitignore` helps prevent accidental additions, but the actual file list still needs review before publication.

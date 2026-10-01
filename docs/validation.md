# Public package validation, 2026-10-01

[Contents](../README.md) · [Русская версия](ru/validation.md)

Validation used the copies of the tools included in this publication. No keyboard was reflashed; no USB/COM commands or Home Assistant service calls were sent.

| Check | Result |
|---|---|
| `python -m unittest discover -s tests -v` | Seven tests passed: CRC vectors, a reference packet, RAM addresses, string lengths, corruption, and rejection of out-of-block requests |
| `python tools/protocol_reference.py` | Reference extended runtime packet, CRC16/CRC32, and length carry across 255 checked |
| `python tools/runtime_codec.py` | Seven synthetic write frames and a signature-read frame generated offline |
| Official reset ZIP extraction | Container and all three payload SHA256 values verified; expected sizes and hashes from recovery.md obtained |
| Extracted stock UI inspection | 30 pages, 385 display records, 187 touch records, 1138 descriptors across two banks, 811 unique decoded images |
| Unsupported/problematic descriptors | 26, explicitly retained in the report rather than counted as successfully decoded |
| Internal documentation links and Python syntax | Checked locally |
| Public files | Scanned for JWTs, private keys, authorization literals, private IPs, user paths, and actual personal entity IDs; no matches found |

Automated secret scanning complements explicit file selection; it is not a mathematical guarantee against every possible kind of personal data. The publication was assembled from an allowlist of texts and source files. Working configurations, conversations, HA snapshots, EXEs, BINs, and the original working-directory history were excluded.

These results validate offline inspection, not the safety of flashing every L99. Earlier hardware observations are described separately in the README and recovery.md.

The English-default documentation update preserves the Russian edition under `README.ru.md` and `docs/ru/`. It changes documentation only; tool source files are unchanged. Internal language links and technical identifiers are checked again before publication.

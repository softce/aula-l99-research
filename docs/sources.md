# Sources, acknowledgements, and evidence boundaries

[Contents](../README.md) · [Русская версия](ru/sources.md)

We started from existing research. This project does not claim to have discovered every L99 protocol and does not include a copied vendor SDK.

| Source | Contribution to this investigation |
|---|---|
| [gavindi/Aula_L99_Linux](https://github.com/gavindi/Aula_L99_Linux), [tools](https://github.com/gavindi/Aula_L99_Linux/tree/main/tools) | HID/serial research, traffic captures, and clock/CPU/GPU/weather data through keyboard HID; an initial protocol reference |
| [HuldaLloyd/lt7689](https://github.com/HuldaLloyd/lt7689/tree/a043cfb7214321cfb4165653fcb74822ec1754eb), [Basic_touch in bsp.c](https://github.com/HuldaLloyd/lt7689/blob/a043cfb7214321cfb4165653fcb74822ec1754eb/User/bsp.c#L12327) | Comparison of UI structures, runtime behavior, and touch codes; not proof of an LT7689 CPU in L99 |
| [Salamor/aula-l99-open-widgets](https://github.com/Salamor/aula-l99-open-widgets), [discussion #2](https://github.com/Salamor/aula-l99-open-widgets/issues/2) | Independent open-widget investigation and screen-image discussions |
| [AULA L99 instructions](https://aulastar.com/faq/818.html), [official reset package](https://www.aulastar.com/uploads/soft/20240621/L99%20reset%20firmware%202026.5.25.zip) | Provenance of the inspected binaries; exact hashes are in recovery.md |
| [LT168 datasheet V2.2](https://www.levetop.cn/uploadfiles/2025/%E8%A7%84%E6%A0%BC%E4%B9%A6/LT168_DS_V22_Eng_User-S.pdf) | Family memory map, pp. 64–65 and 81–83; not a board-specific L99 map |
| [UI Editor-II V3.20](https://www.levetop.cn/uploadfiles/2025/%E5%BA%94%E7%94%A8%E6%89%8B%E5%86%8C/UI_Editor-II_CH_V3.2-250912.pdf) | UI model and hardware-recovery research directions; boot sections 16.1.3.1–16.1.3.2 concern demonstration boards |
| [L99 teardown by 大胖鸟, Weistang](https://www.weistang.com/thread-125204-1-1.html), [teardown page](https://www.weistang.com/portal.php?mod=view&aid=25988&page=4&forcemobile=1) | The author reports HFD168BDP, HFD80CP100, and Goodix GT911; a different specimen, not an inspection of our board |
| [fpb/ajazz-ak820-pro](https://github.com/fpb/ajazz-ak820-pro/tree/180d731357decae00c36bf8d94ad17bf6e43e392), [QMK configuration](https://github.com/fpb/qmk_firmware/blob/cb2d34c07bd131d71fc5886bef1e4cea7f4d9ca9/keyboards/a_jazz/ak820pro/keyboard.json) | Related HFD80CP100/SN32F299 work; the Ajazz matrix, firmware, and recovery procedure cannot be directly transferred to L99 |
| [SonixFlasherC](https://github.com/SonixQMK/SonixFlasherC/blob/b41694cdff5b6d935b51067f24975aabeebe344c/sonixflasher.c) | Comparison of checksum arithmetic and the SN32F290 update protocol; not run against L99 |
| [mos9527/evbunpack](https://github.com/mos9527/evbunpack), [innoextract](https://github.com/dscharrer/innoextract) | Initial static container inspection without executing the updater |

## How to interpret the claims

- **On hardware:** the user observed the new UI, ordinary keyboard input, HA control, and updating values. This is not a full flash readback or a test of every revision.
- **Static analysis:** addresses and structures come from a particular SHA256-identified file. They do not automatically apply to an identically named file from another version.
- **Emulation:** selected machine-code functions were executed and buffers compared. This is not a complete MCU with real peripherals.
- **Hypothesis:** unresolved questions about markings, additional projects, and emergency recovery are explicitly identified.

Many early local notes preceded later checks. This publication reflects the corrected picture: the resource image was located at the manufacturer, keyboard resource 4000 matters more than the initially found HEX, and a limited working UI does not mean the entire firmware is open.

## Licensing and personal data

This repository publishes a newly prepared write-up and our offline tools under GPL-2.0-only. It does not claim rights to AULA/Levetop firmware, SDKs, or artwork. Those files are not included; the tools process a copy obtained separately by the user.

Examples use fictional entity IDs and synthetic readings. Secrets, home-network addresses, configurations, absolute user paths, conversation history, and USB/HA captures are not published. The working directory was not imported as Git history.

# Factory recovery and lessons from the experiments

[Contents](../README.md) · [Русская версия](ru/recovery.md)

## First, distinguish three components

1. Main keyboard firmware: a separate keyboard reset EXE.
2. Screen MCU executable code: `HFD_Code_V2.2.bin` / `HFD_Code_V2.3.bin`.
3. Screen resources/pages: `UartTFT-II_Flash.bin`.

A complete reset package is not a complete backup of a particular board. It does not prove that the bootloader will remain reachable after every possible failure. Our successful UI experiments preserved executable logic; universal hardware recovery remains unverified.

## The recorded official package

The [AULA L99 download listing](https://www.aulastar.com/search.html?typeid=28&method=1&channelid=4&type=sonself&keywords=L99) linked to [L99 reset firmware 2026.5.25.zip](https://www.aulastar.com/uploads/soft/20240621/L99%20reset%20firmware%202026.5.25.zip). We downloaded it from the manufacturer and confirmed it matched a previously found mirror. The URL directory date is not the release date.

| File | Bytes | SHA256 |
|---|---:|---|
| Reset ZIP | 45080624 | `e854bebb87a592eaa8553dacff103a7ae62007318592cba2159685fbdb3615e3` |
| Screen reset EXE | 194946048 | `8d52849afefeadf3a5d28a5e226f2c7a372a9376e1286f35c286d9b820d1ae84` |
| Keyboard reset EXE | 2213280 | `0a946a5d41a872f32e3f3cbdd0d73f9dd7058ea17d3f2a89b2b1bf5c3ed6b217` |
| HFD_Code_V2.2.bin | 305800 | `432e358cac96fb930ab680ada6f953c9005027c58b31b7ee3bb6bc7868ef35cf` |
| HFD_Code_V2.3.bin | 313652 | `a76806ada9648d2672bbebead8a9bb396c0bc6f3a0a071e22e99001ac3359d03` |
| UartTFT-II_Flash.bin | 127599044 | `4cb3fa5c77eea973a2b62ca61873f071692694f4c9a1832507fe2c8c9ba582b4` |

These identify the bytes historically inspected. If the website replaces an archive, different contents under the same name are not automatically compatible. The public extractor stops if the screen EXE's SHA differs.

## What happened on our specimen

The [AULA instructions](https://aulastar.com/faq/818.html) describe Fn + X → 0 → 6. That attempt did not produce the expected result on our specimen. The user reported that, with USB connected, **Fn+Space for approximately five seconds** allowed updating to start. This is an observation of one configuration, not a universal replacement for the official procedure across revisions.

After an early screen experiment, the keyboard typed incorrect characters. Running the stock `L99 keyboard reset firmware … .exe` restored normal input; version 1.06 was displayed. The modified orange screen icon remained. In that case, resetting the keyboard part did not undo the screen-resource modification.

**The cause of the incorrect characters was not established.** A reset changes several conditions; it does not prove that changing an image damaged the MCU. Later, the user confirmed that the redesigned numpad and ordinary keyboard input worked correctly.

Separate UI packages used `HFD_ISP_TOOL_V1.31.exe` with a resource image named `UartTFT-II_Flash.bin`, without HFD_Code or keyboard MCU files. The updater still transfers the entire resource image. Supplying only UI data does not guarantee recovery after power loss.

Before manual updates, AULA Driver and our bridge were closed, the COM port was released, and a known working base was retained. The updater was allowed to finish normally, followed by reconnection and checks of ordinary typing, the screen, and the panel. This describes the procedure used; this repository does not provide an automatic flasher. A different hardware revision first needs its own verified recovery plan.

## Failed experiments worth learning from

### A good preview does not prove a good hardware result

An early “digital clock + energy” version produced stripes and corrupted graphics on the device. A photograph confirmed the symptom, but a single hardware cause was not established. That version is not presented as working. An LT encoder is not proven correct merely because its own decoder accepts the output.

### A numeric field's color is not necessarily RGB888

The inspected fields required correct RGB565 interpretation. Using familiar RGB888 values produced the wrong appearance. The final clock uses verified values: black `0x0000`, white `0xFFFF`.

### Stock-font Cyrillic looked poor

Long Russian labels in an unsuitable format appeared widely spaced. Static labels became bitmaps, while changing numbers stayed ASCII. This solves the design problem; it is not a universal Unicode patch.

### Values can remain after the sender stops

Earlier CPU/GPU readings of 100% did not establish actual PC load. Subsequent checks followed the whole chain: source → sender → RAM readback → visible value. HA clock values first appeared after leaving and reopening the page; the user then confirmed regular updates without switching pages. The cause of the initial blank display remained unknown, and no extra reflash was performed just to address it.

## What is still needed for dependable recovery

- Exact MCU markings and revisions of both boards.
- Verified service contacts and an entry method when the MCU application does not run.
- Read-back and validated regions of the actual device, including device-specific data.
- Recovery testing on a separate specimen rather than assuming a similar Ajazz procedure applies.

LT168-family documentation includes hardware boot/debug signals; SN32 has its own BOOT mechanism. Do not transfer pinouts to an HFD-marked device without evidence or short pads based on another board's photograph. These are research directions, not a completed L99 recovery solution.

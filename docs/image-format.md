# The screen image and how UI modification works

[Contents](../README.md) · [Русская версия](ru/image-format.md)

## Which file did we modify?

`UartTFT-II_Flash.bin`, extracted from the 2026.5.25 reset package:

```text
size:   127599044 bytes (0x079B01C4)
SHA256: 4cb3fa5c77eea973a2b62ca61873f071692694f4c9a1832507fe2c8c9ba582b4
```

This is a vendor-supplied resource image, not a backup read from a particular board and not a complete raw NAND dump with OOB/ECC. `HFD_Code_V2.2.bin` and `HFD_Code_V2.3.bin` contain separate screen-MCU executable code. Our confirmed design changes affect the resource file.

Every address in this chapter is a **file offset**. Page and icon indices are zero-based.

| Offset | Content |
|---|---|
| `0x00000000` | First UI project; size `0x00A355EC`, also stored as LE32 at `+0x174` |
| `0x00000180` | `0x11C50`-byte block including pinyin data; not fully interpreted |
| `0x00011DD0` | Initial variable values; later experiments used this area for the energy block |
| `0x00021DD0` | 30 page records, 12 bytes each |
| `0x00021F38` | Start of widget records |
| `0x000251A5` | Table of four fonts |
| `0x002F4349` | Table of three sound resources |
| `0x0034551C` | Three built-in animations: 76, 8, and 50 frames |
| `0x005C008E` | 30 background descriptors |
| `0x00622A84` | Two banks of 569 bitmap descriptors |
| `0x04000000`, `0x04060000`, `0x040C0000`, `0x041E0000` | Separate 320×480 images |
| `0x04240000` | 171-frame startup animation; ends at `0x05B0D07C` |
| `0x05B10000`, `0x065455EC`, `0x06F7ABD8` | Three more UI projects, `0x00A355EC` bytes each |

The last three projects are identical to each other but differ from the first. Their purpose is not fully understood; they cannot be assumed to be guaranteed recovery copies. Our modifications preserved them.

The offline parser reads 30 pages, 385 display records, and 187 touch records, and decodes 811 unique images by address/format/dimensions. It also reports 26 problematic unique descriptors rather than hiding them. Static reconstruction does not emulate the MCU, clock, or every blending mode.

## Pages and buttons are data records

A page record uses little-endian `struct '<IHIH'`:

```text
u32 display_offset
u16 display_length
u32 touch_offset
u16 touch_length
```

A display record is `u16 type, u16 parameter_address, u8 length_flags, payload`. A touch record is `u16 type_flags, u8 length_flags, payload`. In both, payload length is `length_flags & 0x7F`.

A basic touch button has base type `type_flags & 0x3FFF == 1` and eight LE16 payload fields:

```text
x1, y1, x2, y2,
return_value,
unpressed_icon, pressed_icon,
goto_page
```

`0xFFFF` indicates no ordinary icon/transition in the corresponding field. Do not arbitrarily clear the upper flags: their complete semantics have not been recovered. HOME reused tested types and codes.

Stock-menu example: the record at `0x22077` has type `0x8001`, return code `0x0020`, and a transition to page 21, Mini Numpad. In the updated menu, the LE16 field at `0x22088` changed **21→15** to open HOME in place of About. Coordinates and the return code were preserved. Page 21 was also converted to HOME in the build chain we used.

Each modification has two independent aspects: where to touch and what to draw. Moving artwork without moving the touch rectangle leaves the old hit area. Changing a transition does not create a new keyboard command.

## Bitmap format

A descriptor is 12 bytes:

```text
u32 payload_offset
u16 width, height
u24 payload_size
u8  format
```

The size occupies **24 bits**, not 16. Formats 0/1 were decoded as RGB565 LE; format 2 as ARGB4444 LE. The transparency/key-color differences between 0/1 are not fully reproduced. Format 3 is a proprietary `LT` container, not PNG/JPEG/GIF.

```text
LT container:
  'LT', u16 width, u16 height, u8 block_count, u8 format,
  u32 internal_size
  block_count × (u24 content_length, u8 mode, 256 × RGB565 palette)
  followed by all content blocks in sequence
```

Mode 0 uses one palette index per pixel. Mode 1 uses `count_minus_one, palette_index` pairs; RLE continues across row boundaries. All block metadata precedes all content blocks. Blocks can have different palettes and modes.

The separate images at higher offsets have an 11-byte header: `u32 size, u16 width, u16 height, u8 field, u16 CRC16`, followed by RGB565. CRC16/MODBUS matched for all four inspected images.

## Russian labels, transparency, and the clock

The active project's Chinese artwork bank was replaced with Russian labels. This is a bitmap change; stock font tables were not rewritten. The startup animation and three additional projects were not localized. The precise claim is Russian artwork in the active UI, not universal Cyrillic support.

Dark rectangles around main-menu icons and the bottom control strip were removed by changing pixels/alpha in the relevant resources. Alpha changes do not change the Bluetooth protocol or connection mode.

Clock Energy V3 preserves the native analog clock face (icon 550, 220×230) and hand parameters. Coordinates and weekday labels changed, and four native text widgets were added. Their numbers use the same RAM block as the energy page.

| V3 parameter | Value |
|---|---|
| Page | 26 |
| Working MENU_RU_V2 base SHA256 | `59d606f1602b920c83d03d48043c858e27ba6f72dec561ed923d5d0a1a3fadaf` |
| V3 output SHA256 | `6ddca1f9e9e0c3f37f3eda117d7e833b30c7a0e0ab884d902b5686231c5fc6e3` |
| Reused bitmap IDs | 534–544 in both banks |
| Resource pools | `0x901FA8`, 28000 bytes; `0xA29ADA`, 24000 bytes |
| Allocated data | 50683 bytes, including a 251-byte display block |
| Allowed changes relative to MENU_RU_V2 | 22 descriptors, 2 pools, 6 bytes of the page pointer/length |

These pools are reclaimed weekday resources, not arbitrarily chosen “empty flash.” References from other pages and allocation overlap were checked. V3's new artwork uses raw ARGB4444, without a new LT-compressed background. The entire HOME build chain contains more changes than these 25 ranges: this table describes only MENU_RU_V2→Clock V3.

## How to validate a patch

1. Bind the builder to an exact base SHA-256. Stop on a mismatch.
2. Parse all pages, resource references, and boundaries; do not identify images by an accidental signature match.
3. Keep an original copy. Build a new file rather than overwriting the base.
4. Define allowed byte ranges and independently prove that every other byte is unchanged.
5. Check sizes, references, overlap, exact consumption of display/touch records, and both language banks.
6. Decode the output for a preview and verify that reversing the patch restores the original SHA-256.
7. Treat hardware testing as a separate stage: an attractive preview does not prove correct rendering on the device.

A resource patch limits the logic being changed, but **the official updater transfers the entire resource image**. Changing two pixels does not mean it writes only two pixels to the device. The published inspector is a reader, not a universal packer or flasher.

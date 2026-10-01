# Architecture: what each component does

[Contents](../README.md) · [Русская версия](ru/architecture.md)

## Two USB devices and an inter-controller link

| Component | Observed ID | Role in our implementation |
|---|---|---|
| Main keyboard | `0C45:800A` | Ordinary input; translates touchscreen commands into keys |
| Screen | `EEEF:268A` | USB Serial, UI, and runtime variables |

Windows assigns the COM-port number; do not hardcode someone else's `COM7`. The application searches for exactly one port with the screen's VID/PID. The description below combines observed behavior with handler analysis; we did not separately capture the physical inter-board UART with a logic analyzer.

A button has artwork, coordinates, a return code, and a page transition. Drawing a light bulb does not create a new hardware command. The stock screen MCU processes the touch, then the keyboard MCU maps a known code to an input event. Only the PC application gives that event the meaning “turn on a light.”

## One complete button cycle

1. A user touches a tile on the HOME page.
2. Its touch record contains a known screen code, such as `0x003B`.
3. Stock logic passes that code to the main keyboard.
4. The keyboard's table maps it to USB HID usage `0x59`: NumPad 1.
5. A Windows hook recognizes scan code `0x4F` and the virtual-key variant for the current Num Lock state.
6. The hook suppresses key-down/key-up and queues an event for a worker. HTTP is not performed inside the keyboard callback.
7. The worker checks the mapping and HA state, then calls an allowed service.
8. The application's UI displays state read from HA. Holding a button should not repeat its action.

Steps 2–4 are supported by static analysis and limited emulation of the keyboard handler. The full path from touch to HA control was confirmed by the user on hardware. These are distinct kinds of evidence.

## Why 12 buttons when there are only 10 digits?

We use 1–9, 0, decimal, and minus. Twelve tiles do not require a new HID protocol.

| Panel slot | Screen code | HID usage | Windows scan code | VK with / without Num Lock |
|---:|---|---|---|---|
| 1 | `003B` | `59` | `4F` | `61 / 23` |
| 2 | `003C` | `5A` | `50` | `62 / 28` |
| 3 | `003D` | `5B` | `51` | `63 / 22` |
| 4 | `0038` | `5C` | `4B` | `64 / 25` |
| 5 | `0039` | `5D` | `4C` | `65 / 0C` |
| 6 | `003A` | `5E` | `4D` | `66 / 27` |
| 7 | `0034` | `5F` | `47` | `67 / 24` |
| 8 | `0035` | `60` | `48` | `68 / 26` |
| 9 | `0036` | `61` | `49` | `69 / 21` |
| 10 | `003F` | `62` | `52` | `60 / 2D` |
| 11 | `0040` | `63` | `53` | `6E / 2E` |
| 12 | `0033` | `56` | `4A` | `6D / 6D` |

All values in the table are hexadecimal. Screen codes, HID usages, scan codes, and VK values **are not interchangeable**. Separate E0 navigation keys and synthetic input pass through. Shift/Ctrl/Alt/Win combinations should not trigger actions. The top number row has different scan codes.

`WH_KEYBOARD_LL` does not identify the physical source device, so these keys are reserved on every numpad. Per-device handling needs a different solution: Raw Input distinguishes devices but does not, by itself, provide equivalent global suppression. This is not a one-checkbox fix.

## Home Assistant action semantics

A fictional mapping might be slot 1 → `switch.example_light` → toggle. `button.example_play` invokes `button.press`. These illustrate structure; they are not entities from an actual installation.

In the implemented bridge:

- `toggle` reads the current state and selects `switch.turn_on` or `switch.turn_off`;
- `on`/`off` set a state;
- `press` calls `button.press`;
- `pulse` only calls `switch.turn_on`: **HA or the target device must provide the short pulse and automatic turn-off**. The application does not add an off timer.

Unknown state should prevent an action. A failed HTTP request must not be automatically retried for a gate: the server may already have acted even if the response was lost. Events from a disabled session must not execute after reconnection. Relay state is not gate position.

## The return path: sensor values

Polling seven HA entities produces six numbers and one status string. A worker cycle takes the duration of the requests plus approximately five seconds of waiting; it is not guaranteed to run exactly every five seconds.

| Field | Source and validation |
|---|---|
| Current PV | Numeric state, unit `W` |
| Current grid power | Numeric state, `W`; negative values allowed |
| Battery charge | State, `%`, range 0–100 |
| Floor temperature | `climate.example_floor`, `attributes.current_temperature`; °C assumed |
| Daily PV | Sum of two `kWh` sources; do not add a component already included in the other source |
| Daily grid import | State, `kWh` |

`unknown`, `unavailable`, incorrect units, and nonnumeric values produce `--`. The original temperature formatter did not convert °F to °C: when adapting the bridge, explicitly match HA's units. The grid-power sign convention depends on the integration and is not defined by this project.

The RAM block and layout signature are documented in [protocol.md](protocol.md). Frequent numeric updates write RAM, not resource flash. The modified UI already contains the text widgets. This is not arbitrary live desktop or UI streaming to the display.

## What the background application needs

Our Windows application supports the tray, autostart, and entity mapping. Its token is stored separately using Windows DPAPI, not in exported JSON. Moving to another PC requires entering a token again; a DPAPI file is not a portable credential. Automatic interception should be enabled only after configuring and checking the panel.

The architecture does not require daily reflashing: action mappings can change on the PC. However, the keyboard's artwork and labels are static in this implementation and require a separate UI build to change. A screen tile's color does not confirm the actual HA state.

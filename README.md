# Yamper

A tiny 3D-printed AI voice robot powered by a Raspberry Pi Zero 2 W, with OLED eyes, a speaker, microphone, button control, and a portable PiSugar battery.

## Current version

This version targets a Raspberry Pi Zero 2 WH with a PiSugar 3 1200mAh battery.

## Target hardware

- Raspberry Pi Zero 2 WH
- PiSugar 3 1200mAh Raspberry Pi Zero Battery
- 2x 0.96 inch SSD1306 I2C OLED displays
- INMP441 I2S microphone module
- MAX98357A I2S amplifier
- 3525 4 ohm 3W cavity speaker
- 16 mm momentary illuminated metal pushbutton
- M3 x 8 self-tapping screws for the case
- 20 cm female-to-female Dupont wires
- microSD card, 32 GB or bigger

## Folder layout

```text
hardware/
  v6-zero-fixed/
    stl/       3D-print files
    source/    dimensions, source notes and preview files
    renders/   concept render
software/
  yamper/        early Python app skeleton
  systemd/     service file for autostart
docs/          wiring and build notes
```



Start by printing only:

```text
hardware/v6-zero-fixed/stl/robot_v6_zero_fixed_front_shell.stl
```

Then test-fit:

1. OLEDs
2. speaker
3. mic
4. button

Only print the full set after the front shell fits.

Recommended settings:

- Material: PETG for the main body
- Layer height: 0.20 mm
- Walls: 3 or 4
- Infill: 15 to 25 percent


## Status

This is not final product-ready yet.
Known things to verify:

- speaker thickness
- MAX98357A board size
- PiSugar button location
- OLED clone fit
- button rear depth

Robot V6 Zero fixed beta 2
=========================

This updated model is built around the parts you confirmed:
- Raspberry Pi Zero 2 WH
- PiSugar 3 1200mAh for Pi Zero (official docs list PCB size 65 x 30 mm)
- 2x 0.96 inch SSD1306 OLED boards using the 27.5 x 27.8 mm drawing
- 3525 cavity speaker 25 x 35 mm body, 4 ohm 3W variant
- INMP441 round mic, approx 14 mm diameter
- MAX98357A amp, using a typical small breakout estimate
- 16 mm momentary metal button
- M3 x 8 self tapping screws for case closure

Main fixes in this version:
- speaker grille made smaller and cleaner
- speaker pocket resized for the 25 x 35 mm speaker
- OLED ledges updated from the exact board drawing
- mic cradle tightened for 14 mm board
- amp pocket and clip added
- stronger 3.0 mm walls and stronger corner bosses
- bigger side utility opening for Zero / PiSugar access

Files:
- robot_v6_zero_fixed_front_shell.stl
- robot_v6_zero_fixed_back_cover.stl
- robot_v6_zero_fixed_oled_retainer_print_2x.stl
- robot_v6_zero_fixed_3525_speaker_retainer.stl
- robot_v6_zero_fixed_inmp441_retainer.stl
- robot_v6_zero_fixed_max98357_clip.stl
- robot_v6_zero_fixed_button_washer_optional.stl
- robot_v6_zero_fixed_dimensions.json
- robot_v6_zero_fixed_assembly_preview_not_for_printing.obj

Important assumptions:
- The speaker thickness was not listed in the product page, so a 5 mm body and a 7 mm deep pocket were used.
- The amp board size was not listed, so a typical MAX98357A breakout estimate was used.
- Your cart indicates the 16 mm button variant, so the top hole is 16.4 mm.

Recommended first print workflow:
1. Print the front shell only.
2. Dry fit the OLEDs, speaker and button.
3. If the speaker body is thicker than expected, increase the speaker retainer spacing with a small foam pad.
4. Only after that, print the final clean set.

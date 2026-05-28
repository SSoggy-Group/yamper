# Yamper Hardware Setup

## OLED Screens (I2C Addresses)
Yamper uses two 0.96" SSD1306 OLED screens on the same I2C bus. To prevent address conflicts, they MUST have different I2C addresses (`0x3C` and `0x3D`).

### Modifying the Address Jumper
Most generic SSD1306 OLEDs arrive with a default address of `0x3C` (sometimes labeled as `0x78`). 
To change one screen to `0x3D` (labeled as `0x7A`), you must:
1. Look at the back of one of the OLED modules.
2. Locate the surface-mount resistor next to the address labels (0x78 / 0x7A).
3. Using a soldering iron, carefully desolder and move the resistor from the `0x78` pads to the `0x7A` pads.

*If you are unable to modify the address resistor on the back of your screen, you must use an I2C multiplexer (like the TCA9548A) to talk to both screens independently.*

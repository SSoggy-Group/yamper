# Wiring plan

This is the first wiring plan for Mimo V6 Zero.

## OLED eyes

Both OLED displays use I2C.

| OLED pin | Raspberry Pi pin |
|---|---|
| VCC | 3.3V or 5V |
| GND | GND |
| SCL | GPIO 3 / SCL |
| SDA | GPIO 2 / SDA |

Important: many cheap OLEDs use the same I2C address. If both screens show the same thing, use an I2C multiplexer or buy OLEDs with changeable address. For the first version, mirrored eyes are acceptable.

## INMP441 microphone

| INMP441 pin | Raspberry Pi pin |
|---|---|
| VDD | 3.3V |
| GND | GND |
| SCK | I2S BCLK |
| WS | I2S LRCLK |
| SD | I2S data input |
| L/R | GND |

## MAX98357A amplifier

| MAX98357A pin | Raspberry Pi pin |
|---|---|
| VIN / VCC | 5V or 3.3V, depending on module |
| GND | GND |
| BCLK | I2S BCLK |
| LRC | I2S LRCLK |
| DIN | I2S data output |
| SD | optional GPIO for amp enable |
| Speaker + / - | speaker red / black |

## Button

The button has 2 parts:

1. the switch contacts
2. the LED ring

Use the switch as a normal GPIO input with pull-up or pull-down.

The LED ring depends on the exact voltage version. If it is the 3 to 6 V version, it can be powered from 3.3V or 5V with care. If it is the 12 to 24 V version, do not connect it directly.

## First power-on safety

Before plugging everything in:

- check 5V and 3.3V lines
- check GND is common
- do not short speaker wires
- do not power the LED ring if you are unsure about its voltage

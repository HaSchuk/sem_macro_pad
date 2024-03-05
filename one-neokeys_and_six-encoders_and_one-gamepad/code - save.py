# SPDX-FileCopyrightText: 2021 Phillip Burgess for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
A macro/hotkey program for Adafruit MACROPAD. Macro setups are stored in the
/macros folder (configurable below), load up just the ones you're likely to
use. Plug into computer's USB port, use dial to select an application macro
set, press MACROPAD keys to send key sequences and other USB protocols.
"""

# pylint: disable=import-error, unused-import, too-few-public-methods

import os
import sys
import time
import displayio
import terminalio
import board
import math
import sparkfun_qwiicjoystick
from adafruit_display_shapes.rect import Rect
from adafruit_display_text import label
from adafruit_macropad import MacroPad
from micropython import const
# from rainbowio import colorwheel
from adafruit_neokey.neokey1x4 import NeoKey1x4
from adafruit_seesaw import seesaw, rotaryio, digitalio, neopixel
from adafruit_seesaw.seesaw import Seesaw
from adafruit_hid.keycode import Keycode
from adafruit_hid.mouse import Mouse

# Initialisierung Macropad

macropad = MacroPad()

# use default I2C bus
i2c_bus = board.I2C()

# Create a NeoKey object
neokey = NeoKey1x4(i2c_bus, addr=0x30)

# Create a Joystick object
gamepad = sparkfun_qwiicjoystick.Sparkfun_QwiicJoystick(i2c_bus)

last_x = 0
last_y = 0

speed_H = "zero"
speed_V = "zero"

start_x = 1023 - gamepad.horizontal
start_y = 1023 - gamepad.vertical
ma_joy_pos = [-600, -340, -170, -10, 10, 170, 340]
ma_mo_move = [-100, -50, -10, 0, 10, 50, 100]
ma_mo_xspeed = ['SL 3', 'SL 2', 'SL 1', 'SLR 0', 'SR 1', 'SR 2', 'SR 3']
ma_mo_yspeed = ['SD 3', 'SD 2', 'SD 1', 'SDU 0', 'SU 1', 'SU 2', 'SU 3']
mo_xspeed = None
mo_yspeed = None

# Create a Seesaw object (encoder 1)
qt_enc1 = seesaw.Seesaw(i2c_bus, addr=0x36)

qt_enc1.pin_mode(24, qt_enc1.INPUT_PULLUP)
button1 = digitalio.DigitalIO(qt_enc1, 24)
button_held1 = False

encoder1 = rotaryio.IncrementalEncoder(qt_enc1)
last_position1 = 0

pixel1 = neopixel.NeoPixel(qt_enc1, 6, 1)
pixel1.brightness = 0.2
pixel1.fill(0xFF0000)

while True:
    # gamepad - stick auslesen
    x = 1023 - gamepad.horizontal
    y = 1023 - gamepad.vertical
    x_rel_pos = x - start_x
    y_rel_pos = y - start_y
    y_rel_pos = -y_rel_pos

    for i_dx in range(len(ma_joy_pos)):

        if x_rel_pos >= ma_joy_pos[i_dx]:
            i_x = i_dx

    for i_dy in range(len(ma_joy_pos)):

        if y_rel_pos >= ma_joy_pos[i_dy]:
            i_y = i_dy

    mo_xspeed = ma_mo_move[i_x]  # ma_mo_xspeed[i_x]
    mo_yspeed = ma_mo_move[i_y]  # ma_mo_yspeed[i_y]

    if x_rel_pos == 0:
        speed_H = "zero"

    elif x_rel_pos < 170 and x_rel_pos > 0:
        speed_H = "R low"

    elif x_rel_pos < 340 and x_rel_pos >= 170:
        speed_H = "R middle"

    elif x_rel_pos >= 340:
        speed_H = "R high"

    elif x_rel_pos > -170 and x_rel_pos < 0:
        speed_H = "L low"

    elif x_rel_pos > -340 and x_rel_pos <= -170:
        speed_H = "L middle"

    elif x_rel_pos <= -340:
        speed_H = "L high"

    if y_rel_pos == 0:
        speed_V = "zero"

    elif y_rel_pos < 170 and y_rel_pos > 0:
        speed_V = "U low"

    elif y_rel_pos < 340 and y_rel_pos >= 170:
        speed_V = "U middle"

    elif y_rel_pos >= 340:
        speed_V = "U high"

    elif y_rel_pos > -170 and y_rel_pos < 0:
        speed_V = "D low"

    elif y_rel_pos > -340 and y_rel_pos <= -170:
        speed_V = "D middle"

    elif y_rel_pos <= -340:
        speed_V = "D high"

    if (abs(x_rel_pos) > 1) or (abs(y_rel_pos) > 1):

        if x > start_x and y > start_y:
            print("x R: ", x_rel_pos, "Y U: ", y_rel_pos, speed_H, " ", speed_V)
            print("MOS: ", mo_xspeed, mo_yspeed)

        elif x < start_x and y > start_y:
            print("x L: ", x_rel_pos, "Y U: ", y_rel_pos, speed_H, " ", speed_V)
            print("MOS: ", mo_xspeed, mo_yspeed)

        elif x > start_x and y == start_y:
            print("x R: ", x_rel_pos, "Y C: ", y_rel_pos, speed_H, " ", speed_V)
            print("MOS: ", mo_xspeed, mo_yspeed)

        elif x < start_x and y == start_y:
            print("x L: ", x_rel_pos, "Y C: ", y_rel_pos, speed_H, " ", speed_V)
            print("MOS: ", mo_xspeed, mo_yspeed)

        elif x < start_x and y < start_y:
            print("x L: ", x_rel_pos, "Y D: ", y_rel_pos, speed_H, " ", speed_V)
            print("MOS: ", mo_xspeed, mo_yspeed)

        elif x > start_x and y < start_y:
            print("x R: ", x_rel_pos, "Y D: ", y_rel_pos, speed_H, " ", speed_V)
            print("MOS: ", mo_xspeed, mo_yspeed)
        elif x == start_x and y < start_y:
            print("x C: ", x_rel_pos, "Y D: ", y_rel_pos, speed_H, " ", speed_V)
            print("MOS: ", mo_xspeed, mo_yspeed)
        elif x == start_x and y > start_y:
            print("x C: ", x_rel_pos, "Y U: ", y_rel_pos, speed_H, " ", speed_V)
            print("MOS: ", mo_xspeed, mo_yspeed)
        else:
            print("Joystick centered", x_rel_pos, y_rel_pos, speed_H, " ", speed_V)
            print("MOS: ", mo_xspeed, mo_yspeed)
        last_x = x
        last_y = y

        macropad.mouse.click(macropad.Mouse.MIDDLE_BUTTON)
        macropad.mouse.move(x=mo_xspeed)
        macropad.mouse.move(y=(-1*mo_yspeed))

    # gamepad - button auslesen
    button = gamepad.button

    if button == 0:
        print("Button Joy pressed")

    # Neokey 1x4 auslesen
    if neokey[0]:
        print("Button A")
        neokey.pixels[0] = 0xFF0000
    else:
        neokey.pixels[0] = 0x0

    if neokey[1]:
        print("Button B")
        neokey.pixels[1] = 0xFFFF00
    else:
        neokey.pixels[1] = 0x0

    if neokey[2]:
        print("Button C")
        neokey.pixels[2] = 0x00FF00
    else:
        neokey.pixels[2] = 0x0

    if neokey[3]:
        print("Button D")
        neokey.pixels[3] = 0x00FFFF
    else:
        neokey.pixels[3] = 0x0

    # Encoder 1 auslesen
    position1 = -encoder1.position

    if position1 != last_position1:
        enc1_move = position1 - last_position1
        print("Position 1: {}".format(enc1_move))

        if enc1_move == 1:
            macropad.keyboard.press(Keycode.KEYPAD_PLUS)
            macropad.keyboard.release(Keycode.KEYPAD_PLUS)

        elif enc1_move == -1:
            macropad.keyboard.press(Keycode.KEYPAD_MINUS)
            macropad.keyboard.release(Keycode.KEYPAD_MINUS)

        last_position1 = position1

    if not button1.value and not button_held1:
        button_held1 = True
        pixel1.brightness = 0.5
        print("Button 1 pressed")

    if button1.value and button_held1:
        button_held1 = False
        pixel1.brightness = 0.2
        print("Button 1 released")

    time.sleep(0.01)


# CONFIGURABLES ------------------------

MACRO_FOLDER = '/macros'


# CLASSES AND FUNCTIONS ----------------

class App:
    """ Class representing a host-side application, for which we have a set
        of macro sequences. Project code was originally more complex and
        this was helpful, but maybe it's excessive now?"""
    def __init__(self, appdata):
        self.name = appdata['name']
        self.macros = appdata['macros']

    def switch(self):
        """ Activate application settings; update OLED labels and LED
            colors. """
        group[13].text = self.name   # Application name
        for i in range(12):
            if i < len(self.macros):  # Key in use, set label + LED color
                macropad.pixels[i] = self.macros[i][0]
                group[i].text = self.macros[i][1]
            else:  # Key not in use, no label or LED
                macropad.pixels[i] = 0
                group[i].text = ''
        macropad.keyboard.release_all()
        macropad.consumer_control.release()
        macropad.mouse.release_all()
        macropad.stop_tone()
        macropad.pixels.show()
        macropad.display.refresh()


# INITIALIZATION -----------------------

macropad = MacroPad()
macropad.display.auto_refresh = False
macropad.pixels.auto_write = False

# Set up displayio group with all the labels
group = displayio.Group()
for key_index in range(12):
    x = key_index % 3
    y = key_index // 3
    group.append(label.Label(terminalio.FONT, text='', color=0xFFFFFF,
                             anchored_position=((macropad.display.width - 1) * x / 2,
                                                macropad.display.height - 1 -
                                                (3 - y) * 12),
                             anchor_point=(x / 2, 1.0)))
group.append(Rect(0, 0, macropad.display.width, 12, fill=0xFFFFFF))
group.append(label.Label(terminalio.FONT, text='', color=0x000000,
                         anchored_position=(macropad.display.width//2, -2),
                         anchor_point=(0.5, 0.0)))
macropad.display.root_group = group

# Load all the macro key setups from .py files in MACRO_FOLDER
apps = []
files = os.listdir(MACRO_FOLDER)
files.sort()
for filename in files:
    if filename.endswith('.py') and not filename.startswith('._'):
        try:
            module = __import__(MACRO_FOLDER + '/' + filename[:-3])
            apps.append(App(module.app))
        except (SyntaxError, ImportError, AttributeError, KeyError, NameError,
                IndexError, TypeError) as err:
            print("ERROR in", filename)
            import traceback
            traceback.print_exception(err, err, err.__traceback__)

if not apps:
    group[13].text = 'NO MACRO FILES FOUND'
    macropad.display.refresh()
    while True:
        pass

last_position = None
last_encoder_switch = macropad.encoder_switch_debounced.pressed
app_index = 0
apps[app_index].switch()


# MAIN LOOP ----------------------------

while True:
    # Read encoder position. If it's changed, switch apps.
    position = macropad.encoder
    if position != last_position:
        app_index = position % len(apps)
        apps[app_index].switch()
        last_position = position

    # Handle encoder button. If state has changed, and if there's a
    # corresponding macro, set up variables to act on this just like
    # the keypad keys, as if it were a 13th key/macro.
    macropad.encoder_switch_debounced.update()
    encoder_switch = macropad.encoder_switch_debounced.pressed
    if encoder_switch != last_encoder_switch:
        last_encoder_switch = encoder_switch
        if len(apps[app_index].macros) < 13:
            continue    # No 13th macro, just resume main loop
        key_number = 12  # else process below as 13th macro
        pressed = encoder_switch
    else:
        event = macropad.keys.events.get()
        if not event or event.key_number >= len(apps[app_index].macros):
            continue  # No key events, or no corresponding macro, resume loop
        key_number = event.key_number
        pressed = event.pressed

    # If code reaches here, a key or the encoder button WAS pressed/released
    # and there IS a corresponding macro available for it...other situations
    # are avoided by 'continue' statements above which resume the loop.

    sequence = apps[app_index].macros[key_number][2]
    if pressed:
        # 'sequence' is an arbitrary-length list, each item is one of:
        # Positive integer (e.g. Keycode.KEYPAD_MINUS): key pressed
        # Negative integer: (absolute value) key released
        # Float (e.g. 0.25): delay in seconds
        # String (e.g. "Foo"): corresponding keys pressed & released
        # List []: one or more Consumer Control codes (can also do float delay)
        # Dict {}: mouse buttons/motion (might extend in future)
        if key_number < 12:  # No pixel for encoder button
            macropad.pixels[key_number] = 0xFFFFFF
            macropad.pixels.show()
        for item in sequence:
            if isinstance(item, int):
                if item >= 0:
                    macropad.keyboard.press(item)
                else:
                    macropad.keyboard.release(-item)
            elif isinstance(item, float):
                time.sleep(item)
            elif isinstance(item, str):
                macropad.keyboard_layout.write(item)
            elif isinstance(item, list):
                for code in item:
                    if isinstance(code, int):
                        macropad.consumer_control.release()
                        macropad.consumer_control.press(code)
                    if isinstance(code, float):
                        time.sleep(code)
            elif isinstance(item, dict):
                if 'buttons' in item:
                    if item['buttons'] >= 0:
                        macropad.mouse.press(item['buttons'])
                    else:
                        macropad.mouse.release(-item['buttons'])
                macropad.mouse.move(item['x'] if 'x' in item else 0,
                                    item['y'] if 'y' in item else 0,
                                    item['wheel'] if 'wheel' in item else 0)
                if 'tone' in item:
                    if item['tone'] > 0:
                        macropad.stop_tone()
                        macropad.start_tone(item['tone'])
                    else:
                        macropad.stop_tone()
                elif 'play' in item:
                    macropad.play_file(item['play'])
    else:
        # Release any still-pressed keys, consumer codes, mouse buttons
        # Keys and mouse buttons are individually released this way (rather
        # than release_all()) because pad supports multi-key rollover, e.g.
        # could have a meta key or right-mouse held down by one macro and
        # press/release keys/buttons with others. Navigate popups, etc.
        for item in sequence:
            if isinstance(item, int):
                if item >= 0:
                    macropad.keyboard.release(item)
            elif isinstance(item, dict):
                if 'buttons' in item:
                    if item['buttons'] >= 0:
                        macropad.mouse.release(item['buttons'])
                elif 'tone' in item:
                    macropad.stop_tone()
        macropad.consumer_control.release()
        if key_number < 12:  # No pixel for encoder button
            macropad.pixels[key_number] = apps[app_index].macros[key_number][0]
            macropad.pixels.show()

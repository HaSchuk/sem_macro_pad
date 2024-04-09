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
# import sys
import time
import displayio
import terminalio
import board
import math
import sparkfun_qwiicjoystick
from adafruit_display_shapes.rect import Rect
from adafruit_display_text import label
from adafruit_macropad import MacroPad
# from micropython import const
# from rainbowio import colorwheel
from adafruit_neokey.neokey1x4 import NeoKey1x4
from adafruit_seesaw import seesaw, rotaryio, digitalio, neopixel
# from adafruit_seesaw.seesaw import Seesaw
from adafruit_hid.keycode import Keycode   # Kann auch über die Macros geladen werden
from adafruit_hid.mouse import Mouse  # Kann auch über die Macros geladen werden

# Initialisierung Macropad >> Kommt noch in Zeile 246

macropad = MacroPad()

# use default I2C bus >> Initialisierung des I2C-Bus
i2c_bus = board.I2C()

# Create a NeoKey object >> Laden des Neokey1x4, Standardadresse 0x30
neokey = NeoKey1x4(i2c_bus, addr=0x30)
neokey.pixels[0] = 0x00FF00
neokey.pixels[1] = 0xFF0F00
neokey.pixels[2] = 0xCD1076
neokey.pixels[3] = 0x00008B

# Create a Joystick object >> Laden Sparkfun Joystick (JS),
# Standardadresse 0x20, aus der lib, nur ein JS möglich!!
joy = sparkfun_qwiicjoystick.Sparkfun_QwiicJoystick(i2c_bus)

# letze Positionen JS auf Null setzen
last_x = 0
last_y = 0

# Bestimmung des Nullpunkts x, y JS, Invertierung prüfen
start_x = 1023 - joy.horizontal
start_y = 1023 - joy.vertical

# Bestimmung des Nullpunkts x, y JS, zweites Update, beim Hardboot ofmals y falsch.
start_x = 1023 - joy.horizontal
start_y = 1023 - joy.vertical

# Mousespeed x/y auf Null setzen
mo_xspeed = None
mo_yspeed = None

# Anzahl Encoder
am_enc = 3

# Create a Seesaw object (encoder 1-3), weitere Encoder werden gesondert
# über 0x37, 0x38, ... 0x3B eingebunden
qt_enc1 = seesaw.Seesaw(i2c_bus, addr=0x36)
qt_enc2 = seesaw.Seesaw(i2c_bus, addr=0x38)
qt_enc3 = seesaw.Seesaw(i2c_bus, addr=0x39)

# Encoder1, Push-Button abfragen und auf nicht gedrückt setzen
# Encoder1, Drehrad abfragen, letzte relative Position auf 0 setzen
# RGB Encoder1 abfragen, LED auf Rot und Helligkeit 0.2 setzen
qt_enc1.pin_mode(24, qt_enc1.INPUT_PULLUP)
button1 = digitalio.DigitalIO(qt_enc1, 24)
button_held1 = False
encoder1 = rotaryio.IncrementalEncoder(qt_enc1)
last_position1 = 0
pixel1 = neopixel.NeoPixel(qt_enc1, 6, 1)
pixel1.brightness = 0.2
pixel1.fill(0xFF0000)

# Encoder2, Push-Button abfragen und auf nicht gedrückt setzen
# Encoder2, Drehrad abfragen, letzte relative Position auf 0 setzen
# RGB Encoder2 abfragen, LED auf Blau und Helligkeit 0.2 setzen
qt_enc2.pin_mode(24, qt_enc2.INPUT_PULLUP)
button2 = digitalio.DigitalIO(qt_enc2, 24)
button_held2 = False
encoder2 = rotaryio.IncrementalEncoder(qt_enc2)
last_position2 = 0
pixel2 = neopixel.NeoPixel(qt_enc2, 6, 1)
pixel2.brightness = 0.2
pixel2.fill(0x000020)

# Encoder3, Push-Button abfragen und auf nicht gedrückt setzen
# Encoder3, Drehrad abfragen, letzte relative Position auf 0 setzen
# RGB Encoder3 abfragen, LED auf Blau und Helligkeit 0.2 setzen
qt_enc3.pin_mode(24, qt_enc3.INPUT_PULLUP)
button3 = digitalio.DigitalIO(qt_enc3, 24)
button_held3 = False
encoder3 = rotaryio.IncrementalEncoder(qt_enc3)
last_position3 = 0
pixel3 = neopixel.NeoPixel(qt_enc3, 6, 1)
pixel3.brightness = 0.2
pixel3.fill(0xFFA500)

while True:
    # Joystick auslesen - aktuelle Position absolut, Invertierungen prüfen
    x = 1023 - joy.horizontal
    y = 1023 - joy.vertical

    # relative Position x und y bestimmen, aktuell y invertieren, Code für y prüfen
    x_rel_pos = x - start_x
    y_rel_pos = y - start_y
    y_rel_pos = -y_rel_pos

    # Bei Bewegung R Vorzeichen auf 1 setzen und Mousespeed R berechnen
    # (ln- und lin-Anteil)
    if x_rel_pos > 0:
        x_rel_pos_h = 1
        mo_xspeed_h = math.ceil(((10 * math.log(x_rel_pos)) + (x_rel_pos / 10)))
        mo_xspeed = mo_xspeed_h * x_rel_pos_h

    # Bei Bewegung L Vorzeichen auf -1 setzen und Mousespeed L berechnen
    # (ln- und lin-Anteil)
    elif x_rel_pos < 0:
        x_rel_pos_h = -1
        # da ln nur mit positiven Zahlen funktioniert, Absoluttwert berechnen
        x_rel_pos = abs(x_rel_pos)
        mo_xspeed_h = math.ceil(((10 * math.log(x_rel_pos)) + (x_rel_pos / 10)))
        mo_xspeed = mo_xspeed_h * x_rel_pos_h  # Wieder in neagtiven Wert umwandeln

    else:
        mo_xspeed = 0  # Keine Bewegung

    if y_rel_pos > 0:  # Bewegung U, Rest siehe Bewegung R
        y_rel_pos_h = 1
        mo_yspeed_h = math.ceil(((10 * math.log(y_rel_pos)) + (y_rel_pos / 10)))
        mo_yspeed = mo_yspeed_h * y_rel_pos_h

    elif y_rel_pos < 0:  # Bewegung D, Rest siehe Bewegung L
        y_rel_pos_h = -1
        y_rel_pos = abs(y_rel_pos)
        mo_yspeed_h = math.ceil(((10 * math.log(y_rel_pos)) + (y_rel_pos / 10)))
        mo_yspeed = mo_yspeed_h * y_rel_pos_h

    else:
        mo_yspeed = 0  # Keine Bewegung

    # Bestimmung, ob sich JS bewegt, Test, ob > 2, 3, ... sinnvoll wäre
    if (abs(x_rel_pos) > 1) or (abs(y_rel_pos) > 1):

        # ab hier bis Zeile 147 reine Printausgaben, darauf kann später verzeicht werden
        if x > start_x and y > start_y:
            print("x R: ", x_rel_pos, "Y U: ", y_rel_pos)
            print("MOS: ", mo_xspeed, mo_yspeed)
            print(start_x)

        elif x < start_x and y > start_y:
            print("x L: ", x_rel_pos, "Y U: ", y_rel_pos)
            print("MOS: ", mo_xspeed, mo_yspeed)
            print(start_x)

        elif x > start_x and y == start_y:
            print("x R: ", x_rel_pos, "Y C: ", y_rel_pos)
            print("MOS: ", mo_xspeed, mo_yspeed)
            print(start_x)

        elif x < start_x and y == start_y:
            print("x L: ", x_rel_pos, "Y C: ", y_rel_pos)
            print("MOS: ", mo_xspeed, mo_yspeed)
            print(start_x)

        elif x < start_x and y < start_y:
            print("x L: ", x_rel_pos, "Y D: ", y_rel_pos)
            print("MOS: ", mo_xspeed, mo_yspeed)
            print(start_x)

        elif x > start_x and y < start_y:
            print("x R: ", x_rel_pos, "Y D: ", y_rel_pos)
            print("MOS: ", mo_xspeed, mo_yspeed)
            print(start_x)

        elif x == start_x and y < start_y:
            print("x C: ", x_rel_pos, "Y D: ", y_rel_pos)
            print("MOS: ", mo_xspeed, mo_yspeed)
            print(start_x)

        elif x == start_x and y > start_y:
            print("x C: ", x_rel_pos, "Y U: ", y_rel_pos)
            print("MOS: ", mo_xspeed, mo_yspeed)
            print(start_x)

        else:
            print("Joystick centered", x_rel_pos, y_rel_pos)
            print("MOS: ", mo_xspeed, mo_yspeed)
            print(start_x)
        # Ende Printausgaben^^

        # Position letzte Abfrage festhalten // prüfen, ob weiter gebraucht wird
        last_x = x
        last_y = y

        # Bewegung Maus, durch Code ab Zeile 365 zukünftig abgearbeitet, nur Demo
        macropad.mouse.click(macropad.Mouse.MIDDLE_BUTTON)
        macropad.mouse.move(x=mo_xspeed)
        macropad.mouse.move(y=(-1*mo_yspeed))

    # JS - button auslesen >> gamepad-Variable anpassen, besser js1
    button = joy.button

    if button == 0:
        print("Button Joy pressed")

    # Neokey 1x4 auslesen - Demo zu Abfrage,
    # muss später weiter unten eingearbeitet werden
    # siehe auch originalen Fork two-neokeys....
    if neokey[0]:
        print("Button A")
        neokey.pixels[0] = 0xFF0000
    else:
        neokey.pixels[0] = 0x00FF00

    if neokey[1]:
        print("Button B")
        neokey.pixels[1] = 0xFFFF00
    else:
        neokey.pixels[1] = 0xFF0F00

    if neokey[2]:
        print("Button C")
        neokey.pixels[2] = 0xFFA500
    else:
        neokey.pixels[2] = 0xCD1076

    if neokey[3]:
        print("Button D")
        neokey.pixels[3] = 0x000FFF
    else:
        neokey.pixels[3] = 0x00008B

    # Encoder 1 auslesen
    position1 = -encoder1.position

    # relative Position auslesen. -1 = Bewegung links, +1 = Bewegung rechts
    if position1 != last_position1:
        enc1_move = position1 - last_position1
        # praktisches kleines Problem, wenn Encoder zu schnell bewegt wird,
        # dann 1, 2, 3 >> Auswirkung im Moment kein Drama
        print("Position 1: {}".format(enc1_move))

        if enc1_move >= 1:
            # Encoder1 R >> Ziffernblock + drücken und loslassen,
            # wird unten dann über Macroo gesteuert
            macropad.keyboard.press(Keycode.KEYPAD_PLUS)
            macropad.keyboard.release(Keycode.KEYPAD_PLUS)

        elif enc1_move <= -1:
            # Encoder1 L >> Ziffernblock - drücken und loslassen,
            # wird unten dann über Macro gesteuert
            macropad.keyboard.press(Keycode.KEYPAD_MINUS)
            macropad.keyboard.release(Keycode.KEYPAD_MINUS)

        last_position1 = position1

    # Demo Encoder1 Drücken Encerknopf und loslassen,
    # LED wird heller beim Drücken >> keine praktische Anwendung
    if not button1.value and not button_held1:
        button_held1 = True
        pixel1.brightness = 0.5
        print("Button 1 pressed")

    if button1.value and button_held1:
        button_held1 = False
        pixel1.brightness = 0.2
        print("Button 1 released")

    # Encoder 2 auslesen
    position2 = -encoder2.position

    # relative Position auslesen. -1 = Bewegung links, +1 = Bewegung rechts
    if position2 != last_position2:
        enc2_move = position2 - last_position2
        # praktisches kleines Problem, wenn Encoder zu schnell bewegt wird,
        # dann 1, 2, 3 >> Auswirkung im Moment kein Drama
        print("Position 2: {}".format(enc3_move))

        if enc2_move >= 1:
            # Encoder2 R >> Ziffernblock 1 drücken und loslassen,
            # wird unten dann über Macroo gesteuert
            macropad.keyboard.press(Keycode.KEYPAD_ONE)
            macropad.keyboard.release(Keycode.KEYPAD_ONE)

        elif enc2_move <= -1:
            # Encoder2 L >> Ziffernblock 0 drücken und loslassen,
            # wird unten dann über Macro gesteuert
            macropad.keyboard.press(Keycode.KEYPAD_ZERO)
            macropad.keyboard.release(Keycode.KEYPAD_ZERO)

        last_position2 = position2

    # Demo Encoder2 Drücken Encerknopf und loslassen,
    # LED wird heller beim Drücken >> keine praktische Anwendung
    if not button2.value and not button_held2:
        button_held2 = True
        pixel2.brightness = 0.5
        print("Button 2 pressed")

    if button2.value and button_held2:
        button_held2 = False
        pixel2.brightness = 0.2
        print("Button 2 released")

    # Encoder 3 auslesen
    position3 = -encoder3.position

    # relative Position auslesen. -1 = Bewegung links, +1 = Bewegung rechts
    if position3 != last_position3:
        enc3_move = position3 - last_position3
        # praktisches kleines Problem, wenn Encoder zu schnell bewegt wird,
        # dann 1, 2, 3 >> Auswirkung im Moment kein Drama
        print("Position 3: {}".format(enc3_move))

        if enc3_move >= 1:
            # Encoder3 R >> Ziffernblock 3 drücken und loslassen,
            # wird unten dann über Macroo gesteuert
            macropad.keyboard.press(Keycode.KEYPAD_THREE)
            macropad.keyboard.release(Keycode.KEYPAD_THREE)

        elif enc3_move <= -1:
            # Encoder3 L >> Ziffernblock 2 drücken und loslassen,
            # wird unten dann über Macro gesteuert
            macropad.keyboard.press(Keycode.KEYPAD_TWO)
            macropad.keyboard.release(Keycode.KEYPAD_TWO)

        last_position3 = position3

    # Demo Encoder1 Drücken Encerknopf und loslassen,
    # LED wird heller beim Drücken >> keine praktische Anwendung
    if not button3.value and not button_held3:
        button_held3 = True
        pixel3.brightness = 0.5
        print("Button 3 pressed")

    if button3.value and button_held3:
        button_held3 = False
        pixel3.brightness = 0.2
        print("Button 3 released")


    # Schlaaaaaaaf vor nächstem Durchlauf, was ist eigentlich die Zeiteinheit?
    time.sleep(0.05)


# Ab hier beginnt der Originalcode aus dem Projekt MacroPad Hotkeys
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

"""
A fairly straightforward macro/hotkey program for Adafruit MACROPAD.
Macro key setups are stored in the /macros folder (configurable below),
load up just the ones you're likely to use. Plug into computer's USB port,
use dial to select an application macro set, press MACROPAD keys to send
key sequences.
"""

# pylint: disable=import-error, unused-import, too-few-public-methods

import os
import time
import board
import displayio
import terminalio
import math
import sparkfun_qwiicjoystick
from adafruit_display_shapes.rect import Rect
from adafruit_display_text import label
from adafruit_macropad import MacroPad
from adafruit_neokey.neokey1x4 import NeoKey1x4
from adafruit_seesaw import seesaw, neopixel, rotaryio, digitalio
from adafruit_hid.keycode import Keycode
from adafruit_hid.mouse import Mouse
from rainbowio import colorwheel

am_enc = 3

# CLASSES AND FUNCTIONS ----------------
class App:
    """ Class representing a host-side application, for which we have a set
        of macro sequences. Project code was originally more complex and
        this was helpful, but maybe it's excessive now?"""
    def __init__(self, appdata):
        self.name = appdata['name']
        self.macros = appdata['macros']
        self.enter_macro = appdata['enter_macro']
        self.exit_macro = appdata['exit_macro']

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
        macropad.mouse.release_all()
        macropad.pixels.show()
        macropad.display.refresh()

class SideKeys:

    col_SKe = [0x004000, 0xFF8000, 0x000080, 0x203020]  # color list for Sidekeys -
    col_SKe_c = 0  # Neokey counter for LED colors

    def __init__(self, neoKey):
        self.neoKey = neoKey
        self.key_commands = [[None, None, Keycode.CONTROL, Keycode.CONTROL], [None, None, Keycode.C, Keycode.V]]
        self.debounce_states = [False, False, False, False]
        self.pressed_index = -1
        self.last_pins = 0b11110000

        self.pixels_enabled = True

        self.color = SideKeys.col_SKe[SideKeys.col_SKe_c]  # Initialisation of Sidekeys LED colors
        self.pressed_color = 0xFF2000  # Color of all Sidekey if pressed
        SideKeys.col_SKe_c = SideKeys.col_SKe_c + 1

        self.setAllPixels(self.color)  # call setAllPixels definition >> acces to Sidecolor list

    def setAllPixels(self, color):
        for i in range(4):
            self.neoKey.pixels[i] = SideKeys.col_SKe[i]

    def parsePins(self, pins):
        return [not pins & 0b00010000, not pins & 0b00100000, not pins & 0b01000000, not pins & 0b10000000]

    def update(self):
        pins = self.neoKey.digital_read_bulk(0b11110000)

        if pins == self.last_pins:
            return

        self.last_pins = pins
        keyStates = self.parsePins(pins)

        for i in range(4):
            if keyStates[i] and not self.debounce_states[i]:
                self.neoKey.pixels[i] = self.pressed_color
                self.debounce_states[i] = True
                if self.key_commands[0][i]:
                    for j in range(2):
                        macropad.keyboard.press(self.key_commands[j][i])
                self.pressed_index = i
                continue

            elif not keyStates[i] and self.debounce_states[i]:
                self.neoKey.pixels[i] = SideKeys.col_SKe[i] if self.pixels_enabled else 0x0
                self.debounce_states[i] = False
                if self.key_commands[0][i]:
                   for j in range(2):
                        macropad.keyboard.release(self.key_commands[j][i])
                self.pressed_index = -1
                continue


class SideKnob:

    col_SKn = [0x400000, 0x004000, 0xFF2000, 0x000080, 0xFF8000, 0x000580]  # color list for Sidekeys -
    col_SKn_c = 0 # Neokey counter for LED colors

    def __init__(self, seesaw):
        self.seesaw = seesaw

        seesaw.pin_mode(24, seesaw.INPUT_PULLUP)

        self.button = digitalio.DigitalIO(seesaw, 24)
        self.button_down = False

        self.encoder = rotaryio.IncrementalEncoder(seesaw)
        self.last_position = 0

        self.pixel = neopixel.NeoPixel(seesaw, 6, 1)
        self.pixel.brightness = 0.3
        self.pixels_enabled = True
        self.pixels_enabled_override = False

        self.last_change_time = millis()
        self.color = SideKnob.col_SKn[SideKnob.col_SKn_c]
        self.pixel.fill(self.color)  # change for defined hex val color needed, no rainbow
        SideKnob.col_SKn_c = SideKnob.col_SKn_c + 1

        self.forward_macro = []
        self.reverse_macro = []
        self.button_macro = []

    def setMacros(self, app_index, macro_indicies=[12, 13, 14]):
        self.forward_macro = apps[app_index].macros[macro_indicies[0]][2]
        self.reverse_macro = apps[app_index].macros[macro_indicies[1]][2]
        self.button_macro = apps[app_index].macros[macro_indicies[2]][2]

    def update(self):

        while True:
            position = -self.encoder.position
            if position != self.last_position:
                print("Position: {}".format(position))
                if position > self.last_position:  # Advance forward through the colorwheel.
                    self.color += 10
                    print(len(self.forward_macro))
                    if len(self.forward_macro) == 2:
                        if self.forward_macro[1] == 'Wheel up':
                            macropad.keyboard.press(self.forward_macro[0])
                            macropad.mouse.move(wheel = +1)
                            time.sleep(0.2)
                            macropad.keyboard.release(self.forward_macro[0])
                        elif self.forward_macro[1] == 'Wheel down':
                            macropad.keyboard.press(self.forward_macro[0])
                            macropad.mouse.move(wheel = -1)
                            time.sleep(0.2)
                            macropad.keyboard.release(self.forward_macro[0])
                        if self.forward_macro[1] == 'Mouse right':
                            macropad.mouse.press(macropad.Mouse.RIGHT_BUTTON)
                            macropad.mouse.move(x= +50)
                            time.sleep(0.3)
                            macropad.mouse.release(macropad.Mouse.RIGHT_BUTTON)
                            macropad.mouse.move(x= -50)
                        elif self.forward_macro[1] == 'Mouse left':
                            macropad.mouse.press(macropad.Mouse.RIGHT_BUTTON)
                            macropad.mouse.move(x = -50)
                            time.sleep(0.3)
                            macropad.mouse.release(macropad.Mouse.RIGHT_BUTTON)
                        else:
                            macropad.keyboard.send(self.forward_macro[0])
                            time.sleep(1.5)
                            macropad.keyboard.send(self.forward_macro[1])
                            time.sleep(1.5)
                            macropad.keyboard.send(self.forward_macro[1])
                    else:
                        macropad.keyboard.send(*self.forward_macro)
                else:
                    self.color -= 10  # Advance backward through the colorwheel.
                    print(len(self.reverse_macro))
                    if len(self.reverse_macro) == 2:
                        if self.reverse_macro[1] == 'Wheel up':
                            macropad.keyboard.press(self.reverse_macro[0])
                            macropad.mouse.move(wheel = +1)
                            time.sleep(0.2)
                            macropad.keyboard.release(self.reverse_macro[0])
                        elif self.reverse_macro[1] == 'Wheel down':
                            macropad.keyboard.press(self.reverse_macro[0])
                            macropad.mouse.move(wheel = -1)
                            time.sleep(0.2)
                            macropad.keyboard.release(self.reverse_macro[0])
                        if self.reverse_macro[1] == 'Mouse right':
                            macropad.mouse.move(x = +50)
                            time.sleep(0.3)
                            macropad.mouse.release(macropad.Mouse.RIGHT_BUTTON)
                        elif self.reverse_macro[1] == 'Mouse left':
                            macropad.mouse.press(macropad.Mouse.RIGHT_BUTTON)
                            macropad.mouse.move(x = -50)
                            time.sleep(0.3)
                            macropad.mouse.release(macropad.Mouse.RIGHT_BUTTON)
                            macropad.mouse.move(x = +50)
                        else:
                            macropad.keyboard.send(self.reverse_macro[0])
                            time.sleep(1.5)
                            macropad.keyboard.send(self.reverse_macro[1])
                            time.sleep(1.5)
                            macropad.keyboard.send(self.reverse_macro[1])
                    else:
                        macropad.keyboard.send(*self.reverse_macro)


                self.last_change_time = millis()

            self.last_position = position

            if not self.button.value and not self.button_down:
                self.button_down = True
                macropad.keyboard.press(*self.button_macro)
                self.pixel.fill(colorwheel(self.color))
                self.pixels_enabled_override = True
                self.last_change_time = millis()

            elif self.button.value and self.button_down:
                self.button_down = False
                macropad.keyboard.release(*self.button_macro)
                self.pixels_enabled_override = False
                self.last_change_time = millis()

            if (millis() - self.last_change_time > 100):
                if not self.pixels_enabled and not self.pixels_enabled_override:
                    self.pixel.fill(0x000000)
                return

"""
# Class Joystick:  # Class for access to joystick coordinates >> programming ideas see code.py - SEM

    def __init__(self, Joy):
        self.Joy = joy
        for i in range(3):
            self.start_x = 1023 - joy.horizontal
            self.start_y = 1023 - joy.vertical
        self.mo_xspeed = None
        self.mo_yspeed = None

    def update(self):
        # Joystick auslesen - aktuelle Position absolut, Invertierungen prüfen
        self.x = 1023 - joy.horizontal
        self.y = 1023 - joy.vertical

        # relative Position x und y bestimmen, aktuell y invertieren, Code für y prüfen
        self.x_rel_pos = self.x - self.start_x
        self.y_rel_pos = self.y - self.start_y
        self.y_rel_pos = -self.y_rel_pos

        # Bei Bewegung R Vorzeichen auf 1 setzen und Mousespeed R berechnen
        # (ln- und lin-Anteil)
        if self.x_rel_pos > 0:
            self.x_rel_pos_h = 1
            self.mo_xspeed_h = math.ceil(((10 * math.log(self.x_rel_pos)) + (self.x_rel_pos / 10)))
            self.mo_xspeed = self.mo_xspeed_h * self.x_rel_pos_h

        # Bei Bewegung L Vorzeichen auf -1 setzen und Mousespeed L berechnen
        # (ln- und lin-Anteil)
        elif self.x_rel_pos < 0:
            self.x_rel_pos_h = -1
            # da ln nur mit positiven Zahlen funktioniert, Absoluttwert berechnen
            self.x_rel_pos = self.abs(x_rel_pos)
            self.mo_xspeed_h = math.ceil(((10 * math.log(self.x_rel_pos)) + (self.x_rel_pos / 10)))
            self.mo_xspeed = self.mo_xspeed_h * self.x_rel_pos_h  # Wieder in neagtiven Wert umwandeln

        else:
            self.mo_xspeed = 0  # Keine Bewegung

        if self.y_rel_pos > 0:  # Bewegung U, Rest siehe Bewegung R
            self.y_rel_pos_h = 1
            self.mo_yspeed_h = math.ceil(((10 * math.log(self.y_rel_pos)) + (self.y_rel_pos / 10)))
            self.mo_yspeed = self.mo_yspeed_h * self.y_rel_pos_h

        elif self.y_rel_pos < 0:  # Bewegung D, Rest siehe Bewegung L
            self.y_rel_pos_h = -1
            self.y_rel_pos = abs(self.y_rel_pos)
            self.mo_yspeed_h = math.ceil(((10 * math.log(self.y_rel_pos)) + (self.y_rel_pos / 10)))
            self.mo_yspeed = self.mo_yspeed_h * self.y_rel_pos_h

        else:
            self.mo_yspeed = 0  # Keine Bewegung


"""

def millis():
    return round(time.time() * 1000)

# CONFIGURABLES ------------------------

MACRO_FOLDER = '/macros'

pixels_enabled = True
last_pixels_enabled_state = True
last_app_switch_time = millis()
app_switch_temp_lighting = False

tones = [196, 220, 246, 262, 294, 330, 349, 392, 440, 494, 523, 587]

key_to_app_map = { 1 : 'Lisa.LIMS',
                   0 : 'Quanta'}

# INITIALIZATION -----------------------
macropad = MacroPad()
macropad.display.auto_refresh = False
macropad.pixels.auto_write = False

# use default I2C bus
i2c_bus = board.I2C()

# side keys
neokey1 = SideKeys(NeoKey1x4(i2c_bus, addr=0x30))

# side rotary encoders
knob_1L = SideKnob(seesaw.Seesaw(i2c_bus, addr=0x36))
knob_1R = SideKnob(seesaw.Seesaw(i2c_bus, addr=0x37))
knob_2L = SideKnob(seesaw.Seesaw(i2c_bus, addr=0x38))
knob_2R = SideKnob(seesaw.Seesaw(i2c_bus, addr=0x39))
knob_3L = SideKnob(seesaw.Seesaw(i2c_bus, addr=0x3A))
knob_3R = SideKnob(seesaw.Seesaw(i2c_bus, addr=0x3B))

# Create a Joystick object >> Laden Sparkfun Joystick (JS),
# Standardadresse 0x20, aus der lib, nur ein JS möglich!!
# joy = Joy(sparkfun_qwiicjoystick.Sparkfun_QwiicJoystick(i2c_bus))

# Initialisation Joystick conventional

joy = sparkfun_qwiicjoystick.Sparkfun_QwiicJoystick(i2c_bus)

# letze Positionen JS auf Null setzen
last_x = 0
last_y = 0

# Bestimmung des Nullpunkts x, y JS, Invertierung prüfen
for i in range(3):
    start_x = 1023 - joy.horizontal
    start_y = 1023 - joy.vertical


# Mousespeed x/y auf Null setzen
mo_xspeed = None
mo_yspeed = None


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
macropad.display.show(group)

# Load all the macro key setups from .py files in MACRO_FOLDER
apps = []
app_map = {}
files = os.listdir(MACRO_FOLDER)
files.sort()
idx = 0
for filename in files:
    if filename.endswith('.py') and not filename.startswith('._'):
        try:
            module = __import__(MACRO_FOLDER + '/' + filename[:-3])
            app = App(module.app)
            apps.append(app)
            app_map[app.name] = idx
            idx += 1
        except (SyntaxError, ImportError, AttributeError, KeyError, NameError,
                IndexError, TypeError) as err:
            print("ERROR in", filename)
            import traceback
            traceback.print_exception(err, err, err.__traceback__)
            pass

if not apps:
    group[13].text = 'NO MACRO FILES FOUND'
    macropad.display.refresh()
    while True:
        pass

app_knob_last_position = None
last_encoder_switch = macropad.encoder_switch_debounced.pressed
app_index = 0
apps[app_index].switch()
knob_1L.setMacros(app_index, [12, 13, 14])  # have to be changed with 6 encoders
knob_1R.setMacros(app_index, [15, 16, 17])  # have to be changed with 6 encoders
knob_2L.setMacros(app_index, [18, 19, 20])  # have to be changed with 6 encoders
knob_2R.setMacros(app_index, [21, 22, 23])
knob_3L.setMacros(app_index, [24, 25, 26])
knob_3R.setMacros(app_index, [27, 28, 29])  # 1 = lowest row!

# MAIN LOOP ----------------------------
app_knob_position = 0
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
        mo_xspeed_h = math.ceil(((5 * math.log(x_rel_pos)) + (x_rel_pos / 20)))
        mo_xspeed = mo_xspeed_h * x_rel_pos_h

    # Bei Bewegung L Vorzeichen auf -1 setzen und Mousespeed L berechnen
    # (ln- und lin-Anteil)
    elif x_rel_pos < 0:
        x_rel_pos_h = -1
        # da ln nur mit positiven Zahlen funktioniert, Absoluttwert berechnen
        x_rel_pos = abs(x_rel_pos)
        mo_xspeed_h = math.ceil(((5 * math.log(x_rel_pos)) + (x_rel_pos / 20)))
        mo_xspeed = mo_xspeed_h * x_rel_pos_h  # Wieder in neagtiven Wert umwandeln

    else:
        mo_xspeed = 0  # Keine Bewegung

    if y_rel_pos > 0:  # Bewegung U, Rest siehe Bewegung R
        y_rel_pos_h = 1
        mo_yspeed_h = math.ceil(((5 * math.log(y_rel_pos)) + (y_rel_pos / 20)))
        mo_yspeed = mo_yspeed_h * y_rel_pos_h

    elif y_rel_pos < 0:  # Bewegung D, Rest siehe Bewegung L
        y_rel_pos_h = -1
        y_rel_pos = abs(y_rel_pos)
        mo_yspeed_h = math.ceil(((5 * math.log(y_rel_pos)) + (y_rel_pos / 20)))
        mo_yspeed = mo_yspeed_h * y_rel_pos_h

    else:
        mo_yspeed = 0  # Keine Bewegung

    # Bestimmung, ob sich JS bewegt, Test, ob > 2, 3, ... sinnvoll wäre
    if (abs(x_rel_pos) > 2) or (abs(y_rel_pos) > 2):

        # Position letzte Abfrage festhalten // prüfen, ob weiter gebraucht wird
        last_x = x
        last_y = y
        # Bewegung Maus, durch Code ab Zeile 365 zukünftig abgearbeitet, nur Demo
        macropad.mouse.press(macropad.Mouse.MIDDLE_BUTTON)
        macropad.mouse.move(x=mo_xspeed)
        macropad.mouse.move(y=(-1*mo_yspeed))
        # time.sleep(0.1)

    else:
        joy_m = None
        macropad.mouse.release(macropad.Mouse.MIDDLE_BUTTON)

    # ----------- Neokeys ---------------
    neokey1.update()
    # ----------- End Neokeys ---------------

    # ----------- knobs --------------------
    knob_1L.update()  # to be extented and changed with 6 encoders
    knob_1R.update()
    knob_2L.update()
    knob_2R.update()
    knob_3L.update()
    knob_3R.update()
    # ----------- END knobs --------------------

    # -- cut the lights after 1 second if not enabled
    if not pixels_enabled:
        if (millis() - last_app_switch_time > 1000) and app_switch_temp_lighting:
            for i in range(12):
                macropad.pixels[i] = 0x000000
            knob_1L.pixel.fill(0x000000)
            knob_1R.pixel.fill(0x000000)
            knob_2L.pixel.fill(0x000000)
            knob_2R.pixel.fill(0x000000)
            knob_3L.pixel.fill(0x000000)
            knob_3R.pixel.fill(0x000000)
            macropad.pixels.show()
            app_switch_temp_lighting = False

    # -- app switch check (from encoder or sidekeys).
    app_knob_position = macropad.encoder

    if neokey1.pressed_index == 0 or neokey1.pressed_index == 1:
        app_name = key_to_app_map[neokey1.pressed_index]
        if apps[app_index].exit_macro:
            macropad.keyboard.send(*apps[app_index].exit_macro)
        app_index = app_map[app_name]
        apps[app_index].switch()
        if apps[app_index].enter_macro:
            macropad.keyboard.send(*apps[app_index].enter_macro)
        knob_1L.setMacros(app_index, [12, 13, 14])
        knob_1R.setMacros(app_index, [15, 16, 17])
        knob_2L.setMacros(app_index, [18, 19, 20])
        knob_2R.setMacros(app_index, [21, 22, 23])
        knob_3L.setMacros(app_index, [24, 25, 17])  # 1 = lowest row!
        knob_3R.setMacros(app_index, [27, 28, 29])
        last_app_switch_time = millis()
        app_switch_temp_lighting = True
    elif app_knob_position != app_knob_last_position:
        app_index = app_knob_position % len(apps)
        apps[app_index].switch()
        knob_1L.setMacros(app_index, [12, 13, 14])
        knob_1R.setMacros(app_index, [15, 16, 17])
        knob_2L.setMacros(app_index, [18, 19, 20])
        knob_2R.setMacros(app_index, [21, 22, 23])
        knob_3L.setMacros(app_index, [24, 25, 17])  # 1 = lowest row!
        knob_3R.setMacros(app_index, [27, 28, 29])
        # macropad.play_file("pop.wav")
        app_knob_last_position = app_knob_position
        last_app_switch_time = millis()
        app_switch_temp_lighting = True

    # ------------------------ Macro key events ------------------------
    # -- Handle encoder button - switch LEDs off/on.
    macropad.encoder_switch_debounced.update()
    encoder_switch = macropad.encoder_switch_debounced.pressed
    if encoder_switch:
        pixels_enabled = not pixels_enabled

        if pixels_enabled != last_pixels_enabled_state:
            last_pixels_enabled_state = pixels_enabled

            if pixels_enabled:
                for i in range(12):
                    macropad.pixels[i] = apps[app_index].macros[i][0]
                knob_1L.pixel.fill(colorwheel(knob_1L.color))
                knob_1R.pixel.fill(colorwheel(knob_1R.color))
                knob_2L.pixel.fill(colorwheel(knob_2L.color))
                knob_2R.pixel.fill(colorwheel(knob_2R.color))
                knob_3L.pixel.fill(colorwheel(knob_3L.color))
                knob_3R.pixel.fill(colorwheel(knob_3R.color))
                neokey1.setAllPixels(neokey1.color)
            else:
                for i in range(12):
                    macropad.pixels[i] = 0x000000
                knob_1L.pixel.fill(0x000000)
                knob_1R.pixel.fill(0x000000)
                knob_2L.pixel.fill(0x000000)
                knob_2R.pixel.fill(0x000000)
                knob_3L.pixel.fill(0x000000)
                knob_3R.pixel.fill(0x000000)
                neokey1.setAllPixels(0x0)

            knob_1L.pixels_enabled = pixels_enabled
            knob_1R.pixels_enabled = pixels_enabled
            knob_2L.pixels_enabled = pixels_enabled
            knob_2R.pixels_enabled = pixels_enabled
            knob_3L.pixels_enabled = pixels_enabled
            knob_3R.pixels_enabled = pixels_enabled
            neokey1.pixels_enabled = pixels_enabled

            macropad.pixels.show()
            continue

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

        macropad.pixels[key_number] = 0xFF2000
        macropad.pixels.show()

        for item in sequence:
            if isinstance(item, int):
                if item >= 0:
                    macropad.keyboard.press(item)
                else:
                    macropad.keyboard.release(-item)
            elif isinstance(item, dict):
                if 'buttons' in item:
                    if item['buttons'] >= 0:
                        macropad.mouse.press(item['buttons'])
                    else:
                        macropad.mouse.release(-item['buttons'])
                macropad.mouse.move(item['x'] if 'x' in item else 0,
                                    item['y'] if 'y' in item else 0,
                                    item['wheel'] if 'wheel' in item else 0)
            else:
                macropad.keyboard_layout.write(item)

        # macropad.start_tone(tones[key_number])

    else:
        # macropad.stop_tone()

        for item in sequence:
            if isinstance(item, int) and item >= 0:
                macropad.keyboard.release(item)
            elif isinstance(item, dict):
                if 'buttons' in item:
                    if item['buttons'] >= 0:
                        macropad.mouse.release(item['buttons'])
        if pixels_enabled:
            macropad.pixels[key_number] = apps[app_index].macros[key_number][0]
        else:
            macropad.pixels[key_number] = 0x000000

        macropad.pixels.show()





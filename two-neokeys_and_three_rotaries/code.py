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
from adafruit_display_shapes.rect import Rect
from adafruit_display_text import label
from adafruit_macropad import MacroPad
from adafruit_neokey.neokey1x4 import NeoKey1x4
from adafruit_seesaw import seesaw, neopixel, rotaryio, digitalio
from adafruit_hid.keycode import Keycode
from rainbowio import colorwheel


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
            if i < len(self.macros): # Key in use, set label + LED color
                macropad.pixels[i] = self.macros[i][0]
                group[i].text = self.macros[i][1]
            else:  # Key not in use, no label or LED
                macropad.pixels[i] = 0
                group[i].text = ''
                
        macropad.keyboard.release_all()
        macropad.pixels.show()
        macropad.display.refresh()

class SideKeys:

    def __init__(self, neoKey):
        self.neoKey = neoKey
        self.key_commands = [None, None, None, None]
        self.debounce_states = [False, False, False, False]
        self.pressed_index = -1
        self.last_pins = 0b11110000

        self.pixels_enabled = True

        self.color = 0x00FFFF
        self.pressed_color = 0xFF2000

        self.setAllPixels(self.color)

    def setAllPixels(self, color):
        for i in range(4):
            self.neoKey.pixels[i] = color

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
                if self.key_commands[i]:
                    macropad.keyboard.press(self.key_commands[i])
                self.pressed_index = i
                continue

            elif not keyStates[i] and self.debounce_states[i]:
                self.neoKey.pixels[i] = self.color if self.pixels_enabled else 0x0
                self.debounce_states[i] = False
                if self.key_commands[i]:
                    macropad.keyboard.release(self.key_commands[i])
                self.pressed_index = -1
                continue


class SideKnob:

    def __init__(self, seesaw):
        self.seesaw = seesaw

        seesaw.pin_mode(24, seesaw.INPUT_PULLUP)

        self.button = digitalio.DigitalIO(seesaw, 24)
        self.button_down = False

        self.encoder = rotaryio.IncrementalEncoder(seesaw)
        self.last_position = 0

        self.pixel = neopixel.NeoPixel(seesaw, 6, 1)
        self.pixel.brightness = 0.1
        self.pixels_enabled = True
        self.pixels_enabled_override = False

        self.last_change_time = millis()
        self.color = 200
        self.pixel.fill(colorwheel(self.color))

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
                # print("Position: {}".format(position))
                if position > self.last_position:  # Advance forward through the colorwheel.
                    self.color += 10
                    # print(self.forward_macro)
                    macropad.keyboard.send(*self.forward_macro)
                else:
                    self.color -= 10  # Advance backward through the colorwheel.
                    # print(self.reverse_macro)
                    macropad.keyboard.send(*self.reverse_macro)
                self.color = (self.color + 256) % 256  # wrap around to 0-256
                self.pixel.fill(colorwheel(self.color))

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

def millis():
    return round(time.time() * 1000)

# CONFIGURABLES ------------------------

MACRO_FOLDER = '/macros'

pixels_enabled = True
last_pixels_enabled_state = True
last_app_switch_time = millis()
app_switch_temp_lighting = False

tones = [196, 220, 246, 262, 294, 330, 349, 392, 440, 494, 523, 587]

key_to_app_map = { 3 : 'Application Launch',
                   2 : 'OBS Control',
                   1 : 'Epic Pen',
                   0 : 'Clip Studio Paint'}

# INITIALIZATION -----------------------
macropad = MacroPad()
macropad.display.auto_refresh = False
macropad.pixels.auto_write = False

# use default I2C bus
i2c_bus = board.I2C()

# side keys
neokey_outer = SideKeys(NeoKey1x4(i2c_bus,  addr=0x30))
neokey_inner = SideKeys(NeoKey1x4(i2c_bus, addr=0x31))
# neokey_inner.color = 0xFF2000
# neokey_inner.pressed_color = 0xFFFFFF
# neokey_inner.setAllPixels(0xFF2000)
neokey_inner.key_commands = [Keycode.CONTROL, Keycode.ALT, Keycode.SHIFT, Keycode.WINDOWS]

# side rotary encoders
knob_upr = SideKnob(seesaw.Seesaw(i2c_bus, addr=0x36))
knob_mid = SideKnob(seesaw.Seesaw(i2c_bus, addr=0x37))
knob_lwr = SideKnob(seesaw.Seesaw(i2c_bus, addr=0x38))


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
    if filename.endswith('.py'):
        try:
            module = __import__(MACRO_FOLDER + '/' + filename[:-3])
            app = App(module.app)
            apps.append(app)
            app_map[app.name] = idx
            idx += 1
        except (SyntaxError, ImportError, AttributeError, KeyError, NameError,
                IndexError, TypeError) as err:
            print('error loading app')
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
knob_upr.setMacros(app_index, [12, 13, 14])
knob_mid.setMacros(app_index, [15, 16, 17])
knob_lwr.setMacros(app_index, [18, 19, 20])


# MAIN LOOP ----------------------------
app_knob_position = 0
while True:
    #----------- Neokeys ---------------
    neokey_inner.update()
    neokey_outer.update()
    #----------- End Neokeys ---------------

    # ----------- knobs --------------------
    knob_upr.update()
    knob_mid.update()
    knob_lwr.update()
    # ----------- END knobs --------------------

    #-- cut the lights after 1 second if not enabled
    if not pixels_enabled:
        if (millis() - last_app_switch_time > 1000) and app_switch_temp_lighting:
            for i in range(12):        
                macropad.pixels[i] = 0x000000
            knob_upr.pixel.fill(0x000000)
            knob_mid.pixel.fill(0x000000)
            knob_lwr.pixel.fill(0x000000)
            macropad.pixels.show()
            app_switch_temp_lighting = False

    #-- app switch check (from encoder or sidekeys).
    app_knob_position = macropad.encoder
    
    if neokey_outer.pressed_index >= 0:
        app_name = key_to_app_map[neokey_outer.pressed_index]
        if apps[app_index].exit_macro:
            macropad.keyboard.send(*apps[app_index].exit_macro)
        app_index = app_map[app_name]
        apps[app_index].switch()
        if apps[app_index].enter_macro:
            macropad.keyboard.send(*apps[app_index].enter_macro)
        knob_upr.setMacros(app_index, [12, 13, 14])
        knob_mid.setMacros(app_index, [15, 16, 17])
        knob_lwr.setMacros(app_index, [18, 19, 20])
        last_app_switch_time = millis()
        app_switch_temp_lighting = True
    elif app_knob_position != app_knob_last_position:
        app_index = app_knob_position % len(apps)
        apps[app_index].switch()
        knob_upr.setMacros(app_index, [12, 13, 14])
        knob_mid.setMacros(app_index, [15, 16, 17])
        knob_lwr.setMacros(app_index, [18, 19, 20])
        # macropad.play_file("pop.wav")
        app_knob_last_position = app_knob_position
        last_app_switch_time = millis()
        app_switch_temp_lighting = True

    # ------------------------ Macro key events ------------------------
    # -- Handle encoder button. 
    macropad.encoder_switch_debounced.update()
    encoder_switch = macropad.encoder_switch_debounced.pressed
    if encoder_switch:
        pixels_enabled = not pixels_enabled

        if pixels_enabled != last_pixels_enabled_state:
            last_pixels_enabled_state = pixels_enabled

            if pixels_enabled:
                for i in range(12):
                    macropad.pixels[i] = apps[app_index].macros[i][0]
                knob_upr.pixel.fill(colorwheel(knob_upr.color))
                knob_mid.pixel.fill(colorwheel(knob_mid.color))
                knob_lwr.pixel.fill(colorwheel(knob_lwr.color))
                neokey_inner.setAllPixels(neokey_inner.color)
                neokey_outer.setAllPixels(neokey_outer.color)
            else:
                for i in range(12):
                    macropad.pixels[i] = 0x000000
                knob_upr.pixel.fill(0x000000)
                knob_mid.pixel.fill(0x000000)
                knob_lwr.pixel.fill(0x000000)
                neokey_inner.setAllPixels(0x0)
                neokey_outer.setAllPixels(0x0)

            knob_upr.pixels_enabled = pixels_enabled
            knob_mid.pixels_enabled = pixels_enabled
            knob_lwr.pixels_enabled = pixels_enabled

            neokey_inner.pixels_enabled = pixels_enabled
            neokey_outer.pixels_enabled = pixels_enabled
                    
            macropad.pixels.show()
            continue

    event = macropad.keys.events.get()
    if not event or event.key_number >= len(apps[app_index].macros):
        continue # No key events, or no corresponding macro, resume loop
    key_number = event.key_number
    pressed = event.pressed

    # If code reaches here, a key or the encoder button WAS pressed/released
    # and there IS a corresponding macro available for it...other situations
    # are avoided by 'continue' statements above which resume the loop.

    sequence = apps[app_index].macros[key_number][2]
    if pressed:

        macropad.pixels[key_number] = 0xFFFFFF
        macropad.pixels.show()

        for item in sequence:
            if isinstance(item, int):
                if item >= 0:
                    macropad.keyboard.press(item)
                else:
                    macropad.keyboard.release(-item)
            else:
                macropad.keyboard_layout.write(item)

        # macropad.start_tone(tones[key_number])

    else:
        # macropad.stop_tone()
        
        for item in sequence:
            if isinstance(item, int) and item >= 0:
                macropad.keyboard.release(item)

        if pixels_enabled: 
            macropad.pixels[key_number] = apps[app_index].macros[key_number][0]
        else:
            macropad.pixels[key_number] = 0x000000

        macropad.pixels.show()


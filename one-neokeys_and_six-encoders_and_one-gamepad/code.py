import os
import time
import board
import displayio
import terminalio
import sparkfun_qwiicjoystick
from adafruit_display_shapes.rect import Rect
from adafruit_display_text import label
from adafruit_macropad import MacroPad
from adafruit_neokey.neokey1x4 import NeoKey1x4
from adafruit_seesaw import seesaw
from rainbowio import colorwheel
from config import Config # Configuration management in a separate file (config.py)
from handler_sidekeys import SideKeys
from handler_sideknob import SideKnob
from handler_joystick import JoyStick
#from handler_macropad import MacroPad

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

def millis():
    return round(time.time() * 1000)

# CONFIGURABLES ------------------------
pixels_enabled = True
last_pixels_enabled_state = True
last_app_switch_time = millis()
app_switch_temp_lighting = False

key_to_app_map = { 1 : 'Lisa.LIMS',
                   0 : 'Quanta'}

# INITIALIZATION -----------------------

# use default I2C bus
i2c_bus = board.I2C()

# MacroPad
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
macropad.display.show(group)

# Load all the macro key setups from .py files in MACRO_FOLDER
apps = []
app_map = {}
files = os.listdir(Config.Globals.MACRO_FOLDER)
files.sort()
idx = 0
for filename in files:
    if filename.endswith('.py') and not filename.startswith('._'):
        try:
            module = __import__(Config.Globals.MACRO_FOLDER + '/' + filename[:-3])
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

# side keys
neokey1 = SideKeys(NeoKey1x4(i2c_bus, addr=0x30), macropad)

# side rotary encoders
knob_1L = SideKnob(seesaw.Seesaw(i2c_bus, addr=0x36), macropad, apps)
knob_1R = SideKnob(seesaw.Seesaw(i2c_bus, addr=0x37), macropad, apps)
knob_2L = SideKnob(seesaw.Seesaw(i2c_bus, addr=0x38), macropad, apps)
knob_2R = SideKnob(seesaw.Seesaw(i2c_bus, addr=0x39), macropad, apps)
knob_3L = SideKnob(seesaw.Seesaw(i2c_bus, addr=0x3A), macropad, apps)
knob_3R = SideKnob(seesaw.Seesaw(i2c_bus, addr=0x3B), macropad, apps)
knob_1L.setMacros(app_index, [12, 13, 14])  # have to be changed with 6 encoders
knob_1R.setMacros(app_index, [15, 16, 17])  # have to be changed with 6 encoders
knob_2L.setMacros(app_index, [18, 19, 20])  # have to be changed with 6 encoders
knob_2R.setMacros(app_index, [21, 22, 23])
knob_3L.setMacros(app_index, [24, 25, 26])
knob_3R.setMacros(app_index, [27, 28, 29])  # 1 = lowest row!

# Create a Joystick object >> Laden Sparkfun Joystick (JS),
# Standardadresse 0x20, aus der lib, nur ein JS möglich!!
# joy = Joy(sparkfun_qwiicjoystick.Sparkfun_QwiicJoystick(i2c_bus))

# Initialisation Joystick 
joystick_1R = JoyStick(sparkfun_qwiicjoystick.Sparkfun_QwiicJoystick(i2c_bus), macropad)

# MAIN LOOP ----------------------------
app_knob_position = 0
while True:
    # ----------- JoyStick ---------------
    joystick_1R.update()

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

        # macropad.start_tone(Config.MarcoPad.keypress_tones[key_number])

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





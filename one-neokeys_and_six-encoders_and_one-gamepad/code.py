import os
import board # type: ignore
import displayio # type: ignore
import terminalio # type: ignore
import sparkfun_qwiicjoystick
from adafruit_display_shapes.rect import Rect # type: ignore
from adafruit_display_text import label
from adafruit_macropad import MacroPad # type: ignore
from adafruit_neokey.neokey1x4 import NeoKey1x4
from adafruit_seesaw import seesaw
from rainbowio import colorwheel # type: ignore
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
        display_group[13].text = self.name   # Application name

        for i in range(12):
            if i < len(self.macros):  # Key in use, set label + LED color
                macropad.pixels[i] = self.macros[i][0]
                display_group[i].text = self.macros[i][1]
            else:  # Key not in use, no label or LED
                macropad.pixels[i] = 0
                display_group[i].text = ''

        macropad.keyboard.release_all()
        macropad.mouse.release_all()
        macropad.pixels.show()
        macropad.display.refresh()

# CONFIGURABLES ------------------------
pixels_enabled = True 
last_pixels_enabled_state = True 
last_app_switch_time = Config.GlobalFunctions.get_millis() 
app_switch_temp_lighting = False 

key_to_app_map = { 1 : 'Lisa.LIMS', 
                   0 : 'Quanta'}

# INITIALIZATION -----------------------

# use default I2C bus
i2c_bus = board.I2C() 

# MacroPad
macropad = MacroPad() #In Main
macropad.display.auto_refresh = False 
macropad.pixels.auto_write = False 

# Set up displayio display_group with all the labels
#@staticmethod < wenn in main einbauen
def initialize_display(macropad):
    """
    Erstellt eine Displaygruppe für ein Macropad und fügt Labels für die Tasten und eine Kopfzeile hinzu.

    Args:
        macropad: Das Macropad-Objekt, das die Displayattribute enthält.

    Returns:
        displayio.Group: Eine Gruppe von Displayelementen.
    """
    # Definiere Konstanten für die Farben und die Schriftart
    BACKGROUND_COLOR = 0xFFFFFF  # Weiß
    TEXT_COLOR = 0x000000  # Schwarz
    FONT = terminalio.FONT  # Standard Monospace-Schriftart

    display_group = displayio.Group()  # Erstelle eine neue Gruppe für die Displayelemente

    # Erstelle Labels für die 12 Tasten des Macropads
    for key_index in range(12):
        x = key_index % 3  # Position in der Reihe (0, 1, 2)
        y = key_index // 3  # Position in der Spalte (0, 1, 2, 3)
        # Berechne die verankerte Position jedes Labels
        anchored_position = ((macropad.display.width - 1) * x / 2,
                             macropad.display.height - 1 - (3 - y) * 12)
        # Füge jedes Label zur Gruppe hinzu
        display_group.append(label.Label(FONT, text='', color=BACKGROUND_COLOR,
                                         anchored_position=anchored_position,
                                         anchor_point=(x / 2, 1.0)))

    # Füge ein Rechteck als Kopfzeile am oberen Rand des Displays hinzu
    display_group.append(Rect(0, 0, macropad.display.width, 12, fill=BACKGROUND_COLOR))
    # Füge ein zentrales Label in der Kopfzeile hinzu
    display_group.append(label.Label(FONT, text='', color=TEXT_COLOR,
                                     anchored_position=(macropad.display.width//2, -2),
                                     anchor_point=(0.5, 0.0)))

    # Zeige die Gruppe auf dem Display des Macropads an
    macropad.display.show(display_group)
    return display_group

display_group = initialize_display(macropad)

# Load all the macro key setups from .py files in macro_folder
#@staticmethod < wenn in main einbauen
def load_macros():
    """ Lädt alle Makroeinstellungen aus Python-Dateien im konfigurierten Makroverzeichnis.
    
    Returns:
        tuple: Zwei Elemente, eine Liste von `App`-Instanzen und ein Wörterbuch, das Anwendungsnamen auf deren Indizes abbildet.
    
    Raises:
        SyntaxError, ImportError, AttributeError, KeyError, NameError, IndexError, TypeError:
            Fängt und protokolliert Ausnahmen, die beim Laden der Makrodateien auftreten.
    """
    apps = []
    app_map = {}
    files = os.listdir(Config.Globals.macro_folder)
    files.sort()
    idx = 0
    for filename in files:
        if filename.endswith('.py') and not filename.startswith('._'):
            try:
                module = __import__(Config.Globals.macro_folder + '/' + filename[:-3])
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
        display_group[13].text = 'NO MACRO FILES FOUND'
        macropad.display.refresh()
        while True:
            pass
    return apps, app_map

apps, app_map = load_macros()
app_index = 0  # Setze den Startindex
apps[app_index].switch()  # Starte die Haupt-App

# side keys
neokey1 = SideKeys(NeoKey1x4(i2c_bus, addr=0x30), macropad) 

# side rotary encoders 
knob_1L = SideKnob(seesaw.Seesaw(i2c_bus, addr=0x36), macropad, apps)
knob_1R = SideKnob(seesaw.Seesaw(i2c_bus, addr=0x37), macropad, apps)
knob_2L = SideKnob(seesaw.Seesaw(i2c_bus, addr=0x38), macropad, apps)
knob_2R = SideKnob(seesaw.Seesaw(i2c_bus, addr=0x39), macropad, apps)
knob_3L = SideKnob(seesaw.Seesaw(i2c_bus, addr=0x3A), macropad, apps)
knob_3R = SideKnob(seesaw.Seesaw(i2c_bus, addr=0x3B), macropad, apps) # 1 = lowest row!

# side rotary encoders - Initialize first Macro
knob_1L.setMacros(app_index, [12, 13, 14])  
knob_1R.setMacros(app_index, [15, 16, 17])  
knob_2L.setMacros(app_index, [18, 19, 20])  
knob_2R.setMacros(app_index, [21, 22, 23])
knob_3L.setMacros(app_index, [24, 25, 26])
knob_3R.setMacros(app_index, [27, 28, 29])  

# Initialisation Joystick 
# Create a Joystick object >> Laden Sparkfun Joystick (JS),
# Standardadresse 0x20, aus der lib, nur ein JS möglich!!
joystick_1R = JoyStick(sparkfun_qwiicjoystick.Sparkfun_QwiicJoystick(i2c_bus), macropad) 

# MAIN LOOP ----------------------------
app_knob_last_position = None
app_knob_position = 0
while True:
    # ----------- JoyStick ---------------
    joystick_1R.update()
    # ----------- END JoyStick --------------------
    # ----------- Neokeys ---------------
    neokey1.update()
    # ----------- END Neokeys --------------------
    # ----------- SideKnobs --------------------
    knob_1L.update()  
    knob_1R.update()
    knob_2L.update()
    knob_2R.update()
    knob_3L.update()
    knob_3R.update()
    # ----------- END SideKnobs --------------------

    # -- cut the lights after 1 second if not enabled
    if not pixels_enabled:
        if (Config.GlobalFunctions.get_millis() - last_app_switch_time > 1000) and app_switch_temp_lighting:
            for i in range(12):
                macropad.pixels[i] = 0x000000
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
        last_app_switch_time = Config.GlobalFunctions.get_millis()
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
        last_app_switch_time = Config.GlobalFunctions.get_millis()
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
            else:
                for i in range(12):
                    macropad.pixels[i] = 0x000000

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

    else:

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





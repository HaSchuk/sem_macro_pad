import os, board # type: ignore
import displayio, terminalio # type: ignore
import sparkfun_qwiicjoystick
from adafruit_display_shapes.rect import Rect # type: ignore
from adafruit_display_text import label
from adafruit_macropad import MacroPad # type: ignore
from adafruit_neokey.neokey1x4 import NeoKey1x4
from adafruit_seesaw import seesaw
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
    
    def switch(self, macropad, display_group):
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

class Main:
    _instance = None

    def __init__(self):
        self._initialize_hardware()
        self.run()

    @classmethod
    def get_instance(cls):
        """Statische Methode, um die Instanz zu erhalten oder zu erstellen."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _initialize_hardware(self):
        # Initialize i2c Board
        self.i2c_bus = board.I2C()
        # Initialize MacroPad incl. settings
        self.macropad = MacroPad()
        self.macropad.display.auto_refresh = False
        self.macropad.pixels.auto_write = False
        # Initialize Display
        self._initialize_display()
        # Load macros from macros folder
        self._load_macros()
        # Initialize Controll Interfaces
        self._initialize_control_interfaces(self.i2c_bus, self.macropad, Config.Globals.app_index, self.apps)
        # Switch to default App
        self.apps[Config.Globals.app_index].switch(self.macropad, self.display_group)

    def _initialize_display(self):
        """
        Erstellt eine Displaygruppe für ein Macropad und fügt Labels für die Tasten und eine Kopfzeile hinzu.

        Args:
            macropad: Das Macropad-Objekt, das die Displayattribute enthält.
        """
        # Definiere Konstanten für die Farben und die Schriftart
        BACKGROUND_COLOR = 0xFFFFFF  # Weiß
        TEXT_COLOR = 0x000000  # Schwarz
        FONT = terminalio.FONT  # Standard Monospace-Schriftart

        self.display_group = displayio.Group()  # Erstelle eine neue Gruppe für die Displayelemente

        # Erstelle Labels für die 12 Tasten des Macropads
        for key_index in range(12):
            x = key_index % 3  # Position in der Reihe (0, 1, 2)
            y = key_index // 3  # Position in der Spalte (0, 1, 2, 3)
            # Berechne die verankerte Position jedes Labels
            anchored_position = ((self.macropad.display.width - 1) * x / 2,
                                self.macropad.display.height - 1 - (3 - y) * 12)
            # Füge jedes Label zur Gruppe hinzu
            self.display_group.append(label.Label(FONT, text='', color=BACKGROUND_COLOR,
                                            anchored_position=anchored_position,
                                            anchor_point=(x / 2, 1.0)))

        # Füge ein Rechteck als Kopfzeile am oberen Rand des Displays hinzu
        self.display_group.append(Rect(0, 0, self.macropad.display.width, 12, fill=BACKGROUND_COLOR))
        # Füge ein zentrales Label in der Kopfzeile hinzu
        self.display_group.append(label.Label(FONT, text='', color=TEXT_COLOR,
                                        anchored_position=(self.macropad.display.width//2, -2),
                                        anchor_point=(0.5, 0.0)))

        # Zeige die Gruppe auf dem Display des Macropads an
        self.macropad.display.show(self.display_group)

    def _load_macros(self):
        """ Lädt alle Makroeinstellungen aus Python-Dateien im konfigurierten Makroverzeichnis.
        
        Raises:
            SyntaxError, ImportError, AttributeError, KeyError, NameError, IndexError, TypeError:
                Fängt und protokolliert Ausnahmen, die beim Laden der Makrodateien auftreten.
        """
        self.apps = []
        self.app_map = {}
        files = os.listdir(Config.Globals.macro_folder)
        files.sort()
        idx = 0
        for filename in files:
            if filename.endswith('.py') and not filename.startswith('._'):
                try:
                    module = __import__(Config.Globals.macro_folder + '/' + filename[:-3])
                    app = App(module.app)
                    self.apps.append(app)
                    self.app_map[app.name] = idx
                    idx += 1
                except (SyntaxError, ImportError, AttributeError, KeyError, NameError,
                        IndexError, TypeError) as err:
                    print("ERROR in", filename)
                    import traceback
                    traceback.print_exception(err, err, err.__traceback__)
                    pass
        if not self.apps:
            self.display_group[13].text = 'NO MACRO FILES FOUND'
            self.macropad.display.refresh()
            while True:
                pass
        
    def _initialize_control_interfaces(self, i2cBus, MacroPad, AppIndex, Apps):
        self.sideknobs, self.sidekeys, self.joysticks  = {}, {}, {}
        
        for name, address, macroindices in Config.SideKnob.sideknob_list:
            # Erstelle eine neue SideKnob-Instanz mit der gegebenen I2C-Adresse
            sideknob = SideKnob(seesaw.Seesaw(i2cBus, addr=address), MacroPad, Apps, macroindices)
            # Verbinde MacroPosition mit SideKnob
            sideknob.setMacros(AppIndex)
            # Füge die neue Instanz dem Dictionary hinzu, wobei der Name als Schlüssel dient
            self.sideknobs[name] = sideknob
        
        for name, address, macroindices in Config.SideKeys.sidekey_list:
            # Erstelle eine neue Sidekey-Instanz mit der gegebenen I2C-Adresse
            sidekey = SideKeys(NeoKey1x4(i2cBus, addr=address), MacroPad, Apps)
            # Füge die neue Instanz dem Dictionary hinzu, wobei der Name als Schlüssel dient
            self.sidekeys[name] = sidekey
        
        for name, address in Config.JoyStick.joystick_list:
            # Erstelle eine neue Joystick-Instanz mit der gegebenen I2C-Adresse
            joystick = JoyStick(sparkfun_qwiicjoystick.Sparkfun_QwiicJoystick(i2cBus), MacroPad)
            # Füge die neue Instanz dem Dictionary hinzu, wobei der Name als Schlüssel dient
            self.joysticks[name] = joystick

    @staticmethod
    def _control_interfaces_update(*interface_dicts):
        """ 
        Erwartet Object Dicts mit Interface Elementen die mit initialize_* erzeugt wurden und verwendet die update Methode
        Überspringt Klassen ohne .update Methode
        Aufruf: _control_interfaces_update(dict1, dict2, dict3)
        """
        combined_interfaces = {}
        for interface_dict in interface_dicts:
            combined_interfaces.update(interface_dict)
        for interface in combined_interfaces.values():
            # Prüfe, ob das Interface eine 'update' Methode hat, bevor du sie aufrufst
            if hasattr(interface, 'update'):
                interface.update()

    @staticmethod
    def _control_interfaces_update_macros(AppIndex, *interface_dicts):
        """ 
        Erwartet Object Dicts mit Interface Elementen die mit initialize_* erzeugt wurden und verwendet die update Methode
        Überspringt Klassen ohne .update Methode
        Aufruf: _control_interfaces_update_macros(AppIndex, dict1, dict2, dict3)
        """
        combined_interfaces = {}
        for interface_dict in interface_dicts:
            combined_interfaces.update(interface_dict)
        for interface in combined_interfaces.values():
            # Prüfe, ob das Interface eine 'update' Methode hat, bevor du sie aufrufst
            if hasattr(interface, 'setMacros'):
                interface.setMacros(AppIndex)

    def run(self):
        pixels_enabled = True 
        last_pixels_enabled_state = True 
        app_knob_last_position = None
        app_knob_position = 0
        while True:
            # ----------- Controller Interfaces --------------------
            self._control_interfaces_update(self.sideknobs, self.sidekeys, self.joysticks)
            # ----------- END Controller Interfaces --------------------

            # -- app switch check (from encoder or sidekeys).
            app_knob_position = self.macropad.encoder

            #TODO: Implementieren in Handler Klasse
            for key in self.sidekeys.values():
                if key.pressed_index == 0 or key.pressed_index == 1:
                    app_name = Config.MacroPad.key_to_app_map[key.pressed_index]
                    if self.apps[Config.Globals.app_index].exit_macro:
                        self.macropad.keyboard.send(*self.apps[Config.Globals.app_index].exit_macro)
                    Config.Globals.app_index = self.app_map[app_name]
                    self.apps[Config.Globals.app_index].switch(self.macropad, self.display_group)
                    if self.apps[Config.Globals.app_index].enter_macro:
                        self.macropad.keyboard.send(*self.apps[Config.Globals.app_index].enter_macro)
                    self._control_interfaces_update_macros(Config.Globals.app_index, self.sideknobs, self.sidekeys)

            if app_knob_position != app_knob_last_position:
                Config.Globals.app_index = app_knob_position % len(self.apps)
                self.apps[Config.Globals.app_index].switch(self.macropad, self.display_group)
                self._control_interfaces_update_macros(Config.Globals.app_index, self.sideknobs, self.sidekeys)
                app_knob_last_position = app_knob_position

            # ------------------------ Macro key events ------------------------
            # -- Handle encoder button - switch LEDs off/on.
            self.macropad.encoder_switch_debounced.update()
            encoder_switch = self.macropad.encoder_switch_debounced.pressed
            if encoder_switch:
                pixels_enabled = not pixels_enabled

                if pixels_enabled != last_pixels_enabled_state:
                    last_pixels_enabled_state = pixels_enabled

                    if pixels_enabled:
                        for i in range(12):
                            self.macropad.pixels[i] = self.apps[Config.Globals.app_index].macros[i][0]
                    else:
                        for i in range(12):
                            self.macropad.pixels[i] = 0x000000

                    self.macropad.pixels.show()
                    continue

            event = self.macropad.keys.events.get()
            if not event or event.key_number >= len(self.apps[Config.Globals.app_index].macros):
                continue  # No key events, or no corresponding macro, resume loop
            key_number = event.key_number
            pressed = event.pressed

            # If code reaches here, a key or the encoder button WAS pressed/released
            # and there IS a corresponding macro available for it...other situations
            # are avoided by 'continue' statements above which resume the loop.

            sequence = self.apps[Config.Globals.app_index].macros[key_number][2]
            if pressed:

                self.macropad.pixels[key_number] = 0xFF2000
                self.macropad.pixels.show()

                for item in sequence:
                    if isinstance(item, int):
                        if item >= 0:
                            self.macropad.keyboard.press(item)
                        else:
                            self.macropad.keyboard.release(-item)
                    elif isinstance(item, dict):
                        if 'buttons' in item:
                            if item['buttons'] >= 0:
                                self.macropad.mouse.press(item['buttons'])
                            else:
                                self.macropad.mouse.release(-item['buttons'])
                        self.macropad.mouse.move(item['x'] if 'x' in item else 0,
                                            item['y'] if 'y' in item else 0,
                                            item['wheel'] if 'wheel' in item else 0)
                    else:
                        self.macropad.keyboard_layout.write(item)

            else:

                for item in sequence:
                    if isinstance(item, int) and item >= 0:
                        self.macropad.keyboard.release(item)
                    elif isinstance(item, dict):
                        if 'buttons' in item:
                            if item['buttons'] >= 0:
                                self.macropad.mouse.release(item['buttons'])
                if pixels_enabled:
                    self.macropad.pixels[key_number] = self.apps[Config.Globals.app_index].macros[key_number][0]
                else:
                    self.macropad.pixels[key_number] = 0x000000

                self.macropad.pixels.show()

if __name__ == '__main__':
    main = Main.get_instance()


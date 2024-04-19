import os, board # type: ignore
import displayio, terminalio # type: ignore
from adafruit_display_shapes.rect import Rect # type: ignore
from adafruit_display_text import label
from config import Config # Configuration management in a separate file (config.py)

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

        for i in range(Config.MacroPad.count_keys):
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
    def __init__(self):
        self._initialize_hardware()
        self.run()

    def _initialize_hardware(self):
        # Initialize i2c Board
        self.i2c_bus = board.I2C()
        # Initialize MacroPad incl. settings
        self._initialize_macropad()
        # Initialize Display
        self._initialize_display()
        # Load macros from macros folder
        self._load_macros()
        # Initialize Controll Interfaces 
        self._initialize_control_interfaces()
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
        for key_index in range(Config.MacroPad.count_keys):
            x = key_index % 3  # Position in der Reihe (0, 1, 2)
            y = key_index // 3  # Position in der Spalte (0, 1, 2, 3)
            # Berechne die verankerte Position jedes Labels
            anchored_position = ((self.macropad.display.width - 1) * x / 2,
                                self.macropad.display.height - 1 - (3 - y) * Config.MacroPad.count_keys)
            # Füge jedes Label zur Gruppe hinzu
            self.display_group.append(label.Label(FONT, text='', color=BACKGROUND_COLOR,
                                            anchored_position=anchored_position,
                                            anchor_point=(x / 2, 1.0)))

        # Füge ein Rechteck als Kopfzeile am oberen Rand des Displays hinzu
        self.display_group.append(Rect(0, 0, self.macropad.display.width, Config.MacroPad.count_keys, fill=BACKGROUND_COLOR))
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
        self.app = None
        self.apps = []
        self.app_map = {}
        files = os.listdir(Config.Globals.macro_folder)
        files.sort()
        idx = 0
        for filename in files:
            if filename.endswith('.py') and not filename.startswith('._'):
                try:
                    module = __import__(Config.Globals.macro_folder + '/' + filename[:-3])
                    self.app = App(module.app)
                    self.apps.append(self.app)
                    self.app_map[self.app.name] = idx
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
    
    def _initialize_macropad(self):
        # Import Handler
        from handler_macropad import MacroPadHandler
        # Initialize MacroPadHandler
        self.macropad = MacroPadHandler(self)

    def _initialize_control_interfaces(self):
        # Import Handlers
        from handler_sidekeys import SideKeysHandler
        from handler_sideknob import SideKnobHandler
        from handler_joystick import JoyStickHandler
        #from handler_macropad import MacroPad
        self.sideknobs, self.sidekeys, self.joysticks  = {}, {}, {}
        
        for name, address, macroindices in Config.SideKnob.sideknob_list:
            # Erstelle eine neue SideKnob-Instanz mit der gegebenen I2C-Adresse
            sideknob = SideKnobHandler(self, address, macroindices)
            # Füge die neue Instanz dem Dictionary hinzu, wobei der Name als Schlüssel dient
            self.sideknobs[name] = sideknob
        
        for name, address, macroindices in Config.SideKeys.sidekey_list:
            # Erstelle eine neue Sidekey-Instanz mit der gegebenen I2C-Adresse
            sidekey = SideKeysHandler(self, address, macroindices)
            # Füge die neue Instanz dem Dictionary hinzu, wobei der Name als Schlüssel dient
            self.sidekeys[name] = sidekey
        
        for name, address in Config.JoyStick.joystick_list:
            # Erstelle eine neue Joystick-Instanz mit der gegebenen I2C-Adresse
            joystick = JoyStickHandler(self, address)
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
        while True:
            # ----------- Controller Interfaces --------------------
            self._control_interfaces_update(self.sideknobs, self.sidekeys, self.joysticks)
            self.macropad.update()
            # ----------- END Controller Interfaces --------------------

if __name__ == '__main__':
    main = Main()
from config import Config  # Configuration management in a separate file (config.py)
from adafruit_neokey.neokey1x4 import NeoKey1x4
import time

class SideKeysHandler:
    """
    Klasse zur Verwaltung der seitlichen Tasten am Macropad.

    Diese Klasse kümmert sich um die Erkennung von Tastendrücken und -freigaben
    für seitlich angebrachte Tasten, steuert zugehörige NeoPixel LEDs
    und führt konfigurierte Tastenbefehle aus.
    """
    PIN_MASK = 0b11110000  # Maske, um die relevanten Pins zu isolieren

    def __init__(self, main_instance, hw_address, macroIndices):
        """
        Initialisiert eine neue Instanz der SideKeysHandler-Klasse.
        
        :param main_instance: Die Hauptinstanz der Anwendung, die das Macropad und 
                              andere Komponenten verwaltet.
        :param hw_address: Die Hardware-Adresse des NeoKey-Objekts auf dem I2C-Bus.
        :param macroIndices: Eine Liste von Indizes, die den Tasten zugewiesene Makros darstellen.
        """
        self.main = main_instance
        self.macroindices = macroIndices
        self.neoKey = NeoKey1x4(self.main.i2c_bus, addr=hw_address)
        self._initialize_settings()
        self.set_macros()
        self._set_all_pixels()

    def _initialize_settings(self):
        """
        Initialisiert die Einstellungen des SideKeys.
        """
        self.count_keys = Config.SideKeys.count_keys
        self.debounce_states = [False] * self.count_keys
        self.key_states = Config.SideKeys.key_states
        self.pressed_index = -1
        self.last_pins = self.PIN_MASK
        self.led_pixel_color = [ Config.SideKeys.led_pixels_color_default ] * self.count_keys
        self.led_pixels_color_enabled = Config.SideKeys.led_pixels_color_enabled
        self.neoKey.pixels.brightness = Config.SideKeys.led_pixels_color_brightness 
        self.led_pixels_color_off = Config.Globals.led_color_off
        self.pressed_color = Config.SideKeys.led_pixels_color_pressed_default

    def set_macros(self):
        """
        Lädt die Makros für die aktuell ausgewählte App und aktualisiert die Tastenzuweisungen.
        """
        app_macros = self.main.apps[Config.Globals.app_index].macros

        # Filtere nur die Makros, die den angegebenen Indizes entsprechen
        filtered_macros = [app_macros[idx] for idx in self.macroindices if idx < len(app_macros)]
        self.key_commands = [macro[2] for macro in filtered_macros]
        self.led_pixel_color = [macro[0] for macro in filtered_macros]

        self._set_all_pixels()  # Aktualisiere LED-Farben

    def _set_all_pixels(self):
        """
        Setzt die Farbe aller NeoPixel LEDs basierend auf der aktuellen App.
        """
        for i, color in enumerate(self.led_pixel_color):
            time.sleep(0.05)
            self.neoKey.pixels[i] = color if self.led_pixels_color_enabled else self.led_pixels_color_off
        self.neoKey.pixels.show()

    def _parse_pins(self, pins):
        """
        Wandelt die gelesenen Pin-Zustände in Tastenzustände um.
        
        :param pins: Die gelesenen Pin-Zustände.
        :return: Eine Liste von Booleschen Werten, die den Zustand jeder Taste repräsentieren.
        """
        return [not pins & mask for mask in self.key_states]

    def _handle_key_press(self, index):
        """
        Verarbeitet das Drücken einer Taste.

        :param index: Der Index der gedrückten Taste.
        """
        if index >= len(self.key_commands):
            print(f"Index {index} is out of range for key_commands")
            return
        
        self.neoKey.pixels[index] = self.pressed_color
        self.neoKey.pixels.show()

        key_macro = self.key_commands[index]
        # Konvertiere den Makro-Befehl in Kleinbuchstaben und prüfe, ob der Befehl ein Appswitcher-Makro ist
        if key_macro and isinstance(key_macro[0], str) and 'appswitch_' in key_macro[0].lower():
            # Versuche, die App-Nummer aus dem Makro zu extrahieren
            try:
                app_number = int(key_macro[0].split('_')[-1])
                self.main._control_interfaces_update_macros(app_number, self.main.sideknobs, self.main.sidekeys)
            except ValueError:
                print("Fehler: Ungültige App-Nummer in Makro")
        else:
            # Normale Makroausführung
            for command in key_macro:
                if isinstance(command, int):
                    self.main.macropad.keyboard.press(command)


    def _handle_key_release(self, index):
        """
        Verarbeitet das Loslassen einer Taste.

        :param index: Der Index der losgelassenen Taste.
        """
        if index >= len(self.neoKey.pixels):
            print(f"Index {index} out of range for NeoPixels")
            return

        self.neoKey.pixels[index] = self.led_pixel_color[index] if self.led_pixels_color_enabled else self.led_pixels_color_off
        self.neoKey.pixels.show()

        if index < len(self.key_commands) and self.key_commands[index]:
            for command in self.key_commands[index]:
                if isinstance(command, int):
                    self.main.macropad.keyboard.release(command)
                else:
                    print(f"Invalid command type: {command} at index {index}")


    def update(self):
        """
        Aktualisiert den Status der Seitentasten und verarbeitet Ereignisse.
        """
        pins = self.neoKey.digital_read_bulk(self.PIN_MASK)
        if pins == self.last_pins:
            return

        self.last_pins = pins
        key_states = self._parse_pins(pins)

        for i, state in enumerate(key_states):
            if state and not self.debounce_states[i]:
                self._handle_key_press(i)
                self.debounce_states[i] = True
                self.pressed_index = i

            elif not state and self.debounce_states[i]:
                self._handle_key_release(i)
                self.debounce_states[i] = False
                self.pressed_index = -1
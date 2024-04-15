from config import Config  # Configuration management in a separate file (config.py)
import time

class SideKeys:
    """Klasse zur Verwaltung der seitlichen Tasten am Macropad.
    Diese Klasse kümmert sich um die Erkennung von Tastendrücken und -freigaben
    für seitlich angebrachte Tasten, steuert zugehörige NeoPixel LEDs
    und führt konfigurierte Tastenbefehle aus.
    """
    PIN_MASK = 0b11110000  # Maske, um die relevanten Pins zu isolieren
    KEY_STATES = [0b00010000, 0b00100000, 0b01000000, 0b10000000]  # Pin-Zustände

    def __init__(self, neoKey, macroPad, Apps):
        """Initialisiert eine neue Instanz der SideKeys-Klasse.
        
        :param neoKey: Das NeoKey-Objekt für die LED-Steuerung.
        :param macroPad: Das Macropad-Objekt für die Tastensteuerung.
        """
        self.neoKey = neoKey
        self.macropad = macroPad
        self.apps = Apps
        self.count_keys = Config.SideKeys.count_keys
        self.key_commands = Config.SideKeys.key_commands
        self.debounce_states = [False] * self.count_keys
        self.pressed_index = -1
        self.last_pins = self.PIN_MASK
        self.led_pixel_color_default = Config.SideKeys.led_pixels_color_default
        self.led_pixel_color = Config.SideKeys.led_pixels_color
        self.led_pixels_color_enabled = Config.SideKeys.led_pixels_color_enabled
        self.neoKey.pixels.brightness = Config.SideKeys.led_pixels_color_brightness 
        self.led_pixels_color_off = Config.Globals.led_color_off
        self.pressed_color = Config.SideKeys.led_pixels_color_pressed_default

        self._set_all_pixels(self.led_pixel_color)

    def _set_all_pixels(self, color):
        """Setzt die Farbe aller NeoPixel LEDs.
        
        :param color: Die Farbe, die für alle NeoPixel LEDs gesetzt werden soll.
        """
        
        for i, col in enumerate(color):
            if self.led_pixels_color_enabled:
                self.neoKey.pixels[i] = self.led_pixel_color_default
                time.sleep(0.05)
                self.neoKey.pixels[i] = col
            else:
                self.neoKey.pixels[i] = self.led_pixels_color_off

    def _parse_pins(self, pins):
        """Wandelt die gelesenen Pin-Zustände in Tastenzustände um.
        
        :param pins: Die gelesenen Pin-Zustände.
        :return: Eine Liste von Booleschen Werten, die den Zustand jeder Taste repräsentieren.
        """
        return [not pins & mask for mask in self.KEY_STATES]

    def _handle_key_press(self, index):
        """Verarbeitet das Drücken einer Taste.
        
        :param index: Der Index der gedrückten Taste.
        """
        self.neoKey.pixels[index] = self.pressed_color
        if self.key_commands[0][index]:
            for command in self.key_commands:
                key = command[index]
                if key:
                    self.macropad.keyboard.press(key)

    def _handle_key_release(self, index):
        """Verarbeitet das Loslassen einer Taste.
        
        :param index: Der Index der losgelassenen Taste.
        """
        if self.led_pixels_color_enabled:
            self.neoKey.pixels[index] = self.led_pixel_color[index]  
        else: 
            self.neoKey.pixels[index] = self.led_pixels_color_off
        if self.key_commands[0][index]:
            for command in self.key_commands:
                key = command[index]
                if key:
                    self.macropad.keyboard.release(key)

    def update(self):
        """Aktualisiert den Status der Seitentasten und verarbeitet Ereignisse."""
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

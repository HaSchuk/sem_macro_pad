from config import Config  # Configuration management in a separate file (config.py)
from adafruit_macropad import MacroPad # type: ignore


class MacroPadHandler(MacroPad):  # Erbt von MacroPad
    def __init__(self, main_instance):
        super().__init__()  # Initialisiert MacroPad
        self.display.auto_refresh = False
        self.pixels.auto_write = False
        self.pixels.brightness = Config.MacroPad.led_pixels_color_brightness
        self.main = main_instance
        self.last_pixels_enabled_state = True
        self.app_knob_last_position = None
        self.app_knob_position = 0
        self.led_pixels_color_enabled = Config.MacroPad.led_pixels_color_enabled

    def update_led_state(self):
        """Aktualisiert den Zustand der LEDs auf dem MacroPad."""
        if self.encoder_switch_debounced.pressed:
            self.led_pixels_color_enabled = not self.led_pixels_color_enabled

            if self.led_pixels_color_enabled != self.last_pixels_enabled_state:
                self.last_pixels_enabled_state = self.led_pixels_color_enabled
                self.update_led_colors()

    def update_led_colors(self):
        """Setzt die LED-Farben entsprechend dem aktuellen Modus."""
        color = Config.Globals.led_color_off if not self.led_pixels_color_enabled else None
        for i in range(Config.MacroPad.count_keys):
            self.pixels[i] = color if color else self.main.apps[Config.Globals.app_index].macros[i][0]
        self.pixels.show()

    def handle_encoder_input(self):
        """Verarbeitet Eingaben des Encoders zur App-Umschaltung."""
        self.app_knob_position = self.encoder
        if self.app_knob_position != self.app_knob_last_position:
            app_number = self.app_knob_position % len(self.main.apps)
            self.main._control_interfaces_update_macros(app_number, self.main.sideknobs, self.main.sidekeys)
            self.app_knob_last_position = self.app_knob_position

    def handle_key_events(self):
        """Verarbeitet Tastendruckereignisse und führt zugehörige Makros aus."""
        event = self.keys.events.get()
        if event and event.key_number < len(self.main.apps[Config.Globals.app_index].macros):
            key_number = event.key_number
            sequence = self.main.apps[Config.Globals.app_index].macros[key_number][2]
            if event.pressed:
                self.execute_macro(sequence, key_number, pressed=True)
            else:
                self.execute_macro(sequence, key_number, pressed=False)

    def execute_macro(self, sequence, key_number, pressed):
        """Führt das Makro für eine gegebene Sequenz aus."""
        if pressed:
            self.pixels[key_number] = Config.MacroPad.led_pixels_color_pressed_default
            self.process_macro_sequence(sequence, press=True)
        else:
            self.process_macro_sequence(sequence, press=False)
            self.pixels[key_number] = (self.led_pixels_color_enabled and self.main.apps[Config.Globals.app_index].macros[key_number][0]) or Config.Globals.led_color_off
        self.pixels.show()

    def process_macro_sequence(self, sequence, press):
        """Verarbeitet eine gegebene Makrosequenz, entweder Drücken oder Loslassen."""
        for item in sequence:
            if isinstance(item, int):
                if item >= 0 and press:
                    self.keyboard.press(item)
                elif item < 0 or not press:
                    self.keyboard.release(abs(item))
            elif isinstance(item, dict):
                self.handle_complex_input(item, press)

    def handle_complex_input(self, item, press):
        """Handhabt komplexe Eingabeaktionen wie Mausbewegungen und Tastenkombinationen."""
        if 'buttons' in item and (press or item['buttons'] < 0):
            method = self.mouse.press if press else self.mouse.release
            method(abs(item['buttons']))
        self.mouse.move(item.get('x', 0), item.get('y', 0), item.get('wheel', 0))

    def update(self):
        self.update_led_state()
        self.handle_encoder_input()
        self.handle_key_events()

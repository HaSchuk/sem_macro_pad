from config import Config  # Configuration management in a separate file (config.py)
from adafruit_seesaw import neopixel, rotaryio, digitalio
from adafruit_seesaw import seesaw
import time

class SideKnobHandler:
    """
    Klasse zur Verwaltung eines seitlichen Drehknopfs (Side Knob) am Macropad.
    Diese Klasse initialisiert den Drehknopf, verarbeitet dessen Bewegungen und Knopfdrücke,
    und steuert eine zugehörige NeoPixel LED zur Anzeige des Status.
    """
    
    BUTTON_PIN = 24
    NEOPIXEL_PIN = 6
    DEBOUNCE_DELAY = 100  # Milliseconds for debounce delay

    def __init__(self, main_instance, hw_address, macroIndices):
        """Initialisiert eine neue Instanz der SideKnob-Klasse.
        :param seesaw: Das Seesaw-Objekt für I/O-Operationen.
        :param macroPad: Das Macropad-Objekt für die Steuerung.
        :param Apps: Eine Liste von Anwendungen mit Makros.
        """
        self.main = main_instance
        self.seesaw = seesaw.Seesaw(self.main.i2c_bus, addr=hw_address)
        self.macroindices = macroIndices
        self._initialize_hardware()
        self._initialize_macros()
        self.setMacros(Config.Globals.app_index, self.macroindices)

    def _initialize_hardware(self):
        """Initialisiert die Hardware-Komponenten des Drehknopfs."""
        self.seesaw.pin_mode(self.BUTTON_PIN, self.seesaw.INPUT_PULLUP)
        self.button = digitalio.DigitalIO(self.seesaw, self.BUTTON_PIN)
        self.encoder = rotaryio.IncrementalEncoder(self.seesaw)
        self.pixel = neopixel.NeoPixel(self.seesaw, self.NEOPIXEL_PIN, 1)
        self.pixel.brightness = Config.SideKnob.led_pixels_color_brightness
        self.color = Config.SideKnob.led_pixels_color_default
        self.led_pixels_color_enabled = Config.SideKnob.led_pixels_color_enabled
        self.led_pixels_color_off = Config.Globals.led_color_off
        self.led_pixels_color_pressed_default = Config.SideKnob.led_pixels_color_pressed_default
        self.toggle_knob_led(self.color)
        self.button_down = False
        self.last_position = 0
        self.last_change_time = Config.GlobalFunctions.get_millis()

    def toggle_knob_led(self, color):
        """Schaltet die Led Beleuchtung an oder aus, wenn Sie global deaktiviert ist."""
        if self.led_pixels_color_enabled:
            self.pixel.fill(color)
        else:
            self.pixel.fill(self.led_pixels_color_off)

    def _initialize_macros(self):
        """Initialisiert die Makro-Konfigurationen für den Drehknopf."""
        self.forward_macro = []
        self.reverse_macro = []
        self.button_macro = []
    
    def setMacros(self, app_index, macro_indices=None):
        """Legt die Makros fest, die bei Drehbewegungen und Knopfdrücken ausgeführt werden sollen.
        
        :param app_index: Index der Anwendung in der Apps-Liste, aus der die Makros geladen werden.
        :param macro_indices: Indizes der spezifischen Makros in der Anwendungsmakro-Liste.
        """
        # Wenn kein macro_indices übergeben nehme default
        if macro_indices is None:
            macro_indices = self.macroindices
        # Speichere macro_indices Falls er geändert werden soll
        self.macroindices = macro_indices
        # Stelle sicher, dass die Makro-Indizes innerhalb der Grenzen der Makro-Liste liegen
        app_macros = self.main.apps[app_index].macros
        self.forward_macro = app_macros[self.macroindices[0]][2] if self.macroindices[0] < len(app_macros) else None
        self.reverse_macro = app_macros[self.macroindices[1]][2] if self.macroindices[1] < len(app_macros) else None
        self.button_macro = app_macros[self.macroindices[2]][2] if self.macroindices[2] < len(app_macros) else None
        # Aktualisiere die LED-Farbe basierend auf dem Makro, wenn vorhanden
        self.forward_macro_color = app_macros[self.macroindices[0]][0] if self.forward_macro else None
        self.reverse_macro_color = app_macros[self.macroindices[1]][0] if self.reverse_macro else None
        self.button_macro_color = app_macros[self.macroindices[2]][0] if self.button_macro else None
        # Setze die aktualisierte Farbe
        time.sleep(0.05)  
        self.color = (
            self.forward_macro_color if self.forward_macro else
            self.reverse_macro_color if self.reverse_macro else
            self.button_macro_color if self.button_macro else
            self.color
        )
        self.toggle_knob_led(self.color)

    def _process_encoder_movement(self, position):
        """Verarbeitet die Bewegung des Drehknopfs und führt das zugehörige Makro aus.
        :param position: Die aktuelle Position des Drehknopfs.
        """
        movement = position - self.last_position
        macro_to_process = self.forward_macro if movement > 0 else self.reverse_macro
        if len(macro_to_process) == 2:
            self._execute_macro(macro_to_process)
        else:
            self.main.macropad.keyboard.send(*macro_to_process)
        self.last_position = position

    def _execute_macro(self, macro):
        """Führt ein gegebenes Makro aus.
        
        :param macro: Das auszuführende Makro.
        """
        for action in macro:
            if action == 'Wheel up':
                # Führe eine Scroll-Aktion nach oben aus
                self.main.macropad.mouse.move(wheel=1)
            elif action == 'Wheel down':
                # Führe eine Scroll-Aktion nach unten aus
                self.main.macropad.mouse.move(wheel=-1)
            elif action == 'Mouse right':
                # Bewege die Maus nach rechts
                self.main.macropad.mouse.move(x=10)
            elif action == 'Mouse left':
                # Bewege die Maus nach links
                self.main.macropad.mouse.move(x=-10)
            else:
                # Standard-Verarbeitung für Tastendrücke
                self.main.macropad.keyboard.press(action)
                self.main.macropad.keyboard.release_all()

    def _process_button_press(self):
        """Verarbeitet den Druck auf den Knopf des Drehknopfs."""
        self.main.macropad.keyboard.press(*self.button_macro)
        self.toggle_knob_led(
            self.button_macro_color if self.button_macro_color else
            self.led_pixels_color_pressed_default
        )
        time.sleep(0.05)  
        self.main.macropad.keyboard.release(*self.button_macro)

    def update(self):
        """Aktualisiert den Status des Drehknopfs und verarbeitet Ereignisse."""
        current_position = -self.encoder.position
        if current_position != self.last_position:
            self._process_encoder_movement(current_position)

        if not self.button.value and not self.button_down:
            self.button_down = True
            self._process_button_press()
            self.last_change_time = Config.GlobalFunctions.get_millis()
        elif self.button.value and self.button_down:
            self.button_down = False
            self.last_change_time = Config.GlobalFunctions.get_millis()

        if (Config.GlobalFunctions.get_millis() - self.last_change_time > self.DEBOUNCE_DELAY):
            self.toggle_knob_led(self.color)

from config import Config  # Configuration management in a separate file (config.py)
from adafruit_seesaw import neopixel, rotaryio, digitalio
from rainbowio import colorwheel
import time

class SideKnob:
    """
    Klasse zur Verwaltung eines seitlichen Drehknopfs (Side Knob) am Macropad.
    Diese Klasse initialisiert den Drehknopf, verarbeitet dessen Bewegungen und Knopfdrücke,
    und steuert eine zugehörige NeoPixel LED zur Anzeige des Status.
    """
    
    BUTTON_PIN = 24
    NEOPIXEL_PIN = 6
    DEBOUNCE_DELAY = 100  # Milliseconds for debounce delay

    def __init__(self, seesaw, macroPad, Apps):
        """Initialisiert eine neue Instanz der SideKnob-Klasse.
        :param seesaw: Das Seesaw-Objekt für I/O-Operationen.
        :param macroPad: Das Macropad-Objekt für die Steuerung.
        :param Apps: Eine Liste von Anwendungen mit Makros.
        """
        self.seesaw = seesaw
        self.macropad = macroPad
        self.apps = Apps
        self._initialize_hardware()
        self._initialize_macros()

    def _initialize_hardware(self):
        """Initialisiert die Hardware-Komponenten des Drehknopfs."""
        self.seesaw.pin_mode(SideKnob.BUTTON_PIN, self.seesaw.INPUT_PULLUP)
        self.button = digitalio.DigitalIO(self.seesaw, SideKnob.BUTTON_PIN)
        self.encoder = rotaryio.IncrementalEncoder(self.seesaw)
        self.pixel = neopixel.NeoPixel(self.seesaw, SideKnob.NEOPIXEL_PIN, 1)
        self.pixel.brightness = Config.SideKnob.led_pixels_color_brightness
        self.color = Config.SideKnob.led_pixels_color_default
        self.led_pixels_color_enabled = Config.SideKnob.led_pixels_color_enabled
        self.led_pixels_color_off = Config.Globals.led_color_off
        self.led_pixels_color_pressed = Config.SideKnob.led_pixels_color_pressed
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
    
    def setMacros(self, app_index, macro_indices=[12, 13, 14]):
        """Legt die Makros fest, die bei Drehbewegungen und Knopfdrücken ausgeführt werden sollen.
        
        :param app_index: Index der Anwendung in der Apps-Liste, aus der die Makros geladen werden.
        :param macro_indices: Indizes der spezifischen Makros in der Anwendungsmakro-Liste.
        """
        # Stelle sicher, dass die Makro-Indizes innerhalb der Grenzen der Makro-Liste liegen
        app_macros = self.apps[app_index].macros
        self.forward_macro = app_macros[macro_indices[0]][2] if macro_indices[0] < len(app_macros) else None
        self.reverse_macro = app_macros[macro_indices[1]][2] if macro_indices[1] < len(app_macros) else None
        self.button_macro = app_macros[macro_indices[2]][2] if macro_indices[2] < len(app_macros) else None
        # Aktualisiere die LED-Farbe basierend auf dem Makro, wenn vorhanden
        if self.forward_macro:
            self.color = app_macros[macro_indices[0]][0]  # Verwende die Farbe des Vorwärtsmakros
        elif self.reverse_macro:
            self.color = app_macros[macro_indices[1]][0]  # Alternativ die Farbe des Rückwärtsmakros
        # Setze die aktualisierte Farbe
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
            self.macropad.keyboard.send(*macro_to_process)
        self.last_position = position

    def _execute_macro(self, macro):
        """Führt ein gegebenes Makro aus.
        
        :param macro: Das auszuführende Makro.
        """
        for action in macro:
            if action == 'Wheel up':
                # Führe eine Scroll-Aktion nach oben aus
                self.macropad.mouse.move(wheel=1)
            elif action == 'Wheel down':
                # Führe eine Scroll-Aktion nach unten aus
                self.macropad.mouse.move(wheel=-1)
            elif action == 'Mouse right':
                # Bewege die Maus nach rechts
                self.macropad.mouse.move(x=10)
            elif action == 'Mouse left':
                # Bewege die Maus nach links
                self.macropad.mouse.move(x=-10)
            else:
                # Standard-Verarbeitung für Tastendrücke
                self.macropad.keyboard.press(action)
                self.macropad.keyboard.release_all()

    def _process_button_press(self):
        """Verarbeitet den Druck auf den Knopf des Drehknopfs."""
        self.macropad.keyboard.press(*self.button_macro)
        self.toggle_knob_led(self.led_pixels_color_pressed)
        time.sleep(0.1)  
        self.macropad.keyboard.release(*self.button_macro)


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

        if (Config.GlobalFunctions.get_millis() - self.last_change_time > SideKnob.DEBOUNCE_DELAY):
            self.toggle_knob_led(self.color)
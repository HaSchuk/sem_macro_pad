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
        """
        Initialisiert eine neue Instanz der SideKnobHandler-Klasse.

        :param main_instance: Die Hauptinstanz der Anwendung, die das Macropad und andere Komponenten verwaltet.
        :param hw_address: Die Hardware-Adresse des Seesaw-Objekts auf dem I2C-Bus.
        :param macroIndices: Eine Liste von Indizes, die den Makros entsprechen.
        """
        self.main = main_instance
        self.seesaw = seesaw.Seesaw(self.main.i2c_bus, addr=hw_address)
        self.macroindices = macroIndices
        self._initialize_hardware()
        self._initialize_macros()
        self.set_macros()

    def _initialize_hardware(self):
        """
        Initialisiert die Hardware-Komponenten des Drehknopfs.
        """
        self.seesaw.pin_mode(self.BUTTON_PIN, self.seesaw.INPUT_PULLUP)
        self.button = digitalio.DigitalIO(self.seesaw, self.BUTTON_PIN)
        self.encoder = rotaryio.IncrementalEncoder(self.seesaw)
        self.pixel = neopixel.NeoPixel(self.seesaw, self.NEOPIXEL_PIN, 1)
        self.pixel.brightness = Config.SideKnob.led_pixels_color_brightness
        self.color = Config.SideKnob.led_pixels_color_default
        self.led_pixels_color_default = Config.SideKnob.led_pixels_color_default
        self.led_pixels_color_enabled = Config.SideKnob.led_pixels_color_enabled
        self.led_pixels_color_off = Config.Globals.led_color_off
        self.led_pixels_color_pressed_default = Config.SideKnob.led_pixels_color_pressed_default
        self.toggle_knob_led(self.color)
        self.button_down = False
        self.last_position = 0
        self.last_change_time = Config.GlobalFunctions.get_millis()

    def toggle_knob_led(self, color):
        """
        Schaltet die LED-Beleuchtung an oder aus, basierend auf der globalen Einstellung.

        :param color: Die Farbe, die die LED anzeigen soll.
        """
        if self.led_pixels_color_enabled:
            self.pixel.fill(color)
        else:
            self.pixel.fill(self.led_pixels_color_off)

    def _initialize_macros(self):
        """
        Initialisiert die Makro-Konfigurationen für den Drehknopf.
        """
        self.forward_macro = []
        self.reverse_macro = []
        self.button_macro = []
    
    def set_macros(self):
        """
        Lädt die Makros für die aktuell ausgewählte App und aktualisiert die Makro-Zuweisungen.
        """
        app_macros = self.main.apps[Config.Globals.app_index].macros

        # Funktion zum Extrahieren der Farbe, behandelt explizit `None` als fehlende Farbe
        def extract_color(macro_entry):
            return macro_entry[0] if macro_entry and macro_entry[0] is not None else self.led_pixels_color_default

        if len(app_macros) > self.macroindices[0]:
            self.forward_macro = app_macros[self.macroindices[0]][2]
            self.forward_macro_color = extract_color(app_macros[self.macroindices[0]])
        else:
            self.forward_macro = None
            self.forward_macro_color = self.led_pixels_color_default

        if len(app_macros) > self.macroindices[1]:
            self.reverse_macro = app_macros[self.macroindices[1]][2]
            self.reverse_macro_color = extract_color(app_macros[self.macroindices[1]])
        else:
            self.reverse_macro = None
            self.reverse_macro_color = self.led_pixels_color_default

        if len(app_macros) > self.macroindices[2]:
            self.button_macro = app_macros[self.macroindices[2]][2]
            self.button_macro_color = extract_color(app_macros[self.macroindices[2]])
        else:
            self.button_macro = None
            self.button_macro_color = self.led_pixels_color_pressed_default

        # Verwende die erste gültige Farbe oder fallback zum Default, wenn alle `None` sind
        self.color = (self.forward_macro_color if self.forward_macro_color is not None else
                    self.reverse_macro_color if self.reverse_macro_color is not None else
                    self.button_macro_color if self.button_macro_color is not None else
                    self.led_pixels_color_default)

        time.sleep(0.05)
        self.toggle_knob_led(self.color)


    def _process_encoder_movement(self, position):
        """
        Verarbeitet die Bewegung des Drehknopfs und führt das zugehörige Makro aus.

        :param position: Die aktuelle Position des Drehknopfs.
        """
        movement = position - self.last_position
        if movement != 0:
            # Bestimme die Richtung der Bewegung
            direction = "forward" if movement > 0 else "reverse"
            # Führe das entsprechende Makro aus
            macro_to_process = self.forward_macro if direction == "forward" else self.reverse_macro
            self._execute_macro(macro_to_process)

            # Aktualisiere die Farbe basierend auf der Richtung
            new_color = self.forward_macro_color if direction == "forward" else self.reverse_macro_color
            self.pixel.fill(new_color)
            self.pixel.show()

            self.last_position = position  # Aktualisiere die letzte Position

    def _execute_macro(self, macro):
        """
        Führt ein gegebenes Makro aus.

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
        """
        Verarbeitet den Druck auf den Knopf des Drehknopfs.
        """
        self.main.macropad.keyboard.press(*self.button_macro)
        self.toggle_knob_led(
            self.button_macro_color if self.button_macro_color else
            self.led_pixels_color_pressed_default
        )
        time.sleep(0.03)  
        self.main.macropad.keyboard.release(*self.button_macro)

    def update(self):
        """
        Aktualisiert den Status des Drehknopfs und verarbeitet Ereignisse.
        """
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

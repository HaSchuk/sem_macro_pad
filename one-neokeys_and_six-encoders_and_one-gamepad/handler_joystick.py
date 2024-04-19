import math, time
import sparkfun_qwiicjoystick
from config import Config

class JoyStickHandler:
    """
    Klasse zur Verwaltung eines Joysticks am Macropad.
    
    Diese Klasse liest die Position des Joysticks, berechnet Bewegungen,
    führt entsprechende Aktionen aus und verarbeitet Joystick-Klicks.
    """

    MAX_VALUE = 1023
    MOVEMENT_THRESHOLD = 2
    DEBOUNCE_TIME = 0.1  

    def __init__(self, main_instance, hw_address):
        """Initialisiert eine neue Instanz der JoyStick-Klasse.
        
        :param joystick: Das Joystick-Objekt für die Eingabe.
        :param macroPad: Das Macropad-Objekt für die Aktionen.
        """
        self.main = main_instance
        self.address = hw_address
        self.joystick = sparkfun_qwiicjoystick.Sparkfun_QwiicJoystick(self.main.i2c_bus, hw_address)
        self.initialize_joystick()

    def initialize_joystick(self):
        """Initialisiert die Joystick-Konfiguration und setzt Startwerte."""
        #Letze Positionen JS auf Null setzen
        self.last_x = 0
        self.last_y = 0
        #Initialisiert die Startposition des Joysticks.
        self.start_x = self.MAX_VALUE - self.joystick.horizontal
        self.start_y = self.MAX_VALUE - self.joystick.vertical
        #Mousespeed x/y auf Null setzen
        self.mo_xspeed = None
        self.mo_yspeed = None
        # Initialisiere den Zeitstempel
        self.last_movement_time = time.monotonic()  
        #Initialisiere Button
        self.button_was_pressed = False

    def calculate_relative_position(self, current, start):
        """
        Berechnet die relative Position zum Startpunkt unter Berücksichtigung der Invertierung.
        
        :param current: Aktuelle Position des Joysticks.
        :param start: Startposition des Joysticks.
        :return: Die relative Position.
        """
        return self.MAX_VALUE - current - start

    def calculate_movement_speed(self, relative_position):
        """
        Berechnet die Geschwindigkeit der Bewegung basierend auf der relativen Position.
        
        :param relative_position: Die relative Position des Joysticks.
        :return: Die berechnete Geschwindigkeit der Bewegung.
        """
        if relative_position == 0:
            return 0
        sign = 1 if relative_position > 0 else -1
        relative_position = abs(relative_position)
        speed = math.ceil((5 * math.log(relative_position)) + (relative_position / 20))
        return speed * sign

    def _update_movement(self):
        """
        Verarbeitet die Bewegung des Joysticks und simuliert entsprechende Mausbewegungen.
        """
        current_time = time.monotonic()
        x_rel_pos = self.calculate_relative_position(self.joystick.horizontal, self.start_x)
        y_rel_pos = self.calculate_relative_position(self.joystick.vertical, self.start_y)
        y_rel_pos = -y_rel_pos  # Y-Position invertieren

        # Überprüfen, ob genügend Zeit seit der letzten Bewegung vergangen ist UND
        # die Bewegung groß genug ist
        if (abs(x_rel_pos - self.last_x) > self.MOVEMENT_THRESHOLD or abs(y_rel_pos - self.last_y) > self.MOVEMENT_THRESHOLD) and (current_time - self.last_movement_time > self.DEBOUNCE_TIME):
            mo_xspeed = self.calculate_movement_speed(x_rel_pos)
            mo_yspeed = self.calculate_movement_speed(y_rel_pos)

            self.main.macropad.mouse.press(self.main.macropad.Mouse.MIDDLE_BUTTON)
            self.main.macropad.mouse.move(x=mo_xspeed, y=(-1 * mo_yspeed))
            
            # Aktualisiere die letzte Bewegungszeit und Position
            self.last_movement_time = current_time
            self.last_x = x_rel_pos
            self.last_y = y_rel_pos
        else:
            self.main.macropad.mouse.release(self.main.macropad.Mouse.MIDDLE_BUTTON)

    def _handle_joystick_click(self):
        """Verarbeitet den Joystick-Klick und führt eine Aktion aus, wenn der Button gedrückt wurde."""
        button_pressed = self.joystick.button == 0

        if button_pressed and not self.button_was_pressed:
            # Der Button wurde gerade gedrückt; führe die Aktion aus
            self.main.macropad.mouse.click(self.main.macropad.Mouse.LEFT_BUTTON)

        # Aktualisiere den gespeicherten Zustand für das nächste Update
        self.button_was_pressed = button_pressed

    def update(self):
        """Aktualisiert die Position des Joysticks und führt die entsprechende Aktion aus. 
        Beinhaltet auch die Joystick Klickfunktionalität."""
        self._update_movement()
        self._handle_joystick_click()

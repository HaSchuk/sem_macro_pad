import math
from config import Config

class JoyStick:

    def __init__(self, joyStick, macroPad):
        self.joystick = joyStick
        self.macropad = macroPad

        # letze Positionen JS auf Null setzen
        self.last_x = 0
        self.last_y = 0
        
        # Bestimmung des Nullpunkts x, y JS, Invertierung prüfen
        for i in range(3):
            self.start_x = 1023 - joyStick.horizontal
            self.start_y = 1023 - joyStick.vertical

        # Mousespeed x/y auf Null setzen
        self.mo_xspeed = None
        self.mo_yspeed = None

    def update(self):
        # Joystick auslesen - aktuelle Position absolut, Invertierungen prüfen
        x = 1023 - self.joystick.horizontal
        y = 1023 - self.joystick.vertical

        # relative Position x und y bestimmen, aktuell y invertieren, Code für y prüfen
        x_rel_pos = x - self.start_x
        y_rel_pos = y - self.start_y
        y_rel_pos = -y_rel_pos

        # Bei Bewegung R Vorzeichen auf 1 setzen und Mousespeed R berechnen
        # (ln- und lin-Anteil)
        if x_rel_pos > 0:
            x_rel_pos_h = 1
            mo_xspeed_h = math.ceil(((5 * math.log(x_rel_pos)) + (x_rel_pos / 20)))
            mo_xspeed = mo_xspeed_h * x_rel_pos_h

        # Bei Bewegung L Vorzeichen auf -1 setzen und Mousespeed L berechnen
        # (ln- und lin-Anteil)
        elif x_rel_pos < 0:
            x_rel_pos_h = -1
            # da ln nur mit positiven Zahlen funktioniert, Absoluttwert berechnen
            x_rel_pos = abs(x_rel_pos)
            mo_xspeed_h = math.ceil(((5 * math.log(x_rel_pos)) + (x_rel_pos / 20)))
            mo_xspeed = mo_xspeed_h * x_rel_pos_h  # Wieder in neagtiven Wert umwandeln

        else:
            mo_xspeed = 0  # Keine Bewegung

        if y_rel_pos > 0:  # Bewegung U, Rest siehe Bewegung R
            y_rel_pos_h = 1
            mo_yspeed_h = math.ceil(((5 * math.log(y_rel_pos)) + (y_rel_pos / 20)))
            mo_yspeed = mo_yspeed_h * y_rel_pos_h

        elif y_rel_pos < 0:  # Bewegung D, Rest siehe Bewegung L
            y_rel_pos_h = -1
            y_rel_pos = abs(y_rel_pos)
            mo_yspeed_h = math.ceil(((5 * math.log(y_rel_pos)) + (y_rel_pos / 20)))
            mo_yspeed = mo_yspeed_h * y_rel_pos_h

        else:
            mo_yspeed = 0  # Keine Bewegung

        # Bestimmung, ob sich JS bewegt, Test, ob > 2, 3, ... sinnvoll wäre
        if (abs(x_rel_pos) > 2) or (abs(y_rel_pos) > 2):

            # Position letzte Abfrage festhalten // prüfen, ob weiter gebraucht wird
            last_x = x
            last_y = y
            # Bewegung Maus, durch Code ab Zeile 365 zukünftig abgearbeitet, nur Demo
            self.macropad.mouse.press(self.macropad.Mouse.MIDDLE_BUTTON)
            self.macropad.mouse.move(x=mo_xspeed)
            self.macropad.mouse.move(y=(-1*mo_yspeed))
            # time.sleep(0.1)

        else:
            self.macropad.mouse.release(self.macropad.Mouse.MIDDLE_BUTTON)
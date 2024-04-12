from adafruit_hid.keycode import Keycode
import time

#TODO: Update Macro auf handler Klassen beziehen
#TODO: Switch Encoder Farbe bei Macro Wechsel

class Config:
    class Globals:
        macro_folder = '/macros'
        led_color_off = 0x000000
    class JoyStick:
        test = None
    class SideKeys:
        count_keys = 4 # Anzahl an Keys
        led_pixels_color_default = 0x000580
        led_pixels_color = [0x004000, 0xFF8000, 0x000080, 0x203020]
        led_pixels_color_pressed = 0xFF2000
        led_pixels_color_enabled = True 
        led_pixels_color_brightness = 0.9 #Maxwert 1.0
        #TODO: Wie key_commands erklären?
        key_commands = [
            [None, None, Keycode.CONTROL, Keycode.CONTROL],
            [None, None, Keycode.C, Keycode.V]
        ]
    class SideKnob:
        count_knobs = 6
        led_pixels_color_default = 0x000580 #Wird aus Macro Datei geladen
        led_pixels_color_pressed = 0xFF2000
        led_pixels_color_enabled = True
        led_pixels_color_brightness = 0.2 #Maxwert 1.0
    class MacroPad:
        keypress_tones = [196, 220, 246, 262, 294, 330, 349, 392, 440, 494, 523, 587]

    class GlobalFunctions: 
        @staticmethod
        def get_millis():
            """Gibt die aktuelle Zeit in Millisekunden zurück."""
            return round(time.time() * 1000)
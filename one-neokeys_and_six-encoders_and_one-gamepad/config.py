from adafruit_hid.keycode import Keycode
import time

#TODO: Switch Encoder Farbe bei Macro Wechsel
#TODO: Weitere Elemente Dynamisch bauen!

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
        sideknob_list = [
            ("knob_1L", 0x36, [12, 13, 14]),  # "Name", "HardwareAdresse", "MacroIndices"
            ("knob_1R", 0x37, [15, 16, 17]),
            ("knob_2L", 0x38, [18, 19, 20]),
            ("knob_2R", 0x39, [21, 22, 23]),
            ("knob_3L", 0x3A, [24, 25, 26]),  # 1 = lowest row!
            ("knob_3R", 0x3B, [27, 28, 29])
        ]

    class MacroPad:
        keypress_tones = [196, 220, 246, 262, 294, 330, 349, 392, 440, 494, 523, 587]
    class GlobalFunctions: 
        @staticmethod
        def get_millis():
            """Gibt die aktuelle Zeit in Millisekunden zurück."""
            return round(time.time() * 1000)
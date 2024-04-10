from adafruit_hid.keycode import Keycode
import time

#TODO: Update Macro auf handler Klassen beziehen
#TODO: Switch Encoder Farbe bei Macro Wechsel

# VSCODE Debug Commands
# circuitpython.openSerialMonitor
# circuitpython.selectSerialPort
# circuitpython.closeSerialMonitor

class Config:
    class Globals:
        MACRO_FOLDER = '/macros'
    class JoyStick:
        test = None
    class SideKeys:
        count_keys = 4 # Anzahl an Keys
        led_pixels_color_default = [0x004000, 0x004000, 0x004000, 0x004000] #[0x004000, 0xFF8000, 0x000080, 0x203020]
        led_pixels_color_pressed = 0xFF2000
        led_pixels_color_enabled = True
        #TODO: Wie key_commands erklären?
        key_commands = [
            [None, None, Keycode.CONTROL, Keycode.CONTROL],
            [None, None, Keycode.C, Keycode.V]
        ]
    class SideKnob:
        led_pixels_color_default = [0x000580, 0x000580, 0x000580, 0x000580, 0x000580, 0x000580] #[0x400000, 0x004000, 0xFF2000, 0x000080, 0xFF8000, 0x000580]
        led_pixels_color_enabled = True
        led_pixels_color_brightness = 0.3
    class MacroPad:
        keypress_tones = [196, 220, 246, 262, 294, 330, 349, 392, 440, 494, 523, 587]

    #def initialize_hardware(self):
    
    class GlobalFunctions: 
        def get_millis():
            """Gibt die aktuelle Zeit in Millisekunden zurück."""
            return round(time.time() * 1000)
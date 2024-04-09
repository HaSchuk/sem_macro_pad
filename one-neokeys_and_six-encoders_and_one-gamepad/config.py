
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
    class SideKnob:
        led_pixels_color_default = [0x000580, 0x000580, 0x000580, 0x000580, 0x000580, 0x000580] #[0x400000, 0x004000, 0xFF2000, 0x000080, 0xFF8000, 0x000580]
        led_pixels_color_enabled = True
        led_pixels_color_brightness = 0.3
    class MacroPad:
        keypress_tones = [196, 220, 246, 262, 294, 330, 349, 392, 440, 494, 523, 587]
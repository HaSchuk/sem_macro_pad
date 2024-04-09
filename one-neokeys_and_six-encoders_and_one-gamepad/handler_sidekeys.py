from config import Config # Configuration management in a separate file (config.py)
from adafruit_hid.keycode import Keycode


class SideKeys:

    def __init__(self, neoKey, macroPad):
        self.neoKey = neoKey
        self.count_keys = Config.SideKeys.count_keys
        self.key_commands = [[None, None, Keycode.CONTROL, Keycode.CONTROL], [None, None, Keycode.C, Keycode.V]]
        self.debounce_states = [False, False, False, False]
        self.pressed_index = -1
        self.last_pins = 0b11110000
        self.macropad = macroPad
        self.led_pixel_color = Config.SideKeys.led_pixels_color_default
        self.pixels_enabled = Config.SideKeys.led_pixels_color_enabled
        self.pressed_color = Config.SideKeys.led_pixels_color_pressed  # Color of all Sidekey if pressed

        self.setAllPixels(self.led_pixel_color)  # call setAllPixels definition >> acces to Sidecolor list

    def setAllPixels(self, color):
        for i in range(len(color)):
            self.neoKey.pixels[i] = color[i]

    def __parsePins(self, pins):
        return [not pins & 0b00010000, not pins & 0b00100000, not pins & 0b01000000, not pins & 0b10000000]

    def update(self):
        pins = self.neoKey.digital_read_bulk(0b11110000)

        if pins == self.last_pins:
            return

        self.last_pins = pins
        keyStates = self.__parsePins(pins)

        for i in range(self.count_keys):
            if keyStates[i] and not self.debounce_states[i]:
                self.neoKey.pixels[i] = self.pressed_color
                self.debounce_states[i] = True
                if self.key_commands[0][i]:
                    for j in range(2):
                        self.macropad.keyboard.press(self.key_commands[j][i])
                self.pressed_index = i
                continue

            elif not keyStates[i] and self.debounce_states[i]:
                self.neoKey.pixels[i] = self.led_pixel_color[i] if self.pixels_enabled else 0x0
                self.debounce_states[i] = False
                if self.key_commands[0][i]:
                   for j in range(2):
                        self.macropad.keyboard.release(self.key_commands[j][i])
                self.pressed_index = -1
                continue
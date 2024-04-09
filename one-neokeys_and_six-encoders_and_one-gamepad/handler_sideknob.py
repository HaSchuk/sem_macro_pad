from config import Config # Configuration management in a separate file (config.py)
from adafruit_seesaw import neopixel, rotaryio, digitalio
from rainbowio import colorwheel
import time

class SideKnob:

    col_SKn_c = 0 # Neokey counter for LED colors

    def __init__(self, seesaw, macroPad, Apps):
        self.seesaw = seesaw
        self.macropad = macroPad
        self.apps = Apps

        seesaw.pin_mode(24, seesaw.INPUT_PULLUP)

        self.button = digitalio.DigitalIO(seesaw, 24)
        self.button_down = False

        self.encoder = rotaryio.IncrementalEncoder(seesaw)
        self.last_position = 0

        self.pixel = neopixel.NeoPixel(seesaw, 6, 1)
        self.pixel.brightness = Config.SideKnob.led_pixels_color_brightness
        self.led_pixel_color = Config.SideKnob.led_pixels_color_default
        self.pixels_enabled = Config.SideKnob.led_pixels_color_enabled
        self.pixels_enabled_override = False

        self.last_change_time = self.__get_millis() 
        self.pixel.fill(self.led_pixel_color[SideKnob.col_SKn_c])  # change for defined hex val color needed, no rainbow
        SideKnob.col_SKn_c = SideKnob.col_SKn_c + 1

        self.forward_macro = []
        self.reverse_macro = []
        self.button_macro = []
    
    def setMacros(self, app_index, macro_indicies=[12, 13, 14]):
        self.forward_macro = self.apps[app_index].macros[macro_indicies[0]][2]
        self.reverse_macro = self.apps[app_index].macros[macro_indicies[1]][2]
        self.button_macro = self.apps[app_index].macros[macro_indicies[2]][2]

    def __get_millis(self):
        return round(time.time() * 1000)

    def update(self):

        while True:
            position = -self.encoder.position
            if position != self.last_position:
                print("Position: {}".format(position))
                if position > self.last_position:  # Advance forward through the colorwheel.
                    self.color += 10
                    print(len(self.forward_macro))
                    if len(self.forward_macro) == 2:
                        if self.forward_macro[1] == 'Wheel up':
                            self.macropad.keyboard.press(self.forward_macro[0])
                            self.macropad.mouse.move(wheel = +1)
                            time.sleep(0.2)
                            self.macropad.keyboard.release(self.forward_macro[0])
                        elif self.forward_macro[1] == 'Wheel down':
                            self.macropad.keyboard.press(self.forward_macro[0])
                            self.macropad.mouse.move(wheel = -1)
                            time.sleep(0.2)
                            self.macropad.keyboard.release(self.forward_macro[0])
                        if self.forward_macro[1] == 'Mouse right':
                            self.macropad.mouse.press(self.macropad.Mouse.RIGHT_BUTTON)
                            self.macropad.mouse.move(x= +50)
                            time.sleep(0.3)
                            self.macropad.mouse.release(self.macropad.Mouse.RIGHT_BUTTON)
                            self.macropad.mouse.move(x= -50)
                        elif self.forward_macro[1] == 'Mouse left':
                            self.macropad.mouse.press(self.macropad.Mouse.RIGHT_BUTTON)
                            self.macropad.mouse.move(x = -50)
                            time.sleep(0.3)
                            self.macropad.mouse.release(self.macropad.Mouse.RIGHT_BUTTON)
                        else:
                            self.macropad.keyboard.send(self.forward_macro[0])
                            time.sleep(1.5)
                            self.macropad.keyboard.send(self.forward_macro[1])
                            time.sleep(1.5)
                            self.macropad.keyboard.send(self.forward_macro[1])
                    else:
                        self.macropad.keyboard.send(*self.forward_macro)
                else:
                    self.color -= 10  # Advance backward through the colorwheel.
                    print(len(self.reverse_macro))
                    if len(self.reverse_macro) == 2:
                        if self.reverse_macro[1] == 'Wheel up':
                            self.macropad.keyboard.press(self.reverse_macro[0])
                            self.macropad.mouse.move(wheel = +1)
                            time.sleep(0.2)
                            self.macropad.keyboard.release(self.reverse_macro[0])
                        elif self.reverse_macro[1] == 'Wheel down':
                            self.macropad.keyboard.press(self.reverse_macro[0])
                            self.macropad.mouse.move(wheel = -1)
                            time.sleep(0.2)
                            self.macropad.keyboard.release(self.reverse_macro[0])
                        if self.reverse_macro[1] == 'Mouse right':
                            self.macropad.mouse.move(x = +50)
                            time.sleep(0.3)
                            self.macropad.mouse.release(self.macropad.Mouse.RIGHT_BUTTON)
                        elif self.reverse_macro[1] == 'Mouse left':
                            self.macropad.mouse.press(self.macropad.Mouse.RIGHT_BUTTON)
                            self.macropad.mouse.move(x = -50)
                            time.sleep(0.3)
                            self.macropad.mouse.release(self.macropad.Mouse.RIGHT_BUTTON)
                            self.macropad.mouse.move(x = +50)
                        else:
                            self.macropad.keyboard.send(self.reverse_macro[0])
                            time.sleep(1.5)
                            self.macropad.keyboard.send(self.reverse_macro[1])
                            time.sleep(1.5)
                            self.macropad.keyboard.send(self.reverse_macro[1])
                    else:
                        self.macropad.keyboard.send(*self.reverse_macro)


                self.last_change_time = self.__get_millis()

            self.last_position = position

            if not self.button.value and not self.button_down:
                self.button_down = True
                self.macropad.keyboard.press(*self.button_macro)
                self.pixel.fill(colorwheel(self.color))
                self.pixels_enabled_override = True
                self.last_change_time = self.__get_millis()

            elif self.button.value and self.button_down:
                self.button_down = False
                self.macropad.keyboard.release(*self.button_macro)
                self.pixels_enabled_override = False
                self.last_change_time = self.__get_millis()

            if (self.__get_millis() - self.last_change_time > 100):
                if not self.pixels_enabled and not self.pixels_enabled_override:
                    self.pixel.fill(0x000000)
                return
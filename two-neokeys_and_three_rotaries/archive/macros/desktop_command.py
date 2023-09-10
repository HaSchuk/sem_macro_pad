# MACROPAD Hotkeys example: Adobe Photoshop for Windows

from adafruit_hid.keycode import Keycode # REQUIRED if using Keycode.* values

app = {                       # REQUIRED dict, must be named 'app'
    'name' : 'Desktop Command', # Application name
    'macros' : [              # List of button macros...
        # COLOR    LABEL    KEY SEQUENCE
        # 1st row ----------
        (0x004000, 'Cursor', [Keycode.CONTROL, Keycode.SHIFT, '2']),               # Epic Pen
        (0xBA000F, 'Speakers', [Keycode.CONTROL, Keycode.ALT, Keycode.F9]),        # Sound Switch
        (0x000040, 'Hold', [Keycode.CONTROL, Keycode.ALT, Keycode.SHIFT, '1']),    # OBS
        # 2nd row ----------
        (0x004000, 'Pen', [Keycode.CONTROL, Keycode.SHIFT, '3']),                  # Epic Pen
        (0xBA000F, 'Headset', [Keycode.CONTROL, Keycode.ALT, Keycode.F10]),        # Sound Switch
        (0x000040, 'Shelf', [Keycode.CONTROL, Keycode.ALT, Keycode.SHIFT, '2']),   # OBS
        # 3rd row ----------
        (0x004000, 'Eraser', [Keycode.CONTROL, Keycode.SHIFT, '5']),               # Epic Pen
        (0xBA000F, 'Oculus', [Keycode.CONTROL, Keycode.ALT, Keycode.F11]),         # Sound Switch
        (0x000040, 'Desktop', [Keycode.CONTROL, Keycode.ALT, Keycode.SHIFT, '3']), # OBS
        # 4th row ----------
        (0x004000, 'Clear', [Keycode.CONTROL, Keycode.SHIFT, '7']),                # Epic Pen
        (0xBA000F, 'Cycle', [Keycode.CONTROL, Keycode.ALT, Keycode.F12]),          # Sound Switch
        (0x000040, 'BLEEP', [Keycode.CONTROL, Keycode.ALT, Keycode.SHIFT, '4']),   # OBS
        # Encoder button ---
        (0x000000, '', [Keycode.CONTROL, Keycode.ALT, 'S']) # Save for web
    ]
}

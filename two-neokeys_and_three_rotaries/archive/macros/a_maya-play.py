# MACROPAD Hotkeys example: Adobe Photoshop for Windows

from adafruit_hid.keycode import Keycode # REQUIRED if using Keycode.* values

app = {                       # REQUIRED dict, must be named 'app'
    'name' : 'Maya Play', # Application name
    'macros' : [              # List of button macros...
        # COLOR    LABEL    KEY SEQUENCE
        # 1st row ----------
        (0x004000, '<-step', [Keycode.ALT, ',']),
        (0x000040, 'key->', '.'),
        (0x004000, 'step->', [Keycode.ALT, '.']),   # Cycle brush modes
        # 2nd row ----------
        (0xBA000F, 'Frame-0', [Keycode.ALT, '/']),
        (0x000040, '<-key', ','),
        (0xBA000F, 'play', [Keycode.ALT, 'v']),  # Cycle eraser modes
        # 3rd row ----------
        (0x101010, 'Swap', 'x'),    # Swap foreground/background colors
        (0x101010, 'Move', 'v'),    # Move layer
        (0x101010, 'Fill', 'G'),    # Cycle fill/gradient modes
        # 4th row ----------
        (0x101010, 'Eyedrop', 'I'), # Cycle eyedropper/measure modes
        (0x101010, 'Wand', 'W'),    # Cycle "magic wand" (selection) modes
        (0x101010, 'Heal', 'J'),    # Cycle "healing" modes
        # Encoder button ---
        (0x000000, '', [Keycode.CONTROL, Keycode.ALT, 'S']) # Save for web
    ]
}

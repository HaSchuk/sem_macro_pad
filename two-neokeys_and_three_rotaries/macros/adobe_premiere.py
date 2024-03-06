# MACROPAD Hotkeys example: Adobe Photoshop for Windows

from adafruit_hid.keycode import Keycode # REQUIRED if using Keycode.* values

app = {                       # REQUIRED dict, must be named 'app'
    'name' : 'Adobe Premiere', # Application name
    'enter_macro' : [],
    'exit_macro' : [],
    'macros' : [              # List of button macros...
        # COLOR    LABEL    KEY SEQUENCE
        # 1st row ----------
        (0xFF2000, 'A', [Keycode.A]),
        (0xFF2000, 'Marker', [Keycode.M]),
        (0xFF2000, 'V', [Keycode.V]),
        # 2nd row ----------
        (0x00FFFF, 'In', [Keycode.I]),
        (0x00FFFF, 'Mark', [Keycode.X]),
        (0x00FFFF, 'Out', [Keycode.O]),
        # 3rd row ----------
        (0xFF2000, 'Trim L', [Keycode.Q]),
        (0xFF2000, 'Select', [Keycode.D]),
        (0xFF2000, 'Trim R', [Keycode.W]),
        # 4th row ----------
        (0x00FFFF, '<-', [Keycode.J]),
        (0x00FFFF, 'stop', [Keycode.K]),
        (0x00FFFF, '->', [Keycode.L]),
        # L-Upper Encoder ---
        (0x000000, '', [Keycode.EQUALS ]), # Save for web
        (0x000000, '', [Keycode.MINUS ]), # Save for web
        # L-Middle Encoder ---
        (0x000000, '', [Keycode.DOWN_ARROW]), # Save for web
        (0x000000, '', [Keycode.UP_ARROW]), # Save for web
        # L-lower Encoder ---
        (0x000000, '', [Keycode.RIGHT_ARROW]), # Save for web
        (0x000000, '', [Keycode.LEFT_ARROW]), # Save for web
        # R-Upper Encoder ---
        (0x000000, '', [Keycode.EQUALS ]), # Save for web
        (0x000000, '', [Keycode.MINUS ]), # Save for web
        # R-Middle Encoder ---
        (0x000000, '', [Keycode.DOWN_ARROW]), # Save for web
        (0x000000, '', [Keycode.UP_ARROW]), # Save for web
        # R-lower Encoder ---
        (0x000000, '', [Keycode.RIGHT_ARROW]), # Save for web
        (0x000000, '', [Keycode.LEFT_ARROW]), # Save for web
        # U/D Joystick
        (0x000000, '', [mo_ypeed]), # Joy = Mouse Up/Down
        # L/R Joystick ---
        (0x000000, '', [mo_xspeed]), # Joy = Mouse Left/Right

    ]
}

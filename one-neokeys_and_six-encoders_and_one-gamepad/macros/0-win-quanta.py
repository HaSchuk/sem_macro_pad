# SPDX-FileCopyrightText: 2024 Harald  Schukow , Competenza GmbH
#
# SPDX-License-Identifier: MIT

# MACROPAD Hotkeys example: Quanta Software Shortcuts

from adafruit_hid.keycode import Keycode # REQUIRED if using Keycode.* values

app = {                       # REQUIRED dict, must be named 'app'
    'name' : 'Quanta', # Application name
    'enter_macro' : [],
    'exit_macro' : [],
    'macros' : [              # List of button macros...
        # COLOR    LABEL    KEY SEQUENCE
        # 1st row ----------
        (0xFFFFFF, 'PhaB', [Keycode.F2]), # starts Photo with active beam
        (0x004000, 'S/Qm', [Keycode.F5]), # toggles Single / Quad Image mode
        (0x400000, 'Scan', [Keycode.F6]),      # pauses / releases scanning
        # 2nd row ----------
        (0x202000, 'Red+/-', [Keycode.F7]), # toggles Reduced On / Off
        (0x6600CC, 'ACB', [Keycode.F9]), #starts Auto Contrast and Brightness procedure
        (0x336600, 'LinkZ', [Keycode.SHIFT, Keycode.F9]), #starts Link Z
        # 3rd row ----------
        (0x008080, 'AF', [Keycode.F11]), # AF procedure
        (0x800000, 'Stigm', [Keycode.CONTROL, Keycode.F11]), # Auto Stigmator correction procedure
        (0xFF8000, 'Spot', [Keycode.CONTROL, 'k']), # Spot mode conditions
        # 4th row ----------
        (0x800080, 'ScaCon', [Keycode.CONTROL, 'm']), # Full frame scanning conditions
        (0x202020, 'SaveI', [Keycode.CONTROL, 's']), # saves image
        (0x000080, 'LPos', [Keycode.CONTROL, 'z']), # moves stage to the last position
        # 1L Encoder --- RED
        (0xFF0000, '', [Keycode.SHIFT, 'Wheel up']),  # Magn fine up
        (0xFF0000, '', [Keycode.SHIFT, 'Wheel down']),  # Magn fine down
        (0xFF0000, '', []), # button, not used
        # 1R Encoder --- GREEN
        (0x00FF00, '', [Keycode.CONTROL, 'Mouse right']), # Focus up
        (0x00FF00, '', [Keycode.CONTROL, 'Mouse left']),  # Focus down
        (0x00FF00, '', []),  # button, not used
        # 2L Encoder --- BLUE
        (0x0000FF, '', [Keycode.CONTROL, 'Wheel up']),  # Magn coarse up
        (0x0000FF, '', [Keycode.CONTROL, 'Wheel down']),  # Magn coarse down
        (0x0000FF, '', []),  # button, not used
        # 2R Encoder --- YELLOW
        (0xFFFF00, '', [Keycode.RIGHT_ARROW, Keycode.RIGHT_ARROW]),  # 240% IMA right
        (0xFFFF00, '', [Keycode.LEFT_ARROW, Keycode.LEFT_ARROW]),   # 240% IMA left
        (0xFFFF00, '', []),  # button, not used
        # 3L Encoder --- MAGENTA
        (0xFF00FF, '', [Keycode.KEYPAD_MINUS]),  # Magn x2 up
        (0xFF00FF, '', [Keycode.KEYPAD_PLUS]),   # Magn x2 down
        (0xFF00FF, '', []),   # button, not used
        # 3R Encoder --- Cyan
        (0x00FFFF, '', [Keycode.UP_ARROW, Keycode.UP_ARROW]),  # 240% IMA up
        (0x00FFFF, '', [Keycode.DOWN_ARROW, Keycode.DOWN_ARROW]),  # 240% IMA down
        (0x00FFFF, '', []),  # button, not used

    ]
}

# SPDX-FileCopyrightText: 2024 Harald  Schukow , Competenza GmbH
#
# SPDX-License-Identifier: MIT

# MACROPAD Hotkeys example: Quanta Software Shortcuts

from adafruit_hid.keycode import Keycode # REQUIRED if using Keycode.* values

app = {                       # REQUIRED dict, must be named 'app'
    'name' : 'Quanta', # Application name
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
 
        # Encoder button ---
        (0x000000, '', [Keycode.ESCAPE]) # ESC
    ]
}

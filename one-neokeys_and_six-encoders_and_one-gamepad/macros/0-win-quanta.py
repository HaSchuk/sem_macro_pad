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

        # MacroPad
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

        # Enoder
        # 1L Encoder ---
        (0x004000, '', [Keycode.SHIFT, 'Wheel up']),  # Magn fine up, 'Wheel up' as trigger key for special handling
        (0x004000, '', [Keycode.SHIFT, 'Wheel down']),  # Magn fine down, 'Wheel down' as trigger key for special handling
        (0x004000, '', []), # button, not used
        # 1R Encoder ---
        (0x400000, '', [Keycode.CONTROL, 'Mouse right']), # Focus up, 'Mouse right' as trigger key for special handling
        (0x400000, '', [Keycode.CONTROL, 'Mouse left']),  # Focus down, 'Mouse left' as trigger key for special handling
        (0x400000, '', []),  # button, not used
        # 2L Encoder ---
        (0x004100, '', [Keycode.CONTROL, 'Wheel up']),  # Magn coarse up, 'Wheel up' as trigger key for special handling
        (0x004100, '', [Keycode.CONTROL, 'Wheel down']),  # Magn coarse down, 'Wheel down' as trigger key for special handling
        (0x004100, '', []),  # button, not used
        # 2R Encoder ---
        (0x4169E1, '', [Keycode.RIGHT_ARROW, Keycode.RIGHT_ARROW, Keycode.RIGHT_ARROW]),  # 240% IMA right
        (0x4169E1, '', [Keycode.LEFT_ARROW, Keycode.LEFT_ARROW, Keycode.LEFT_ARROW]),   # 240% IMA left
        (0x4169E1, '', []),  # button, not used
        # 3L Encoder ---
        (0x004200, '', [Keycode.KEYPAD_MINUS]),  # Magn x2 up
        (0x004200, '', [Keycode.KEYPAD_PLUS]),   # Magn x2 down
        (0x004200, '', []),   # button, not used
        # 3R Encoder ---
        (0x4165E1, '', [Keycode.UP_ARROW, Keycode.UP_ARROW, Keycode.UP_ARROW]),  # 240% IMA up
        (0x4165E1, '', [Keycode.DOWN_ARROW, Keycode.DOWN_ARROW, Keycode.DOWN_ARROW]),  # 240% IMA down
        (0x4165E1, '', []),  # button, not used

        # NeoKey1x4 1
        # Key1
        (0x004000, '', ['AppSwitch_0']), # switching to Quanta key assignment, 'Appswitcher1' as trigger key for special handling
        # Key2
        (0xFF8000, '', ['AppSwitch_1']), # sitching to LISA key assignment, 'Appswitcher2' as trigger key for special handling
        # Key3
        (0x000080, '', [Keycode.CONTROL, Keycode.C]),      # Copy
        # Key4
        (0x203020, '', [Keycode.CONTROL, Keycode.V]),      # Paste
    ]
}

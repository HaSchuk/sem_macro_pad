# SPDX-FileCopyrightText: 2024 Harald  Schukow , Competenza GmbH
#
# SPDX-License-Identifier: MIT

# MACROPAD Hotkeys example: Quanta Software Shortcuts

from adafruit_hid.keycode import Keycode # REQUIRED if using Keycode.* values

app = {                       # REQUIRED dict, must be named 'app'
    'name' : 'Lisa.LIMS', # Application name
    'macros' : [              # List of button macros...
        # COLOR    LABEL    KEY SEQUENCE
        # 1st row ----------
        (0x202000, 'S copy', [Keycode.F2]), # Satz kopieren
        (0x400000, 'S ins', [Keycode.F6]), # Satz einfügen
        (0x004000, 'S del', [Keycode.SHIFT, Keycode.F6]),      # Satz löschen
        # 2nd row ----------
        (0xFFFFEE, 'Save', [Keycode.F10]), # Satz speichern
        (0x6600CC, 'Frei', [Keycode.ALT, 'f']), # Freigabe
        (0x000080, 'Report', [Keycode.CONTROL, Keycode.F12]), # Report auswahlen
        # 3rd row ----------
        (0x008080, 'Suche', [Keycode.F7]), # Suche
        (0x800000, 'Ausw', [Keycode.F9]), # Feldauswahl
        (0xFF8000, 'Spot', [Keycode.F12]), # Reload
        # 4th row ----------
        (0x800080, 'Copy', [Keycode.CONTROL, 'c']), # Kopieren
        (0x000000, 'All', [Keycode.CONTROL, 'a']), # alles markieren
        (0x336600, 'Ins', [Keycode.CONTROL, 'v']), # Einfügen

        # Encoder button ---
        (0x000000, '', [Keycode.ENTER]) # ESC
    ]
}

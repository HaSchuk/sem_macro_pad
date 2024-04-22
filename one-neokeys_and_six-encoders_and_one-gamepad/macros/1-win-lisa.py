# SPDX-FileCopyrightText: 2024 Harald  Schukow , Competenza GmbH
#
# SPDX-License-Identifier: MIT

# MACROPAD Hotkeys example: Quanta Software Shortcuts

from adafruit_hid.keycode import Keycode # type: ignore # REQUIRED if using Keycode.* values

app = {                       # REQUIRED dict, must be named 'app'
    'name' : 'Lisa.LIMS', # Application name
    'enter_macro' : [],
    'exit_macro' : [],
    'macros' : [              # List of button macros...
        # COLOR    LABEL    KEY SEQUENCE
        
        # MacroPad
        # 1st row ----------
        (0x202000, 'S kopi', [Keycode.F2]),  # Satz kopieren
        (0x400000, 'S einf', [Keycode.F6]),  # Satz einfügen
        (0x004000, 'S lösc', [Keycode.SHIFT, Keycode.F6]),      # Satz löschen
        # 2nd row ----------
        (0xFFFFEE, 'Speic', [Keycode.F10]),  # Satz speichern
        (0x6600CC, 'Freig', [Keycode.ALT, 'f']),  # Freigabe
        (0x000080, 'Report', [Keycode.CONTROL, Keycode.F12]),  # Report auswahlen
        # 3rd row ----------
        (0x008080, 'Suche', [Keycode.F7]),  # Suche
        (0x800000, 'Ausw', [Keycode.F9]),  # Feldauswahl
        (0xFF8000, 'S Aktu', [Keycode.F12]),  # Satz aktualisieren
        # 4th row ----------
        (0x800080, 'M All', [Keycode.CONTROL, 'a']),  # Kopieren
        (0x000000, 'Persp', [Keycode.CONTROL, Keycode.F10]),  # verfügbare Perspektiven
        (0x336600, 'Detai', [Keycode.CONTROL, Keycode.F11]),  # Details in Perspektiven
        
        # Enoder
        # 1L Encoder ---
        (0x000000, '', []),  # not used
        (0x000000, '', []),  # not used
        (0x000000, '', []),  # not used
        # 1R Encoder ---
        (0x000000, '', []),  # not used
        (0x000000, '', []),  # not used
        (0x000000, '', []),  # not used
        # 2L Encoder ---
        (0x000000, '', []),  # not used
        (0x000000, '', []),  # not used
        (0x000000, '', []),  # not used
        # 2R Encoder ---
        (0x000000, '', []),  # not used
        (0x000000, '', []),  # not used
        (0x000000, '', []),  # not used
        # 3L Encoder ---
        (0x000000, '', []),  # not used
        (0x000000, '', []),  # not used
        (0x000000, '', []),  # not used
        # 3R Encoder ---
        (0x000000, '', []),  # not used
        (0x000000, '', []),  # not used
        (0x000000, '', []),  # not used

        # NeoKey1x4 1
        # Key1
        (0x004000, '', ['AppSwitch_0']), # switching to Quanta key assignment, 'Appswitcher1' as trigger key for special handling
        # Key2
        (0xFF8000, '', ['AppSwitch_1']), # sitching to LISA key assignment, 'Appswitcher2' as trigger key for special handling
        # Key3
        (0x000080, '', [Keycode.CONTROL, Keycode.C]),      # Copy 
        # Key4
        (0x203020, '', [Keycode.CONTROL, Keycode.V]),      #Paste 
    ]
}

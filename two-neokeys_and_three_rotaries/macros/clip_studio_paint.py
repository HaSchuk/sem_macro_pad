# MACROPAD Hotkeys example: Adobe Photoshop for Windows

from adafruit_hid.keycode import Keycode # REQUIRED if using Keycode.* values

app = {                       # REQUIRED dict, must be named 'app'
    'name' : 'Clip Studio Paint', # Application name
    'enter_macro' : [],
    'exit_macro' : [],
    'macros' : [              # List of button macros...
        # COLOR    LABEL    KEY SEQUENCE
        # 1st row ----------
        (0xFEF200, 'LVis', [Keycode.CONTROL, Keycode.BACKSLASH]),      
        (0x800078, 'lyr up', [Keycode.ALT, Keycode.RIGHT_BRACKET]),         
        (0xFF2000, 'redo', [Keycode.CONTROL, Keycode.Y]),     
        # 2nd row ----------
        (0xFEF200, 'lockT', [Keycode.BACKSLASH]),    
        (0x800078, 'lyr dn', [Keycode.ALT, Keycode.LEFT_BRACKET]),       
        (0xFF2000, 'undo', [Keycode.CONTROL, Keycode.Z]),
        # 3rd row ----------
        (0x004000, 'sel', [Keycode.M]),
        (0x004000, 'blend', [Keycode.J]),
        (0x004000, 'erase', [Keycode.E]),
        # 4th row ----------
        (0x00FFFF, 'pencil', [Keycode.P]),
        (0x00FFFF, 'pen', [Keycode.I]),
        (0x00FFFF, 'brush', [Keycode.B]),
        # Upper Encoder ---
        (0x000000, '', [Keycode.RIGHT_BRACKET]), #brush up
        (0x000000, '', [Keycode.LEFT_BRACKET]),  #brush down
        (0x000000, '', [Keycode.CONTROL, Keycode.ALT, Keycode.SHIFT, Keycode.ZERO]), #view reset all
        # Middle Encoder ---
        (0x000000, '', [Keycode.EQUALS]),          #view rotate right
        (0x000000, '', [Keycode.MINUS]),           #view rotate left
        (0x000000, '', [Keycode.ALT, Keycode.H]),  #view mirror
        # lower Encoder ---
        (0x000000, '', [Keycode.CONTROL, Keycode.EQUALS]), #view zoom in
        (0x000000, '', [Keycode.CONTROL, Keycode.MINUS]),  #view zoom out
        (0x000000, '', [Keycode.SPACE ]),   #view pan
    ]
}

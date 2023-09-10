# MACROPAD Hotkeys example: Adobe Photoshop for Windows

from adafruit_hid.keycode import Keycode # REQUIRED if using Keycode.* values

app = {                       # REQUIRED dict, must be named 'app'
    'name' : 'Adobe Photoshop', # Application name
    'enter_macro' : [],
    'exit_macro' : [],
    'macros' : [              # List of button macros...
        # COLOR    LABEL    KEY SEQUENCE
        # 1st row ----------
        (0x00FFFF, 'Flip H', [Keycode.CONTROL, Keycode.ALT, Keycode.H]),      
        (0xFF2000, 'LockT', [Keycode.FORWARD_SLASH]),         
        (0x00FFFF, 'PolyL', [Keycode.K]),    
        # 2nd row ----------
        (0x00FFFF, 'P', [Keycode.P]),    
        (0x800078, 'D', [Keycode.D]),       
        (0x00FFFF, 'Lasso', [Keycode.L]),
        # 3rd row ----------
        (0x00FFFF, 'R', [Keycode.R]),
        (0x800078, 'E', [Keycode.E]),
        (0x00FFFF, 'Redo', [Keycode.CONTROL, Keycode.SHIFT, Keycode.Z]),
        # 4th row ----------
        (0x00FFFF, 'spacebar', [Keycode.SPACEBAR]),
        (0xFF2000, 'Brush', [Keycode.B]),
        (0x00FFFF, 'Undo', [Keycode.CONTROL, Keycode.Z]),
        # Upper Encoder ---
        (0x000000, '', [Keycode.CONTROL, Keycode.EQUALS]),
        (0x000000, '', [Keycode.CONTROL, Keycode.MINUS]), 
        (0x000000, '', [Keycode.BACKSPACE]),  
        # Middle Encoder ---
        (0x000000, '', [Keycode.SHIFT, Keycode.RIGHT_BRACKET]), 
        (0x000000, '', [Keycode.SHIFT, Keycode.LEFT_BRACKET]), 
        (0x000000, '', [Keycode.ESCAPE]), 
        # lower Encoder ---
        (0x000000, '', [Keycode.RIGHT_BRACKET]), 
        (0x000000, '', [Keycode.LEFT_BRACKET]), 
        (0x000000, '', [Keycode.CONTROL, Keycode.ZERO]), 
    ]
}

# MACROPAD Hotkeys example: Adobe Photoshop for Windows

from adafruit_hid.keycode import Keycode # REQUIRED if using Keycode.* values

app = {                       # REQUIRED dict, must be named 'app'
    'name' : 'Epic Pen', # Application name
    'enter_macro' : [Keycode.CONTROL, Keycode.SHIFT, Keycode.F17],
    'exit_macro' : [],
    'macros' : [              # List of button macros...
        # COLOR    LABEL    KEY SEQUENCE
        # 1st row ----------
        (0x004000, 'Cursor', [Keycode.CONTROL, Keycode.SHIFT, '2']),               
        (0xFF9900, 'ScreenShot', [Keycode.CONTROL, Keycode.SHIFT, Keycode.PRINT_SCREEN]),        
        (0x00ADEF, 'Blue', [Keycode.ALT, Keycode.SHIFT, '1']),              
        # 2nd row ----------
        (0x004000, 'Pen', [Keycode.CONTROL, Keycode.SHIFT, '3']),                 
        (0xFF9900, 'Highlight', [Keycode.CONTROL, Keycode.SHIFT, '4']),      
        (0xFEF200, 'Yellow', [Keycode.ALT, Keycode.SHIFT, '2']),              
        # 3rd row ----------
        (0x004000, 'Eraser', [Keycode.CONTROL, Keycode.SHIFT, '5']),            
        (0xFF9900, 'Line', [Keycode.CONTROL, Keycode.ALT, Keycode.SHIFT, 'l']),        
        (0xFF0B88, 'Pink', [Keycode.ALT, Keycode.SHIFT, '3']),             
        # 4th row ----------
        (0x004000, 'Clear', [Keycode.CONTROL, Keycode.SHIFT, '7']),              
        (0xFF9900, 'Text', [Keycode.CONTROL, Keycode.SHIFT, 't']),         
        (0x87837F, 'Black', [Keycode.ALT, Keycode.SHIFT, '4']),            
        # Encoder button ---
        # Upper Encoder ---
        (0x000000, '', [Keycode.CONTROL, Keycode.SHIFT, Keycode.RIGHT_BRACKET]), # stroke size
        (0x000000, '', [Keycode.CONTROL, Keycode.SHIFT, Keycode.LEFT_BRACKET]), # stroke size
        (0x000000, '', [Keycode.HOME]), # Save for web
        # Middle Encoder ---
        (0x000000, '', [Keycode.RIGHT_ARROW]), # Save for web
        (0x000000, '', [Keycode.LEFT_ARROW]), # Save for web
        (0x000000, '', [Keycode.HOME]), # Save for web
        # lower Encoder ---
        (0x000000, '', [Keycode.RIGHT_ARROW]), # Save for web
        (0x000000, '', [Keycode.LEFT_ARROW]), # Save for web
        (0x000000, '', [Keycode.HOME]), # Save for web
    ]
}

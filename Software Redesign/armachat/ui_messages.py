from armachat.ui_screen import Line as Line
from armachat.ui_screen import ui_screen as ui_screen
from armachat.ui_messages_view import ui_messages_view as ui_messages_view
from adafruit_simple_text_display import SimpleTextDisplay

class ui_messages(ui_screen):
    def __init__(self, ac_vars):
        ui_screen.__init__(self, ac_vars)

        self.exit_keys = []
        lines26 = [
            Line("Messages", SimpleTextDisplay.GREEN),
            Line("Scroll [L]down  [O]up", SimpleTextDisplay.WHITE),
            Line("Pg [ENT]next [DEL]previous", SimpleTextDisplay.WHITE),
            Line("[SPC] details", SimpleTextDisplay.WHITE),
            Line("[ALT] to exit", SimpleTextDisplay.WHITE),
            Line("", SimpleTextDisplay.WHITE),
            Line("", SimpleTextDisplay.WHITE),
            Line("", SimpleTextDisplay.WHITE),
            Line("", SimpleTextDisplay.WHITE),
            Line("[ALT] Exit [Ent] > [Del] <", SimpleTextDisplay.RED)
        ]
        lines20 = [
            Line("Messages", SimpleTextDisplay.GREEN),
            Line("Scroll [L]dwn  [O]up", SimpleTextDisplay.WHITE),
            Line("Pg [ENT]nxt [DEL]pre", SimpleTextDisplay.WHITE),
            Line("[SPC] details", SimpleTextDisplay.WHITE),
            Line("[ALT] to exit", SimpleTextDisplay.WHITE),
            Line("", SimpleTextDisplay.WHITE),
            Line("", SimpleTextDisplay.WHITE),
            Line("", SimpleTextDisplay.WHITE),
            Line("", SimpleTextDisplay.WHITE),
            Line("ALT-Ex [ENT]> [DEL]<", SimpleTextDisplay.RED)
        ]
        self.lines = lines26 if self.vars.display.width_chars >= 26 else lines20
        
    def show(self):
        self.line_index = 0
        self._show_screen()
        self.vars.display.sleepUpdate(None, True)
        while True:
            self.receive()
            keypress = self.vars.keypad.get_key()
            if self.vars.display.sleepUpdate(keypress):
                continue

            if keypress is not None:
                self._showGC()
                # O, L, Q, A, B, V
                if not self.checkKeys(keypress):
                    if keypress["key"] == "alt":
                        self.vars.sound.ring()
                        return None
                    elif keypress["key"] == "ent":
                        self.vars.sound.ring()
                        gui_setup_next = ui_messages_view(self.vars)
                        if gui_setup_next.show() == None:
                            return None
                        self.line_index = 0
                        self._show_screen()
                    elif keypress["key"] in self.exit_keys:
                        self.vars.sound.ring()
                        return keypress
                    else:
                        self.vars.sound.beep()

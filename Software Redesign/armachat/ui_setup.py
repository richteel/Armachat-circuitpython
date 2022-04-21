from armachat.ui_screen import Line as Line
from armachat.ui_screen import ui_screen as ui_screen
from armachat.ui_setup_radio import ui_setup_radio as ui_setup_radio
from adafruit_simple_text_display import SimpleTextDisplay

class ui_setup(ui_screen):
    def __init__(self, ac_vars):
        ui_screen.__init__(self, ac_vars)

        self.exit_keys = []
        lines26 = [
            Line("Setup", SimpleTextDisplay.GREEN),
            Line("", SimpleTextDisplay.WHITE),
            Line("Pg [ENT]next [DEL]previous", SimpleTextDisplay.WHITE),
            Line("[ALT] to exit", SimpleTextDisplay.WHITE),
            Line("", SimpleTextDisplay.WHITE),
            Line("", SimpleTextDisplay.WHITE),
            Line("", SimpleTextDisplay.WHITE),
            Line("", SimpleTextDisplay.WHITE),
            Line("", SimpleTextDisplay.WHITE),
            Line("[ALT] Exit [Ent] > [Del] <", SimpleTextDisplay.RED)
        ]
        lines20 = [
            Line("Setup", SimpleTextDisplay.GREEN),
            Line("Scroll [L]dwn  [O]up", SimpleTextDisplay.WHITE),
            Line("Pg [ENT]nxt [DEL]pre", SimpleTextDisplay.WHITE),
            Line("[ALT] to exit", SimpleTextDisplay.WHITE),
            Line("", SimpleTextDisplay.WHITE),
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
            self.vars.radio.receive(self.vars)
            keypress = self.vars.keypad.get_key()
            self.vars.display.sleepUpdate(keypress)

            if keypress is not None:
                print("keypress -> ", keypress)

                if keypress["key"] == "o":
                    if self._inc_lines(-1 * self.vars.display.height_lines):
                        self._show_screen()
                        self.vars.sound.ring()
                    else:
                        self.vars.sound.beep()
                elif keypress["key"] == "l":
                    if self._inc_lines(self.vars.display.height_lines):
                        self._show_screen()
                        self.vars.sound.ring()
                    else:
                        self.vars.sound.beep()
                elif keypress["key"] == "x":
                    self.vars.sound.ring()
                    if not self.vars.display.incBacklight(1):
                        self.vars.sound.ring()
                elif keypress["key"] == "z":
                    self.vars.sound.ring()
                    if not self.vars.display.incBacklight(-1):
                        self.vars.sound.ring()
                elif keypress["key"] == "q":
                    if self.vars.keypad.toggleBacklight():
                        self.vars.sound.ring()
                    else:
                        self.vars.sound.beep()
                elif keypress["key"] == "a":
                    self.vars.sound.ring()
                    self.vars.display.toggleBacklight()
                elif keypress["key"] == "alt":
                    self.vars.sound.ring()
                    return None
                elif keypress["key"] == "ent":
                    self.vars.sound.ring()
                    gui_setup_next = ui_setup_radio(self.vars)
                    if gui_setup_next.show() == None:
                        return None
                    self.line_index = 0
                    self._show_screen()
                elif keypress["key"] in self.exit_keys:
                    self.vars.sound.ring()
                    return keypress
                else:
                    self.vars.sound.beep()

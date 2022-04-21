from armachat.ui_screen import Line as Line
from armachat.ui_screen import ui_screen as ui_screen
from adafruit_simple_text_display import SimpleTextDisplay
from armachat.ui_setup_sound import ui_setup_sound as ui_setup_sound

class ui_setup_display(ui_screen):
    def __init__(self, ac_vars):
        ui_screen.__init__(self, ac_vars)

        self.exit_keys = []
        lines26 = [
            Line("ARMACHAT %freq%MHz      %RW%", SimpleTextDisplay.WHITE),
            Line("2 Display:", SimpleTextDisplay.GREEN),
            Line("[B] Bright %bright%", SimpleTextDisplay.WHITE),
            Line("[S] Sleep  %sleep% secs", SimpleTextDisplay.WHITE),
            Line("[F] Font   %font%", SimpleTextDisplay.WHITE),
            Line("[T] Theme  %theme%", SimpleTextDisplay.WHITE),
            Line("", SimpleTextDisplay.WHITE),
            Line("", SimpleTextDisplay.WHITE),
            Line("", SimpleTextDisplay.WHITE),
            Line("[ALT] Exit [Ent] > [Del] <", SimpleTextDisplay.RED)
        ]
        lines20 = [
            Line("%freq%MHz         %RW%", SimpleTextDisplay.WHITE),
            Line("2 Display:", SimpleTextDisplay.GREEN),
            Line("[B] Bright %bright%", SimpleTextDisplay.WHITE),
            Line("[S] Sleep  %sleep% secs", SimpleTextDisplay.WHITE),
            Line("[F] Font   %font%", SimpleTextDisplay.WHITE),
            Line("[T] Theme  %theme%", SimpleTextDisplay.WHITE),
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
                    gui_setup_next = ui_setup_sound(self.vars)
                    if gui_setup_next.show() == None:
                        return None
                    self.line_index = 0
                    self._show_screen()
                elif keypress["key"] == "bsp":
                    self.vars.sound.ring()
                    return keypress
                elif keypress["key"] == "b":
                    self.vars.sound.ring()
                    self.vars.display.incBrightness(1)
                    self._show_screen()
                elif keypress["key"] == "s":
                    self.vars.sound.ring()
                    self.vars.display.incSleep(1)
                    self._show_screen()
                elif keypress["key"] in self.exit_keys:
                    self.vars.sound.ring()
                    return keypress
                else:
                    self.vars.sound.beep()

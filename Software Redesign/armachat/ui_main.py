from armachat.ui_screen import Line as Line
from armachat.ui_screen import ui_screen as ui_screen
from adafruit_simple_text_display import SimpleTextDisplay

class ui_main(ui_screen):
    def __init__(self, ac_vars):
        ui_screen.__init__(self, ac_vars)
        
        self.exit_keys = ['n', 'm', 'i', 'p', 's']
        lines26 = [
            Line("ARMACHAT %freq%MHz      %RW%", SimpleTextDisplay.WHITE),
            Line(">(%myAddress%)%myName%", SimpleTextDisplay.GREEN),
            Line("[N] New message", SimpleTextDisplay.WHITE),
            Line("[D] To:(%toAddress%)%toName%", SimpleTextDisplay.WHITE),
            Line("[M] Messages - ALL:%countMessagesAll%", SimpleTextDisplay.WHITE),
            Line("New:%countMessagesNew% Undelivered:%countMessagesUndel%", SimpleTextDisplay.WHITE),
            Line("[ ]          [I] HW Info", SimpleTextDisplay.WHITE),
            Line("[ ]          [P] Ping", SimpleTextDisplay.WHITE),
            Line("[T] Terminal [S] Setup", SimpleTextDisplay.WHITE),
            Line("Ready ...", SimpleTextDisplay.RED)
        ]
        lines20 = [
            Line("%freq%MHz         %RW%", SimpleTextDisplay.WHITE),
            Line(">(%myAddress%)%myName%", SimpleTextDisplay.GREEN),
            Line("[N] New message", SimpleTextDisplay.WHITE),
            Line("[D] To:%to_name%", SimpleTextDisplay.WHITE),
            Line("[M] Messages-A:%countMessages_all%", SimpleTextDisplay.WHITE),
            Line("New:%countMessages_new% Undeliv:%countMessages_undel%", SimpleTextDisplay.WHITE),
            Line("[ ]       [I] HW Inf", SimpleTextDisplay.WHITE),
            Line("[ ]       [P] Ping", SimpleTextDisplay.WHITE),
            Line("[T] Term  [S] Setup", SimpleTextDisplay.WHITE),
            Line("Ready ...", SimpleTextDisplay.RED)
        ]
        self.lines = lines26 if self.vars.display.width_chars >= 26 else lines20

    def show(self):
        self.line_index = 0
        self._show_screen()
        self.vars.display.sleepUpdate(None, True)

        while True:
            self.vars.radio.receive(self.vars)
            keypress = self.vars.keypad.get_key()
            if self.vars.display.sleepUpdate(keypress):
                continue

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
                elif keypress["key"] == "d":
                    self.vars.sound.ring()
                    if keypress["longPress"]:
                        self.vars.to_dest_idx = self.changeValInt(self.vars.to_dest_idx, 0, len(self.vars.address_book) - 1, 1, False)
                    else:
                        self.vars.to_dest_idx = self.changeValInt(self.vars.to_dest_idx, 0, len(self.vars.address_book) - 1)

                    self._show_screen()
                elif keypress["key"] == "t":
                    self.vars.sound.ring()
                    self.vars.display.screen.show_terminal()
                    keypress = self.vars.keypad.get_key()
                    while keypress is None:
                        keypress = self.vars.keypad.get_key()
                    
                    self.vars.sound.ring()
                    self._show_screen()
                elif keypress["key"] in self.exit_keys:
                    self.vars.sound.ring()
                    return keypress
                else:
                    self.vars.sound.beep()

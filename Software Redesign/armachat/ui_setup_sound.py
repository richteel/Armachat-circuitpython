from armachat.ui_screen import Line as Line
from armachat.ui_screen import ui_screen as ui_screen
from adafruit_simple_text_display import SimpleTextDisplay
from config import config

class ui_setup_sound(ui_screen):
    def __init__(self, ac_vars):
        ui_screen.__init__(self, ac_vars)

        self.exit_keys = []
        lines26 = [
            Line("ARMACHAT %freq%MHz      %RW%", SimpleTextDisplay.WHITE),
            Line("3 Sound:", SimpleTextDisplay.GREEN),
            Line("[V] Volume %volume%", SimpleTextDisplay.WHITE),
            Line("", SimpleTextDisplay.WHITE),
            Line("[T] Tone %tone%", SimpleTextDisplay.WHITE),
            Line("[M] Melody %melodyIdx%", SimpleTextDisplay.WHITE),
            Line("    %melodyName%", SimpleTextDisplay.WHITE),
            Line("    %melodyLenSecs% secs", SimpleTextDisplay.WHITE),
            Line("", SimpleTextDisplay.WHITE),
            Line("[ALT] Exit [Ent] > [Del] <", SimpleTextDisplay.RED)
        ]
        lines20 = [
            Line("%freq%MHz         %RW%", SimpleTextDisplay.WHITE),
            Line("3 Sound:", SimpleTextDisplay.GREEN),
            Line("[V] Volume 6", SimpleTextDisplay.WHITE),
            Line("", SimpleTextDisplay.WHITE),
            Line("[T] Tone", SimpleTextDisplay.WHITE),
            Line("[M] Melody", SimpleTextDisplay.WHITE),
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
                elif keypress["key"] == "bsp":
                    self.vars.sound.ring()
                    return keypress
                elif keypress["key"] == "v":
                    config.volume += 1
                    if config.volume > 6:
                        config.volume = 0
                    config.writeConfig()
                    self._show_screen()
                    self.vars.sound.ring()
                elif keypress["key"] == "t":
                    config.tone += 1000
                    if config.tone > 10000:
                        config.tone = 1000
                    config.writeConfig()
                    self._show_screen()
                    self.vars.sound.ring()
                elif keypress["key"] == "m":
                    self.vars.sound.ring()
                    config.melody += 1
                    if config.melody > len(self.vars.sound.melody.melodies) - 1:
                        config.melody = 0
                    self._show_screen()
                    config.writeConfig()
                    self.vars.sound.play_melody(config.melody)
                elif keypress["key"] in self.exit_keys:
                    self.vars.sound.ring()
                    return keypress
                else:
                    self.vars.sound.beep()

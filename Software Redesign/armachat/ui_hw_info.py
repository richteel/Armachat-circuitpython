from armachat.ui_screen import Line as Line
from armachat.ui_screen import ui_screen as ui_screen
from adafruit_simple_text_display import SimpleTextDisplay

class ui_hw_info(ui_screen):
    def __init__(self, ac_vars):
        ui_screen.__init__(self, ac_vars)

        self.exit_keys = []
        lines26 = [
            Line("ARMACHAT %freq%MHz      %RW%", SimpleTextDisplay.WHITE),
            Line("System info:", SimpleTextDisplay.GREEN),
            Line("VSYS power = %vsys% V", SimpleTextDisplay.WHITE),
            Line("%usbConnected%", SimpleTextDisplay.WHITE),
            Line("Disk size %diskSize% KB", SimpleTextDisplay.WHITE),
            Line("Free space %freeSpace% KB", SimpleTextDisplay.WHITE),
            Line("CPU Temp: %cpuTemp% degrees C", SimpleTextDisplay.WHITE),
            Line("Free RAM %freeRam%", SimpleTextDisplay.WHITE),
            Line("", SimpleTextDisplay.WHITE),
            Line("[ALT] Exit", SimpleTextDisplay.RED)
        ]
        lines20 = [
            Line("%freq%MHz         %RW%", SimpleTextDisplay.WHITE),
            Line("System info:", SimpleTextDisplay.GREEN),
            Line("VSYS power = %vsys% V", SimpleTextDisplay.WHITE),
            Line("%usbConnected%", SimpleTextDisplay.WHITE),
            Line("Disk size %diskSize% KB", SimpleTextDisplay.WHITE),
            Line("Free space %freeSpace% KB", SimpleTextDisplay.WHITE),
            Line("CPU Temp: %cpuTemp% C", SimpleTextDisplay.WHITE),
            Line("Free RAM %freeRam%", SimpleTextDisplay.WHITE),
            Line("", SimpleTextDisplay.WHITE),
            Line("[ALT] Exit", SimpleTextDisplay.RED)
        ]
        self.lines = lines26 if self.vars.display.width_chars >= 26 else lines20
        
    def show(self):
        self.line_index = 0
        self._show_screen()

        while True:
            self.vars.radio.receive(self.vars)
            keypress = self.vars.keypad.get_key()

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
                else:
                    self.vars.sound.beep()

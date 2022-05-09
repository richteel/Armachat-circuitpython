from armachat.ui_screen import Line as Line
from armachat.ui_screen import ui_screen as ui_screen
from adafruit_simple_text_display import SimpleTextDisplay
from armachat.ui_setup_id import ui_setup_id as ui_setup_id
from armachat import config

class ui_setup_radio(ui_screen):
    def __init__(self, ac_vars):
        ui_screen.__init__(self, ac_vars)

        self.exit_keys = []
        lines26 = [
            Line("ARMACHAT %freq% MHz     %RW%", SimpleTextDisplay.WHITE),
            Line("0 Radio:", SimpleTextDisplay.GREEN),
            Line("[R] Region: %region%", SimpleTextDisplay.WHITE),
            Line("[F] Frequency: %freq% MHz", SimpleTextDisplay.WHITE),
            Line("    Channel: %channel%", SimpleTextDisplay.WHITE),
            Line("[P] Power: %power%", SimpleTextDisplay.WHITE),
            Line("[S] Profile: %profile%", SimpleTextDisplay.WHITE),
            Line("%profileName%", SimpleTextDisplay.WHITE),
            Line("%profileDesc%", SimpleTextDisplay.WHITE),
            Line("[ALT] Exit [Ent] > [Del] <", SimpleTextDisplay.RED)
        ]
        lines20 = [
            Line("%freq% MHz        %RW%", SimpleTextDisplay.WHITE),
            Line("0 Radio:", SimpleTextDisplay.GREEN),
            Line("[R] Region: %region%", SimpleTextDisplay.WHITE),
            Line("[F] Freq: %freq% MHz", SimpleTextDisplay.WHITE),
            Line("    Channel: %channel%", SimpleTextDisplay.WHITE),
            Line("[P] Power: %power%", SimpleTextDisplay.WHITE),
            Line("[S] Profile: %profile%", SimpleTextDisplay.WHITE),
            Line("%profileName%", SimpleTextDisplay.WHITE),
            Line("%profileDesc%", SimpleTextDisplay.WHITE),
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
            if self.vars.display.sleepUpdate(keypress):
                continue

            if keypress is not None:
                # O, L, Q, A, B, V
                if not self.checkKeys(keypress):
                    if keypress["key"] == "alt":
                        self.vars.sound.ring()
                        return None
                    elif keypress["key"] == "ent":
                        self.vars.sound.ring()
                        gui_setup_next = ui_setup_id(self.vars)
                        if gui_setup_next.show() == None:
                            return None
                        self.line_index = 0
                        self._show_screen()
                    elif keypress["key"] == "bsp":
                        self.vars.sound.ring()
                        return keypress
                    elif keypress["key"] == "r":
                        pass
                    elif keypress["key"] == "f":
                        preval = config.freq
                        config.setFreqToCenterOfChannel()
                        channelWidth = config.getChannelWidth()

                        if keypress["longPress"]:
                            config.freq = config.freq - channelWidth
                        else:
                            config.freq = config.freq + channelWidth
                        config.validateSetting("freq")
                        if preval != config.freq:
                            config.writeConfig()
                            self.vars.sound.ring()
                        else:
                            self.vars.sound.beep()
                        self._show_screen()
                    elif keypress["key"] == "p":
                        preval = config.power
                        if keypress["longPress"]:
                            config.power = self.changeValInt(config.power, 5, 23 , -1)
                        else:
                            config.power = self.changeValInt(config.power, 5, 23)
                        config.validateSetting("power")
                        if preval != config.power:
                            config.writeConfig()
                            self.vars.sound.ring()
                        else:
                            self.vars.sound.beep()
                        self._show_screen()
                    elif keypress["key"] == "s":
                        preval = config.loraProfile
                        if keypress["longPress"]:
                            config.loraProfile = self.changeValInt(config.loraProfile, 1, len(config.loraProfiles) , -1)
                        else:
                            config.loraProfile = self.changeValInt(config.loraProfile, 1, len(config.loraProfiles))
                        config.validateSetting("loraProfile")
                        if preval != config.loraProfile:
                            config.setFreqToCenterOfChannel()
                            config.writeConfig()
                            self.vars.sound.ring()
                        else:
                            self.vars.sound.beep()
                        self._show_screen()
                    elif keypress["key"] in self.exit_keys:
                        self.vars.sound.ring()
                        return keypress
                    else:
                        self.vars.sound.beep()

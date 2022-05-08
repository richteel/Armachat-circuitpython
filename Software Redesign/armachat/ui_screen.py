import gc
import supervisor
from collections import namedtuple
from adafruit_simple_text_display import SimpleTextDisplay
from config import config
from armachat import hw

Line = namedtuple('Line', ['text', 'color'])

class ui_screen(object):
    def __init__(self, ac_vars):
        self.vars = ac_vars
        self.exit_keys = []
        self.lines = []
        self.line_index = 0
        self.fs_rw = "??"
        self.fs_rw_long = "??"

    def _countMessages(self, msgStat=""):
        if msgStat is None:
            return 0
        allMsg = len(self.vars.messages)
        c = 0
        for i in range(allMsg):
            if self.vars.messages[i].count(msgStat) > 0:
                c = c + 1
        return c
    
    def _get_vars(self):
        return {
            "%freq%": "{:5.2f}".format(config.freq),
            "%RW%": self.fs_rw,
            "%RWlong%": self.fs_rw_long,
            "%myAddress%": str(config.myAddress),
            "%myName%": config.myName,
            "%toAddress%": self.vars.address_book[self.vars.to_dest_idx]["address"],
            "%toName%": self.vars.address_book[self.vars.to_dest_idx]["name"],
            "%countMessagesAll%": str(self._countMessages("")),
            "%countMessagesNew%": str(self._countMessages("|N|")),
            "%countMessagesUndel%": str(self._countMessages("|S|")),
            "%region%": config.region,
            "%power%": str(config.power),
            "%profile%": str(config.loraProfile),
            "%profileName%": hw.get_lora_profile_val("modemPresetConfig"),
            "%profileDesc%": hw.get_lora_profile_val("modemPresetDescription"),
            "%vsys%": "{:5.2f} V".format(hw.get_VSYSvoltage()),
            "%usbConnected%": "USB power connected" if hw.VBUS_status.value else "No USB power",
            "%diskSize%": "{:,.1f}".format(hw.get_DiskSpaceKb()),
            "%freeSpace%": "{:,.1f}".format(hw.get_FreeSpaceKb()),
            "%freeRam%": "{:,}".format(gc.mem_free()),
            "%cpuTemp%": "{:.2f}".format(hw.get_CpuTempC()),
            "%volume%": str(config.volume),
            "%tone%": str(config.tone),
            "%melodyIdx%": str(config.melody),
            "%melodyName%": self.vars.sound.get_melodyName(config.melody),
            "%melodyLenSecs%": self.vars.sound.get_melodyLength(config.melody),
            "%bright%": config.bright,
            "%sleep%": self.vars.display.get_sleepTime(),
            "%font%": config.font,
            "%theme%": config.theme,
        }

    def _inc_lines(self, step):
        if self.vars.display.height_lines >= len(self.lines):
            return False
        
        t = self.line_index + step

        if t < 0:
            self.vars.sound.ring()
            t = 0

        if t < len(self.lines):
            self.line_index = t
        else:
            self.vars.sound.ring()

        return True

    def _replace_var(self, text, screen_vars):
        txt = text

        for key, value in screen_vars.items():
            txt = txt.replace(key, str(value))

        return txt
    
    def _show_screen(self):
        print("Free RAM: {:,}".format(gc.mem_free()))
        gc.collect()
        print("gc.collect()")
        print("Free RAM: {:,}".format(gc.mem_free()))
        self.fs_rw = "RO"
        self.fs_rw_long = "Read Only"
        if config.fileSystemWriteMode():
            self.fs_rw = "RW"
            self.fs_rw_long = "Read Write"

        screen_vars = self._get_vars()
        
        if self.line_index >= len(self.lines):
            self.line_index = 0
        
        screenColors = ()

        for i in range(0, self.vars.display.height_lines):
            line = self.line_index + i

            if i > self.vars.display.height_lines - 1 or line > len(self.lines) - 1:
                screenColors += (SimpleTextDisplay.WHITE,)
            else:
                screenColors += (self.lines[line].color,)
        
        self.vars.display.screen = SimpleTextDisplay(
            display=self.vars.display.display,
            font=self.vars.display.font,
            text_scale=1,
            colors=screenColors
        )

        for i in range(0, self.vars.display.height_lines):
            line = self.line_index + i

            if i > self.vars.display.height_lines - 1 or line > len(self.lines) - 1:
                self.vars.display.screen[i].text = ""
            else:
                self.vars.display.screen[i].text = \
                    self._replace_var(self.lines[line].text, screen_vars)
            
        self.vars.display.screen.show()

    def changeValInt(self, currentval, min, max, step=1, loopval=False):
        newval = currentval
        newval += step
        
        if not loopval and (newval < min or newval > max):
            newval = currentval
        elif loopval and newval < min:
            newval = max
        elif loopval and newval > max:
            newval = min
        
        return newval

    def checkKeys(self, keypress):
        handled = False
        
        print("keypress -> ", keypress)

        # Navigation for small screens
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
        # Special keys for all screens except editor
        # Volume
        elif keypress["key"] == "v":
            preval = config.volume
            if keypress["longPress"]:
                config.volume = self.changeValInt(config.volume, 0, 6, -1)
            else:
                config.volume = self.changeValInt(config.volume, 0, 6)
            config.writeConfig()
            
            if preval != config.volume:
                self.vars.sound.ring()
            else:
                self.vars.sound.beep()
        # Brightness (Screen)
        elif keypress["key"] == "b":
            preval = config.bright
            if keypress["longPress"]:
                self.vars.display.incBacklight(-1)
            else:
                self.vars.display.incBacklight(1)
            config.writeConfig()

            if preval != config.bright:
                self.vars.sound.ring()
            else:
                self.vars.sound.beep()
        # Toggle Keyboard Backlight
        elif keypress["key"] == "q":
            if self.vars.keypad.toggleBacklight():
                self.vars.sound.ring()
            else:
                self.vars.sound.beep()
        # Toggle Display Backlight
        elif keypress["key"] == "a":
            self.vars.sound.ring()
            self.vars.display.toggleBacklight()

        return handled

    def isUsbConnected(self):
        return supervisor.runtime.usb_connected

    def show(self):
        raise NotImplementedError
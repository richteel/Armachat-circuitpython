import gc
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
            "%myAddress%": str(config.myAddress),
            "%myName%": config.myName,
            "%toAddress%": self.vars.address_book[self.vars.to_dest_idx]["address"],
            "%toName%": self.vars.address_book[self.vars.to_dest_idx]["name"],
            "%countMessagesAll%": str(self._countMessages("")),
            "%countMessagesNew%": str(self._countMessages("|N|")),
            "%countMessagesUndel%": str(self._countMessages("|S|")),
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
        if config.fileSystemWriteMode():
            self.fs_rw += "RW"

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
                self.vars.display.screen[i].text = self._replace_var(self.lines[line].text, screen_vars)
            
        self.vars.display.screen.show()

    def changeValInt(self, currentval, min, max, step=1, inc=True):
        newval = currentval
        if inc:
            newval += step
        else:
            newval -= step

        if newval < min:
            newval = max
        elif newval > max:
            newval = min
        
        return newval

    def show(self):
        raise NotImplementedError
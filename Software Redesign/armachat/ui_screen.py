import gc
import supervisor
import displayio
import terminalio
import time
from adafruit_display_text import label
from collections import namedtuple
from adafruit_simple_text_display import SimpleTextDisplay
from armachat import config
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
        self.editor = { 
            "action": "",
            "cursorPos": 0,
            "cursorPosX": 0,
            "cursorPosY": 0,
            "text": "",
            "maxLines": 0,
            "maxLen": 0,
            "validation": "",
            "validationMsg1": "",
            "validationMsg2": "",
            }
        self.receiveTimeout = 0.1

    '''
    def _countMessages(self, msgStat=""):
        if msgStat is None:
            return 0
        allMsg = len(self.vars.messages)
        c = 0
        for i in range(allMsg):
            if self.vars.messages[i].count(msgStat) > 0:
                c = c + 1
        return c
    '''

    def _countMessages(self, msgStat=""):
        if msgStat is None:
            return 0
        c = 0
        for i in range(len(self.vars.messages)):
            if len(msgStat) == 0 or self.vars.messages[i]["status"] == msgStat:
                c = c + 1
        return c
    
    def _get_vars(self):
        return {
            "%freq%": "{:5.2f}".format(config.freq),
            "%channel%": str(config.getChannel()),
            "%RW%": self.fs_rw,
            "%RWlong%": self.fs_rw_long,
            "%myAddress%": str(config.myAddress),
            "%myName%": config.myName,
            "%toAddress%": self.vars.address_book[self.vars.to_dest_idx]["address"],
            "%toName%": self.vars.address_book[self.vars.to_dest_idx]["name"],
            "%countMessagesAll%": str(self._countMessages("")),
            "%countMessagesNew%": str(self._countMessages("N")),
            "%countMessagesUndel%": str(self._countMessages("S")),
            "%region%": config.region,
            "%power%": str(config.power),
            "%profile%": str(config.loraProfile),
            "%profileName%": config.loraProfiles[config.loraProfile - 1]["modemPresetConfig"],
            "%profileDesc%": config.loraProfiles[config.loraProfile - 1]["modemPresetDescription"],
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
            "%locked%": "L" if self.vars.keypad.keyLayoutLocked else "U",
            "%line%": self.editor["cursorPosY"],
            "%col%": self.editor["cursorPosX"],
            "%pos%": self.editor["cursorPos"],
            "%len%": len(self.editor["text"]) - 1,
            "%keyLayout%": self.vars.keypad.keyLayout,
            "%action%": self.editor["action"],
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

    def _showGC(self):
        print("Free RAM: {:,}".format(gc.mem_free()))
        gc.collect()
        print("gc.collect()")
        print("Free RAM: {:,}".format(gc.mem_free()))
    
    def _show_screen(self):
        self._showGC()
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
        self._showGC()

    def appendMessage(self, message):
        timeStamp = str(time.monotonic())

        self.vars.messages.append(
            message["to"]
            + "|"
            + message["from"]
            + "|"
            + message["id"]
            + "|"
            + str(message["hops"]) if message["hops"] is not None else "n/a"
            + "|"
            + message["status"]
            + "|"
            + str(message["rssi"]) if message["rssi"] is not None else "n/a"
            + "|"
            + str(message["snr"]) if message["snr"] is not None else "n/a"
            + "|"
            + timeStamp
            + "|"
            + str(message["data"]),
            "utf-8",
        )

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
        
        # print("keypress -> ", keypress)

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

    def getTimeStamp(self):
        return time.monotonic()

    def isUsbConnected(self):
        return supervisor.runtime.usb_connected

    def receive(self):
        message = self.vars.radio.receive(timeout=self.receiveTimeout)

        if message is not None:
            self._showGC()
            self.vars.messages.append(message)
            self._show_screen()
            self.vars.sound.play_melody(config.melody)
            self._showGC()

    def show(self):
        raise NotImplementedError

    def showConfirmation(self, message="", okOnly = False, message2=""):
        self._showGC()
        font_width, font_height = terminalio.FONT.get_bounding_box()
        font_scale = 2
        char_width = self.vars.display.display.width/(font_width * font_scale) - 2
        startX = (font_width * font_scale)
        startY = int((self.vars.display.display.height - (font_height * 3))/2)

        text1 = message if len(message)>0 else self.editor["action"]
        text2 = "[ENT] Yes [DEL] No"
        text3 = "[ALT] Cancel"
        if okOnly:
            text2 = message2
            text3 = "[ENT] OK"

        text1 = self.textCenter(text1, char_width)
        text2 = self.textCenter(text2, char_width)
        text3 = self.textCenter(text3, char_width)

        # Make the display context
        splash = displayio.Group(x=startX, y=startY)

        text_area1 = label.Label(
            terminalio.FONT, text=text1, scale=font_scale, background_tight=False, background_color=0x000066, color=0xFFFFFF
        )
        
        text_area2 = label.Label(
            terminalio.FONT, text=text2, scale=font_scale, background_tight=False, background_color=0x0000FF, color=0xFFFFFF
        )
        text_area2.y = (font_height * font_scale)

        text_area3 = label.Label(
            terminalio.FONT, text=text3, scale=font_scale, background_tight=False, background_color=0x0000FF, color=0xFFFFFF
        )
        text_area3.y = font_height * font_scale * 2

        splash.append(text_area1)
        splash.append(text_area2)
        splash.append(text_area3)

        self.vars.keypad.keyLayout = self.vars.keypad.keyboards[0]["layout"]

        # self.vars.display.display.show(splash)
        self.vars.display.screen.text_group.append(splash)
        self.vars.display.screen.show()

        while True:
            self.receive()
            keypress = self.vars.keypad.get_key()

            if self.vars.display.sleepUpdate(keypress):
                continue

            if keypress is not None:
                self._showGC()
                # ent, bsp, or alt
                if not self.checkKeys(keypress):
                    if keypress["key"] == "ent" or keypress["key"] == "rt" or keypress["key"] == "dn":
                        self.vars.sound.ring()
                        return "Y"
                    elif keypress["key"] == "bsp" or keypress["key"] == "lt" or keypress["key"] == "up":
                        self.vars.sound.ring()
                        return "N"
                    elif keypress["key"] == "alt":
                        self.vars.sound.ring()
                        self.vars.keypad.keyLayout = self.vars.keypad.keyboards[self.vars.keypad.keyboard_current_idx]["layout"]
                        return None
                    else:
                        self.vars.sound.beep()

        # self.vars.keypad.keyLayout = self.vars.keypad.keyboards[self.vars.keypad.keyboard_current_idx]["layout"]
        self._showGC()
    
    
    def textCenter(self, text, char_width):
        retText = (" " * int((char_width - len(text))/2)) + text
        retText += " " * int(char_width - len(retText))
        return retText
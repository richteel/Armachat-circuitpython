import time

# import alarm
import board
import busio
import terminalio
import displayio
import analogio
import gc
import os
import aesio
# import random
from binascii import hexlify
import microcontroller
from adafruit_simple_text_display import SimpleTextDisplay

# import adafruit_imageload
import adafruit_matrixkeypad

from adafruit_bitmap_font import bitmap_font
from pwmio import PWMOut

from adafruit_display_text import label
from adafruit_st7789 import ST7789
from config import config
import digitalio

# import adafruit_rfm9x
# import ulora
import armachat_lora

import armachat_address

FREQ_LIST = [169.0, 434.0, 868.0, 915.0]

modemPreset = (0x72, 0x74, 0x04)  # < Bw = 125 kHz, Cr = 4/5, Sf = 128chips/symbol,
#  CRC on. Default medium range
modemPresetConfig = "c"
modemPresetDescription = "d"
messages = ["1|2|3|4|5|6|7|8|a1|a2|a3|a4|a5|a6|a7|a8"]
msgCounter = 0x00
message = ""


def readKeyboard():
    message = receiveMessage()
    if not message == "":
        ring()
        ring()
    return keypad.pressed_keys


def beep():
    audioPin = PWMOut(board.GP0, duty_cycle=0, frequency=440, variable_frequency=True)
    audioPin.frequency = 5000
    audioPin.duty_cycle = 1000 * (config.volume)
    time.sleep(0.002)
    audioPin.duty_cycle = 0
    audioPin.deinit()


def ring():
    audioPin = PWMOut(board.GP0, duty_cycle=0, frequency=440, variable_frequency=True)
    audioPin.frequency = 2000
    audioPin.duty_cycle = 1000 * (config.volume)
    time.sleep(0.1)
    audioPin.frequency = 3000
    audioPin.duty_cycle = 1000 * (config.volume)
    time.sleep(0.1)
    audioPin.frequency = 6000
    audioPin.duty_cycle = 1000 * (config.volume)
    time.sleep(0.1)
    audioPin.duty_cycle = 0
    audioPin.deinit()


def get_VSYSvoltage():
    VSYSin = ((VSYS_voltage.value * 3.3) / 65536) * 3
    return VSYSin


def countMessages(msgStat=""):
    allMsg = len(messages)
    c = 0
    for i in range(allMsg):
        if messages[i].count(msgStat) > 0:
            c = c + 1
            # print(messages[i])
    return c


def changeMessageStatus(msgID="", old="", new=""):
    allMsg = len(messages)
    c = 0
    print(msgID)
    for i in range(allMsg):
        if messages[i].count(msgID) > 0:
            print("Change status for message:" + msgID)
            messages[i] = messages[i].replace(old, new)
            c = c + 1
    return c


def clearScreen(stat=""):
    for i in range(8):
        screen[i].text = ""


def screenSafeText(txt=""):
    retText = txt

    for x in range(32):
        if x != 9 and x != 10 and x != 13:
            retText = retText.replace(chr(x), "")
    return retText


def showMemory():
    msg = 0
    clearScreen()
    ring()
    screen.show()
    while True:
        time.sleep(0.1)  # a little delay here helps avoid debounce annoyances
        keys = keypad.pressed_keys
        if keys:
            beep()
            if keys[0] == "lt" or keys[0] == "bsp":
                if msg > 0:
                    msg = msg - 1
            if keys[0] == "rt" or keys[0] == "ent":
                if msg < (len(messages) - 1):
                    msg = msg + 1
            if keys[0] == "tab" or keys[0] == "alt":
                beep()
                return 1
            if keys[0] == "s":
                beep()
                try:
                    with open("messages.txt", "a") as f:
                        for line in messages:
                            print(line)
                            f.write(line + "\n")
                    # f.close()
                except OSError:
                    print("messages.txt - Read Only File System")
            if keys[0] == "r":
                beep()
                messages.clear()
                try:
                    with open("messages.txt", "r") as f:
                        msgf = f.readlines()
                        print("Reading messages:")
                        for line in msgf:
                            print(line)
                            messages.append(line)
                    # f.close()
                except OSError:
                    print("messages.txt does not exist")

            # for f in messages[message]
            clearScreen()
            screen[0].text = "Message:" + str(msg)
            mem = messages[msg]
            oneItm = mem.split("|")
            line = 1
            if messages[msg].count("|N|") > 0:
                print("Mesage mark as read:" + str(msg))
                messages[msg] = messages[msg].replace("|N|", "|R|")
                ring()
            # ( destination+'|'+sender+'|'+messageID+'|'+hop+'|R|'+rssi+'|'+snr+'|'+
            # timeStamp+'|'+packet_text,'utf-8')
            if keys[0] == " ":
                screen[1].text = "Status:" + oneItm[4]
                screen[2].text = "To:" + oneItm[0]
                screen[3].text = "From:" + oneItm[1]
                screen[4].text = "MsgId:" + oneItm[2]
                screen[5].text = "Hop:" + oneItm[3]
                screen[6].text = "RSSI:" + oneItm[5] + " SNR:" + oneItm[6]
                screen[7].text = "Time:" + oneItm[7]
                screen[8].text = "[ALT] Exit"
            else:
                screen[1].text = screenSafeText(oneItm[8])
                screen[2].text = screenSafeText(oneItm[9])
                screen[3].text = screenSafeText(oneItm[10])
                screen[4].text = screenSafeText(oneItm[11])
                screen[5].text = screenSafeText(oneItm[12])
                screen[6].text = screenSafeText(oneItm[13])
                screen[7].text = screenSafeText(oneItm[14])
                screen[8].text = "ALT-Ex Ent> Del< SPC-Detail"


def sendMessage(text, messageID):
    LED.value = True

    destination = address_book[to_dest_idx]["address"]
    outp = bytearray(len(text))
    cipher = aesio.AES(bytes(config.password, "utf-8"),
                       aesio.MODE_CTR, bytes(config.passwordIv, "utf-8"))
    cipher.encrypt_into(bytes(text, "utf-8"), outp)
    # print("Send header:")
    # print(hexlify(bytearray(header)))
    print("Encrypted message:")
    print(hexlify(outp))
    # rfm9x.send(list(bytearray(header)) + list(outp), 0)  # (list(outp), 0)
    rfm9x.send(destination, outp, msgId=messageID)  # (list(outp), 0)

    timeStamp = str(time.monotonic())
    # print(sender)
    # print(hop)
    print("Save to message memory:")
    print("text -> ", text)
    print("type(text) -> ", type(text))
    storedMsg = str(destination
                    + "|"
                    + config.myAddress
                    + "|"
                    + messageID
                    + "|"
                    + str(rfm9x._hop_limit)
                    + "|S|n/a|n/a|"
                    + timeStamp  # str
                    + "|"
                    + text,  # str
                    "utf-8",
                    )
    print(storedMsg)
    messages.append(storedMsg)
    LED.value = False


def receiveMessage():
    message = rfm9x.receive(timeout=0.1)

    # If no packet was received during the timeout then None is returned.
    if message is None:
        return None

    # Check values
    if message["to"] is None or message["from"] is None or message["id"] is None or \
            message["flags"] is None:
        print("ERROR: receiveMessage - to, from, id, or flags is None")
        return None
    if len(message["to"]) != 4:
        print("ERROR: receiveMessage - 'to' incorrect length -> ",
              len(message["to"]))
        return None
    if len(message["from"]) != 4:
        print("ERROR: receiveMessage - 'from' incorrect length -> ",
              len(message["from"]))
        return None
    if len(message["id"]) != 4:
        print("ERROR: receiveMessage - 'id' incorrect length -> ",
              len(message["id"]))
        return None
    if len(message["flags"]) != 4:
        print("ERROR: receiveMessage - 'flags' incorrect length -> ",
              len(message["flags"]))
        return None

    # Received delivery confirmation
    if message["flags"][2] == 33:  # 33 = symbol ! it is delivery confirmation
        print("Delivery comfirmation")
        print("hexlify(message[\"id\"])", str(hexlify(message["id"]), "utf-8"))
        changeMessageStatus(
            msgID=str(hexlify(message["id"]), "utf-8"), old="|S|", new="|D|"
        )
        # do something to mark message is delivered
        packet_text = "D"
        return packet_text

    # One last check to see if we may continue
    if message["data"] is None:
        print("ERROR: receiveMessage - data is None")
        return None

    # Decrypt
    cipher = aesio.AES(bytes(config.password, "utf-8"),
                       aesio.MODE_CTR, bytes(config.passwordIv, "utf-8"))
    inp = bytes(message["data"])
    outp = bytearray(len(inp))
    cipher.encrypt_into(inp, outp)
    print("Received encrypted message:")
    print(hexlify(inp))
    try:
        packet_text = str(outp, "utf-8")
    except UnicodeError:
        print("ERROR: receiveMessage - cannot decode message")
        packet_text = ""
        return packet_text
    print("Decoded message:")
    print(packet_text)

    rssi = str(rfm9x.last_rssi)
    snr = str(rfm9x.last_snr)
    destination = armachat_address.addressLst2Str(message["to"])
    sender = armachat_address.addressLst2Str(message["from"])
    messageID = str(hexlify(message["id"]))
    hop = str(message["flags"][3])
    timeStamp = str(time.monotonic())

    print("destination -> ", destination)
    print("sender -> ", sender)
    print("messageID -> ", messageID)
    print("hop -> ", hop)
    print("timeStamp -> ", timeStamp)

    storedMsg = str(
        destination
        + "|"
        + sender
        + "|"
        + messageID
        + "|"
        + hop
        + "|N|"
        + rssi
        + "|"
        + snr
        + "|"
        + timeStamp
        + "|"
        + packet_text,
        "utf-8"
    )

    msgPart = storedMsg.split("|")

    while len(msgPart) < 16:
        storedMsg = storedMsg + "|"
        msgPart = storedMsg.split("|")
    print("SNR:" + snr + " RSSI:" + rssi)

    print(storedMsg)
    messages.append(storedMsg)

    # confirmation
    LED.value = True
    # Set confirmation flag
    message["flags"][2] = 33  # 33 = symbol ! it is delivery confirmation

    # Create response header = swap destination<>sender + same message ID
    # Sender (4:8), Destination (0:4), MessageID (8:12), HopLimit(12:16)
    header = message["from"] + message["to"] + message["id"] + message["flags"]
    print("Response header ...")
    print(hexlify(header))
    mId = armachat_address.addressLst2Str(message["id"])
    # rfm9x.send(list(bytearray(header + "!")), 0)  # (list(outp), 0)
    rfm9x.send(sender, (list("Confirmation")), mId,
               flags=message["flags"])

    print("Confirmation send ...")
    LED.value = False
    return packet_text


def valueUp(min, max, value):
    value = value + 1
    if value > max:
        value = min
    if value < min:
        value = max
    return value


def getListIndex(lst, value):
    for i in range(len(lst)):
        if lst[i] == value:
            return i
    return -1


def valueUpList(lst, value):
    idx = getListIndex(lst, value) + 1

    if idx >= len(lst):
        idx = 0
    if idx < 0:
        idx = len(lst) - 1

    return lst[idx]


def setup():
    menu = 0
    screen[0].text = "SETUP:"
    screen[1].text = "Use Left/Right"
    screen[2].text = "to switch page"
    screen[3].text = "[ESC] to exit"
    screen[4].text = ""
    screen[5].text = ""
    screen[6].text = ""
    screen[7].text = ""
    screen[8].text = ""
    ring()
    screen.show()
    while True:
        keys = keypad.pressed_keys
        if keys:
            beep()
            if keys[0] == "lt" or keys[0] == "bsp":
                if menu > 0:
                    menu = menu - 1
            if keys[0] == "rt" or keys[0] == "ent":
                if menu < 3:
                    menu = menu + 1
            if keys[0] == "tab" or keys[0] == "alt":
                beep()
                return 1
            if menu == 0:
                if keys[0] == "f":
                    config.freq = valueUpList(FREQ_LIST, config.freq)
                    radioInit()
                    config.writeConfig()
                if keys[0] == "p":
                    config.power = valueUp(5, 23, config.power)
                    radioInit()
                    config.writeConfig()
                if keys[0] == "x":
                    config.loraProfile = valueUp(1, 6, config.loraProfile)
                    loraProfileSetup(config.loraProfile)
                    radioInit()
                    config.writeConfig()
                screen[0].text = "{:.d} Radio:".format(menu)
                screen[1].text = "[F] Frequency: {:5.2f}MHz".format(config.freq)
                screen[2].text = "[P] Power {:.d}".format(config.power)
                screen[3].text = "[X] Profile {:.d}".format(config.loraProfile)
                screen[4].text = modemPresetConfig
                screen[5].text = modemPresetDescription
                screen[6].text = ""
                screen[7].text = ""
                screen[8].text = "[ALT] Exit [Ent] > [Del] <"
                screen.show()
            elif menu == 1:
                if keys[0] == "n":
                    config.myName = editor(text=config.myName)
                    config.writeConfig()
                screen[0].text = "{:.d} Identity:".format(menu)
                screen[1].text = "[N] Name: {} ".format(config.myName)
                screen[2].text = "------"
                screen[3].text = "[G] Group 3:{}".format(config.myGroup3)
                screen[4].text = "[G] Group 2:{}".format(config.myGroup2)
                screen[5].text = "[G] Group 1:{}".format(config.myGroup1)
                screen[6].text = "[I] ID:     {}".format(config.myID)
                screen[7].text = "[E] Encryption {}"
                screen[8].text = "[ALT] Exit [Ent] > [Del] <"
                screen.show()
            elif menu == 2:
                screen[0].text = "{:.d} Display:".format(menu)
                screen[1].text = "[B] Bright {}".format(config.bright)
                screen[2].text = "[I] Sleep  {}".format(config.sleep)
                screen[3].text = "[F] Font   {}".format(config.font)
                screen[4].text = "[T] Theme  {}".format(config.theme)
                screen[5].text = ""
                screen[6].text = ""
                screen[7].text = ""
                screen[8].text = "[ALT] Exit [Ent] > [Del] <"
                screen.show()
            elif menu == 3:
                if keys[0] == "v":
                    config.volume = valueUp(0, 6, config.volume)
                    ring()
                    config.writeConfig()
                screen[0].text = "{:.d} Sound:".format(menu)
                screen[1].text = "[V] Volume {}".format(config.volume)
                screen[2].text = ""
                screen[3].text = "[T] Tone"
                screen[4].text = "[M] Melody"
                screen[5].text = ""
                screen[6].text = ""
                screen[7].text = ""
                screen[8].text = "[ALT] Exit [Ent] > [Del] <"
                screen.show()


def editor(text):
    cursor = 0
    layout = 0
    editLine = 0
    editText = text
    layoutName = "abc"
    EditorScreen[8].text = "[Ent] confirm"
    EditorScreen.show()
    line = ["0", "1", "2", "3", "4", "5", "6"]
    line[0] = text
    line[1] = ""
    line[2] = ""
    line[3] = ""
    line[4] = ""
    line[5] = ""
    line[6] = ""
    EditorScreen[1].text = line[0]
    EditorScreen[2].text = line[1]
    EditorScreen[3].text = line[2]
    EditorScreen[4].text = line[3]
    EditorScreen[5].text = line[4]
    EditorScreen[6].text = line[5]
    EditorScreen[7].text = line[6]
    while True:
        EditorScreen[0].text = (
            "["
            + layoutName
            + "] "
            + str(editLine)
            + ":"
            + str(cursor)
            + "/"
            + str(len(text))
        )

        if layout == 0:
            keypad = adafruit_matrixkeypad.Matrix_Keypad(
                config.rows, config.cols, config.keys1
            )
            layoutName = "abc"
            HotKeysHelp = "[Ent] Send    [Del] Delete"
        elif layout == 1:
            keypad = adafruit_matrixkeypad.Matrix_Keypad(
                config.rows, config.cols, config.keys2
            )
            layoutName = "123"
            HotKeysHelp = "[Ent] < Left  [Del] > Right"
        elif layout == 2:
            keypad = adafruit_matrixkeypad.Matrix_Keypad(
                config.rows, config.cols, config.keys3
            )
            layoutName = "ABC"
            HotKeysHelp = "[Ent] Down    [Del] Up"
        keys = keypad.pressed_keys

        if config.model == "compact":
            EditorScreen[8].text = HotKeysHelp

        if keys:
            if keys[0] == "alt":
                layout = layout + 1
                ring()
                if layout == 3:
                    layout = 0
                keys[0] = ""
            if keys[0] == "bsp" and cursor == 0:
                text = ""
                return text
            if keys[0] == "bsp":
                if cursor > 0:
                    editText = (editText[0 : cursor - 1]) + (editText[cursor:])
                    cursor = cursor - 1
                keys[0] = ""
            if keys[0] == "lt":
                if cursor > 0:
                    cursor = cursor - 1
                keys[0] = ""
            if keys[0] == "rt":
                if cursor < len(editText):
                    cursor = cursor + 1
                keys[0] = ""
            if keys[0] == "up":
                line[editLine] = editText
                EditorScreen[editLine + 1].text = editText
                if editLine > 0:
                    editLine = editLine - 1
                editText = line[editLine]
                cursor = 0
                keys[0] = ""
            if keys[0] == "dn":
                line[editLine] = editText
                EditorScreen[editLine + 1].text = editText
                if editLine < config.maxLines:
                    editLine = editLine + 1
                editText = line[editLine]
                cursor = 0
                keys[0] = ""
            if keys[0] == "ent":
                beep()
                for r in range(7):
                    text = text + line[r] + "|"
                return text
            if keys[0] != "":
                if len(editText) < config.maxChars:
                    editText = (editText[0:cursor]) + keys[0] + (editText[cursor:])
                    cursor = cursor + 1
                    layout = 0
                    while keypad.pressed_keys:
                        pass
            line[editLine] = editText  # (editText[0:cursor])+"_"+(editText[cursor:])
            EditorScreen[editLine + 1].text = (
                (editText[0:cursor]) + "_" + (editText[cursor:])
            )  # line[editLine]
            EditorScreen.show()


def loraProfileSetup(profile):
    global modemPresetConfig
    global modemPresetDescription
    global modemPreset

    if profile == 1:
        modemPreset = (0x92, 0x74, 0x04)  # Bw = 500kHz, Cr = 4/5,
        #   Sf = 128chips/symbol, CRC on.
        modemPresetConfig = "Bw500Cr45Sf128"
        modemPresetDescription = "Short/Fast"
    if profile == 2:
        modemPreset = (0x72, 0x74, 0x04)  # Bw = 125kHz, Cr = 4/5,
        #   Sf = 128chips/symbol, CRC on.
        modemPresetConfig = "Bw125Cr45Sf128"
        modemPresetDescription = "Short/Slow"
    if profile == 3:
        modemPreset = (0x82, 0xA4, 0x04)  # Bw = 250kHz, Cr = 4/7,
        #   Sf = 1024chips/symbol, CRC on.
        modemPresetConfig = "Bw250Cr47Sf1024"
        modemPresetDescription = "Medium/Fast"
    if profile == 4:
        modemPreset = (0x84, 0xB4, 0x04)  # Bw = 250kHz, Cr = 4/6,
        #   Sf = 2048chips/symbol, CRC on.
        modemPresetConfig = "Bw250Cr46Sf2048"
        modemPresetDescription = "Medium/Slow"
    if profile == 5:
        modemPreset = (0x48, 0x94, 0x04)  # Bw = 31.25kHz, Cr = 4/8,
        #   Sf = 512chips/symbol, CRC on.
        modemPresetConfig = "Bw31_25Cr48Sf512"
        modemPresetDescription = "Long/Fast"
    if profile == 6:
        modemPreset = (0x78, 0xC4, 0x0C)  # Bw = 125kHz, Cr = 4/8,
        #   Sf = 4096chips/symbol, CRC on.
        modemPresetConfig = "Bw125Cr48Sf4096"
        modemPresetDescription = "Long/Slow"


def radioInit():
    global rfm9x

    # print("myAddress -> ", myAddress)

    try:
        rfm9x = armachat_lora.LoRa(
            spi, CS, freq=config.freq, modem_config=modemPreset,
            tx_power=config.power, this_address=config.myAddress,
            hop_limit=config.hopLimit
        )  # , interrupt=28
    except Exception as e:
        print("Lora module not detected !!!")  # None
        print(e)

def loadAddressBook():
    broadcastAddressList = armachat_address.broadcastAddressList(config.myAddress,
                                                                 config.groupMask)
    broadcastAddress = armachat_address.addressLst2Str(broadcastAddressList)
    # destinations = "Sammy|12-36-124-8|Tom|12-36-124-17|Sandy|12-36-124-3"
    parts = config.destinations.split("|")
    retVal = [{"name": "All", "address": broadcastAddress}]

    if len(parts) % 2 != 0:
        return retVal

    for i in range(0, len(parts), 2):
        retVal += [{"name": parts[i], "address": parts[i+1]}]

    return retVal

# ----------------------FUNCTIONS---------------------------

# with open('x.txt', 'w') as f:
#    f.write("Hello world!\r\n")
#    f.close()


if config.model == "compact":
    KBL = digitalio.DigitalInOut(board.GP14)
    KBL.direction = digitalio.Direction.OUTPUT

LED = digitalio.DigitalInOut(board.LED)
LED.direction = digitalio.Direction.OUTPUT
VSYS_voltage = analogio.AnalogIn(board.VOLTAGE_MONITOR)

VBUS_status = digitalio.DigitalInOut(board.VBUS_SENSE)  # defaults to input
VBUS_status.pull = digitalio.Pull.UP  # turn on internal pull-up resistor

SMPSmode = digitalio.DigitalInOut(board.SMPS_MODE)
SMPSmode.direction = digitalio.Direction.OUTPUT
SMPSmode.value = True

displayio.release_displays()

tft_cs = board.GP21
tft_dc = board.GP16
spi_mosi = board.GP19
spi_clk = board.GP18
spi = busio.SPI(spi_clk, spi_mosi)
backlight = board.GP20

# BACKLIGHT = PWMOut(backlightLed, duty_cycle=0, frequency=500, variable_frequency=True)
# BACKLIGHT.duty_cycle = 65535

display_bus = displayio.FourWire(spi, command=tft_dc, chip_select=tft_cs)

display = ST7789(
    display_bus, rotation=270, width=320, height=240, backlight_pin=backlight
)
# Make the display context
splash = displayio.Group()
display.show(splash)

text = "Free RAM:" + str(gc.mem_free()) + " Loading ..."
text_area = label.Label(
    terminalio.FONT, text=text, scale=2, background_tight=False, background_color=255
)
text_area.x = 0
text_area.y = 100

display.show(text_area)


# font
font_file = "fonts/neep-24.pcf"
# font_file = "fonts/gohufont-14.pcf"
# font_file = "fonts/Gomme10x20n.pcf"
# font_file = "fonts/Arial-18.pcf"
font = bitmap_font.load_font(font_file)
# font = terminalio.FONT


# Define pins connected to the chip.
CS = digitalio.DigitalInOut(board.GP13)
RESET = digitalio.DigitalInOut(board.GP17)
spi = busio.SPI(board.GP10, MOSI=board.GP11, MISO=board.GP12)
# Initialze radio

print("starting Lora")

loraProfileSetup(config.loraProfile)

rfm9x = None

radioInit()

print("Free memory:")
print(gc.mem_free())
EditorScreen = SimpleTextDisplay(
    display=display,
    font=font,
    title="Armachat EDITOR",
    title_scale=1,
    text_scale=1,
    colors=(
        SimpleTextDisplay.YELLOW,
        SimpleTextDisplay.WHITE,
        SimpleTextDisplay.WHITE,
        SimpleTextDisplay.WHITE,
        SimpleTextDisplay.WHITE,
        SimpleTextDisplay.WHITE,
        SimpleTextDisplay.WHITE,
        SimpleTextDisplay.WHITE,
        SimpleTextDisplay.GREEN,
    ),
)

screen = SimpleTextDisplay(
    display=display,
    font=font,
    title="ARMACHAT {:5.2f}MHz".format(config.freq),
    title_scale=1,
    text_scale=1,
    colors=(
        SimpleTextDisplay.GREEN,
        SimpleTextDisplay.WHITE,
        SimpleTextDisplay.WHITE,
        SimpleTextDisplay.WHITE,
        SimpleTextDisplay.WHITE,
        SimpleTextDisplay.WHITE,
        SimpleTextDisplay.WHITE,
        SimpleTextDisplay.WHITE,
        SimpleTextDisplay.RED,
    ),
)


print("Screen ready,Free memory:")
print(gc.mem_free())

to_dest_idx = 0
address_book = loadAddressBook()

print("address_book -> ", address_book)

broadcastAddressList = armachat_address.broadcastAddressList(config.myAddress,
                                                             config.groupMask)
broadcastAddress = \
    armachat_address.addressLst2Str(armachat_address.broadcastAddressList
                                    (config.myAddress, config.groupMask))

while True:
    screen[0].text = ">(" + str(config.myAddress) + ")" + config.myName
    screen[1].text = "[N] New message"
    screen[2].text = "[D] To:(" + address_book[to_dest_idx]["address"] + ")" \
        + address_book[to_dest_idx]["name"]
    screen[3].text = "[M] Memory - ALL:" + str(countMessages(""))
    screen[4].text = (
        "New:" + str(countMessages("|N|")) + " Undelivered:" + str(countMessages("|S|"))
    )
    screen[5].text = "[ ]          [I] HW Info"
    screen[6].text = "[ ]          [P] Ping"
    screen[7].text = "[T] Terminal [S] Setup"
    screen[8].text = "Ready ..."
    screen.show()
    beep()
    keypad = adafruit_matrixkeypad.Matrix_Keypad(config.rows, config.cols, config.keys1)

    sleepStart_time = time.monotonic()  # fraction seconds uptime
    message = ""
    while message == "":
        sleep_time = time.monotonic() - sleepStart_time
        # if (sleep_time > 10):
        # print ("Sleep in future ...")
        # BACKLIGHT.duty_cycle = 5000
        # time_alarm = alarm.time.TimeAlarm(monotonic_time=time.monotonic() + 3)
        # Deep sleep until the alarm goes off. Then restart the proram.
        # alarm.alarm.light_sleep_until_alarms(time_alarm)

        keys = keypad.pressed_keys
        # beep()
        # main LOOP
        message = receiveMessage()
        if not message == "":
            ring()
            ring()
        if keys:
            # BACKLIGHT.duty_cycle = 65535
            break
    if not keys:
        continue
    if keys[0] == "n":
        text = editor(text="")
        # Most likely there is a max length on the length of text/data
        # that may be sent. Once determined, change code to send chuncks/packets
        if not text == "":
            ring()
            sendMessage(text, armachat_address.getMessageId(msgCounter))
            message = receiveMessage()
            msgCounter += 1
            if(msgCounter > 255):
                msgCounter = 0
    if keys[0] == "d":
        to_dest_idx += 1
        if to_dest_idx > len(address_book)-1:
            to_dest_idx = 0
    if keys[0] == "m":
        showMemory()
        ring()
    if keys[0] == "a":
        SMPSmode.value = True
    if keys[0] == "b":
        SMPSmode.value = False
    if keys[0] == "e":
        try:
            with open("config.txt", "r") as f:
                lines = f.readlines()
                print("Printing lines in file:")
                count = 0
                for line in lines:
                    count += 1
                    print("Line{}: {}".format(count, line.strip()))
                # f.close()
        except OSError:
            print("config.txt does not exist")
    if keys[0] == "i":
        screen[0].text = "System info:"
        screen[1].text = "VSYS power = {:5.2f} V".format(get_VSYSvoltage())
        if VBUS_status.value:
            screen[2].text = "USB power connected"
        else:
            screen[2].text = "No USB power"
        fs_stat = os.statvfs("/")
        screen[3].text = "Disk size " + str(fs_stat[0] * fs_stat[2] / 1024) + " KB"
        screen[4].text = "Free space " + str(fs_stat[0] * fs_stat[3] / 1024) + " KB"
        screen[5].text = "CPU Temp: {:.2f} degrees C".format(
            microcontroller.cpu.temperature
        )
        screen[6].text = "-"
        screen[7].text = "-"
        screen[8].text = "Ready ..."
        ring()
        keys = keypad.pressed_keys
        while not keys:
            keys = keypad.pressed_keys
    if keys[0] == "s":
        ring()
        setup()
    if keys[0] == "t":
        screen.show_terminal()
        ring()
        keys = keypad.pressed_keys
        while not keys:
            keys = keypad.pressed_keys
    if config.model == "compact":
        if keys[0] == "q":
            KBL.value = True
            ring()
        if keys[0] == "a":
            KBL.value = False
            ring()
    # added a simple ping message
    if keys[0] == "p":
        beep()
        text = ""
        line = ["0", "1", "2", "3", "4", "5", "6"]
        line[0] = "Ping from >"
        line[1] = config.myName
        line[2] = ""
        line[3] = ""
        line[4] = ""
        line[5] = ""
        line[6] = ""
        for r in range(7):
            text = text + line[r] + "|"
        print("text: " + text)
        ring()
        sendMessage(text, armachat_address.getMessageId(msgCounter))
        message = receiveMessage()
        msgCounter += 1
        if msgCounter > 255:
            msgCounter = 0

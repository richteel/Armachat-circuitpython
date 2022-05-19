from armachat import config
from armachat import ac_address
from armachat import audio
from armachat import display
from armachat import keyboard
from armachat import lora

class ac_globals(object):
    def __init__(self):
        self.keypad = keyboard.keyboard()
        self.display = display.display()
        self.sound = audio.audio(self.keypad)
        self.radio = lora.lora()
        self.address_book = self.loadAddressBook()
        self.to_dest_idx = 0
        self.messages = []
        # self.model = config.model
    
    def loadAddressBook(self):
        broadcastAddressList = ac_address.broadcastAddressList(
            config.myAddress, config.groupMask
        )
        broadcastAddress = ac_address.addressLst2Str(broadcastAddressList)
        # destinations = "Sammy|12-36-124-8|Tom|12-36-124-17|Sandy|12-36-124-3"
        parts = config.destinations.split("|")
        retVal = [{"name": "All", "address": broadcastAddress}]

        if len(parts) % 2 != 0:
            return retVal
        for i in range(0, len(parts), 2):
            retVal += [{"name": parts[i], "address": parts[i + 1]}]
        return retVal
from armachat import config
from armachat import ac_address

class ac_globals(object):
    def __init__(self, display, keypad, sound, radio):
        self.display = display
        self.keypad = keypad
        self.sound = sound
        self.radio = radio
        self.address_book = self.loadAddressBook()
        self.to_dest_idx = 0
        self.messages = ["1|2|3|4|5|6|7|8|a1|a2|a3|a4|a5|a6|a7|a8"]
        self.model = config.model
    
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
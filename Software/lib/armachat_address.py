import re
import random


def addressToBytes(address, length=4):
    assert isinstance(address, str), \
        "ERROR: Address is not a string"

    try:
        q = addressToList(address)

        b = bytes(q)

        if b is not None and len(b) == length:
            return b
        else:
            # raise ValueError("ERROR in addressToBytes:
            #   Invalid address - Expected " + length + " bytes -> ", address)
            return None
    except ValueError:
        # raise ValueError("ERROR in addressToBytes:
        #   Invalid address - Invalid character -> ", address)
        return None

def addressToList(address, length=4):
    assert isinstance(address, str), \
        "ERROR: Address is not a string"

    try:
        regX = re.compile(",|\.|-|_|:|;")
        q = [int(x.strip()) for x in regX.split(address)]

        for s in q:
            if s < 0 or s > 255:
                # raise ValueError("ERROR in addressToList:
                #   Invalid address - Number not between 0 and 255 -> ", address)
                return None

        if len(q) == length:
            return q
        else:
            # raise ValueError("ERROR in addressToList:
            #   Invalid address - Expected " + length + " bytes -> ", address)
            return None
    except ValueError:
        # raise ValueError("ERROR in addressToList:
        #   Invalid address - Invalid character -> ", address)
        return None

def addressLst2Str(address):

    if len(address) != 4:
        return None

    retVal = ""

    for n in address:
        if len(retVal) > 0:
            retVal += "-"

        print("retVal -> ", retVal)

        retVal += str(n)

    return retVal

def broadcastAddressBytes(address, mask="255-255-255-0"):
    assert isinstance(address, str), \
        "ERROR: Address is not a string"

    a = addressToBytes(address)
    m = addressToBytes(mask)

    c = (int.from_bytes(a, 'big') &
         int.from_bytes(m, 'big')).to_bytes(max(len(a), len(m)), 'big')

    i = (~int.from_bytes(m, 'big', False) & 255).to_bytes(len(m), 'big')

    r = (int.from_bytes(c, 'big') |
         int.from_bytes(i, 'big')).to_bytes(max(len(c), len(i)), 'big')

    return r

def broadcastAddressList(address, mask="255-255-255-0"):
    assert isinstance(address, str), \
        "ERROR: Address is not a string"

    b = broadcastAddressBytes(address, mask)

    return [int(x) for x in b]

def broadcastAddressString(address, mask="255-255-255-0"):
    assert isinstance(address, str), \
        "ERROR: Address is not a string"

    s = ""

    for n in broadcastAddressList(address, mask):
        if len(s) > 0:
            s += "-"

        s += str(n)

    return s

def getMessageId(msgCount=0):
    return (str(random.randint(0, 255)) +
            "-" + str(random.randint(0, 255)) +
            "-" + str(random.randint(0, 255)) +
            "-" + str(msgCount)
            )




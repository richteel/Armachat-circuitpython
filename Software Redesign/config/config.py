import os

unitName = "ARMACHAT"
region = "Unset"
freq = 915.0
power = 23

'''
Matches Mestastic values in table at
https://meshtastic.org/docs/settings/channel
    1 => Bw500Cr45Sf128       Short/Fast
    2 => Bw125Cr45Sf128       Short/Slow
    3 => Bw250Cr47Sf1024      Medium/Fast
    4 => Bw250Cr46Sf2048      Medium/Slow
    5 => Bw31_25Cr48Sf512     Long/Fast
    6 => Bw125Cr48Sf4096      Long/Slow
'''

loraProfile = 1

myName = "DemoUser"

myAddress = "12-36-124-3"
groupMask = "255-255-255-0"
destinations = "Test 1|12-36-124-1|Test 2|12-36-124-2|Test 3|12-36-124-3"

hopLimit = 3

password = "Sixteen byte key"
passwordIv = "Sixteen byte key"
bright = 4
sleep = 0
font = 2
theme = 1

volume = 4
tone = 5000
melody = 0

'''
Models
    max
    compact
    watch
'''
model = "compact"

# ----------         End of Settings          ----------
# ---------- Start read/write config.txt file ----------

# File Open Modes
# r -> read
# rb -> read binary
# w -> write
# wb -> write binary
# a -> append
# ab -> append binary

CONFIG_FILENAME = "config.txt"

config_settings = set()
config_excludeNames = {
    "CONFIG_FILENAME",
    "__file__",
    "__name__",
    "maxChars",
    "maxLines",
    "model"
}
config_includeTypes = {
    float,
    int,
    str
}

loraProfiles = [
    {"profile": 1, "modemPreset": (0x92, 0x74, 0x04), "modemPresetConfig": "Bw500Cr45Sf128", "modemPresetDescription": "Short/Fast", "bw": 500},
    {"profile": 2, "modemPreset": (0x72, 0x74, 0x04), "modemPresetConfig": "Bw125Cr45Sf128", "modemPresetDescription": "Short/Slow", "bw": 125},
    {"profile": 3, "modemPreset": (0x82, 0xA4, 0x04), "modemPresetConfig": "Bw250Cr47Sf1024", "modemPresetDescription": "Medium/Fast", "bw": 250},
    {"profile": 4, "modemPreset": (0x84, 0xB4, 0x04), "modemPresetConfig": "Bw250Cr46Sf2048", "modemPresetDescription": "Medium/Slow", "bw": 250},
    {"profile": 5, "modemPreset": (0x48, 0x94, 0x04), "modemPresetConfig": "Bw31_25Cr48Sf512", "modemPresetDescription": "Long/Fast", "bw": 31.25},
    {"profile": 6, "modemPreset": (0x78, 0xC4, 0x0C), "modemPresetConfig": "Bw125Cr48Sf4096", "modemPresetDescription": "Long/Slow", "bw": 125},
]

regions = [
    {"region": "US", "freqCenter": 915, "freqStart": 902, "freqEnd": 928, "dutyCycle": 100, "spacing": 0, "powerLimit": 30},
    {"region": "EU433", "freqCenter": 433.5, "freqStart": 433, "freqEnd": 434, "dutyCycle": 10, "spacing": 0, "powerLimit": 12},
    {"region": "EU868", "freqCenter": 869.525, "freqStart": 869.4, "freqEnd": 869.65, "dutyCycle": 10, "spacing": 0, "powerLimit": 16},
    {"region": "CN", "freqCenter": 490, "freqStart": 470, "freqEnd": 510, "dutyCycle": 100, "spacing": 0, "powerLimit": 19},
    {"region": "JP", "freqCenter": 924.3, "freqStart": 920.8, "freqEnd": 927.8, "dutyCycle": 100, "spacing": 0, "powerLimit": 16},
    {"region": "ANZ", "freqCenter": 921.5, "freqStart": 915, "freqEnd": 928, "dutyCycle": 100, "spacing": 0, "powerLimit": 30},
    {"region": "RU", "freqCenter": 868.95, "freqStart": 868.7, "freqEnd": 869.2, "dutyCycle": 100, "spacing": 0, "powerLimit": 20},
    {"region": "KR", "freqCenter": 921.5, "freqStart": 920, "freqEnd": 923, "dutyCycle": 100, "spacing": 0, "powerLimit": 0},
    {"region": "TW", "freqCenter": 922.5, "freqStart": 920, "freqEnd": 925, "dutyCycle": 100, "spacing": 0, "powerLimit": 0},
    {"region": "IN", "freqCenter": 866, "freqStart": 865, "freqEnd": 867, "dutyCycle": 100, "spacing": 0, "powerLimit": 30},
    {"region": "NZ865", "freqCenter": 866, "freqStart": 864, "freqEnd": 868, "dutyCycle": 100, "spacing": 0, "powerLimit": 0},
    {"region": "TH", "freqCenter": 922.5, "freqStart": 920, "freqEnd": 925, "dutyCycle": 100, "spacing": 0, "powerLimit": 16},
    {"region": "Unset", "freqCenter": 915, "freqStart": 902, "freqEnd": 928, "dutyCycle": 100, "spacing": 0, "powerLimit": 30},
]

def printValue(name, val):
    print(name +" (", type, ") -> ", val)

def fileExists(fileName):
    retVal = False

    try:
        with open(fileName, "r") as f:
            f.readlines()
            retVal = True
    except OSError:
        print(fileName + " does not exist")

    return retVal


def fileSystemWriteMode():
    retVal = False
    testFileName = "delete.txt"

    try:
        with open(testFileName, "w") as f:
            f.write("test\n")
            retVal = True

        os.remove(testFileName)
    except OSError:
        print("config.py - Read Only File System")

    return retVal


def getConfigProperties():
    my_globals = globals()
    for g in my_globals:
        if g not in config_excludeNames:
            if type(globals()[g]) in config_includeTypes:
                config_settings.add(g)


# printConfigProperties is useful for debugging and may be removed
def printConfigProperties():
    i = 1
    for c in config_settings:
        # print(str(i) + chr(9) + c + chr(9) + str(globals()[c]))

        if str(type(globals()[c])) == "<class 'str'>":
            print(c + " = \"" + str(globals()[c]) + "\"")
        else:
            print(c + " = " + str(globals()[c]))
        i = i + 1


def readConfig(createIfNotExists=False):
    if len(config_settings) == 0:
        getConfigProperties()

    if not fileExists(CONFIG_FILENAME):
        if createIfNotExists:
            writeConfig()
        return False

    with open(CONFIG_FILENAME, "r") as f:
        conf = f.readlines()
        print("Reading config:")
        for line in conf:
            if line.strip().startswith("#"):  # Ignore comment
                continue

            keyvalPair = line.split("=")

            if(len(keyvalPair) != 2):  # Ignore not key value pair
                continue

            key = keyvalPair[0].strip()
            value = keyvalPair[1].strip()

            if key not in config_settings:  # Ignore key is not a setting
                continue

            if isinstance(globals()[key], str):
                if value.startswith("\"") and value.endswith("\""):
                    value = value[1:-1]
                globals()[key] = value
            elif isinstance(globals()[key], int):
                globals()[key] = int(value)
            elif isinstance(globals()[key], float):
                globals()[key] = float(value)

    return True


def writeConfig():
    if len(config_settings) == 0:
        getConfigProperties()

    # Create dict to track if items have been saved
    configTrackDict = {}
    for k in config_settings:
        configTrackDict[k] = False

    printValue("configTrackDict", configTrackDict)

    if not fileSystemWriteMode():
        print("Cannot write config file.")
        print("Enable Write mode on device boot.")
        return False

    # Recover from previous failure #
    # If the old config file exists, assume a failure last time.
    # Copy the old config file back and try again.
    # This will cause an issue if the original configuration file
    # was the source of the issue and the code has not changed to
    # address the issue.
    if fileExists(CONFIG_FILENAME + ".old"):
        if fileExists(CONFIG_FILENAME):
            os.remove(CONFIG_FILENAME)
        os.rename(CONFIG_FILENAME + ".old", CONFIG_FILENAME)

    # if the config file exists, rename it then delete it
    if fileExists(CONFIG_FILENAME):
        os.rename(CONFIG_FILENAME, CONFIG_FILENAME + ".old")
    
    
    with open(CONFIG_FILENAME, "w") as f_new:
        # if a previous config file exists, keep comments and formats for existing values
        if fileExists(CONFIG_FILENAME + ".old"):
            with open(CONFIG_FILENAME + ".old", "r") as f_old:
                    conf_old = f_old.readlines()
                    for line in conf_old:
                        if line.strip().startswith("#"):  # Comment
                            writeConfigLine(f_new, line)
                            continue

                        keyvalPair = line.split("=")
                        if(len(keyvalPair) != 2):  # Not key value pair
                            writeConfigLine(f_new, line)
                            continue

                        key = keyvalPair[0].strip()

                        if key not in config_settings:  # Ignore key is not a setting
                            writeConfigLine(f_new, line)
                        elif isinstance(globals()[key], str):
                            writeConfigLine(f_new, key + " = \"" + globals()[key] + "\"")
                            configTrackDict[key] = True
                        else:
                            writeConfigLine(f_new, key + " = " + str(globals()[key]))
                            configTrackDict[key] = True

        for dkey, dval in configTrackDict.items():
            if not dval:
                if isinstance(globals()[dkey], str):
                    writeConfigLine(f_new, dkey + " = \"" + globals()[dkey] + "\"")
                else:
                    writeConfigLine(f_new, dkey + " = " + str(globals()[dkey]))

    if fileExists(CONFIG_FILENAME + ".old"):
        os.remove(CONFIG_FILENAME + ".old")

    return True

def writeConfigLine(f, line):
    if line.endswith("\n"):
        f.write(line)
    else:
        f.write(line + "\n")


# print("--- Default Settings ---")
# printConfigProperties()
readConfig()
# print("--- Configuration File Settings ---")
# printConfigProperties()

# writeConfig()

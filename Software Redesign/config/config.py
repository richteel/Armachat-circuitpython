import os

unitName = "ARMACHAT"
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

volume = 2
tone = 5000
melody = 2

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
    {"profile": 1, "modemPreset": (0x92, 0x74, 0x04), "modemPresetConfig": "Bw500Cr45Sf128", "modemPresetDescription": "Short/Fast"},
    {"profile": 2, "modemPreset": (0x72, 0x74, 0x04), "modemPresetConfig": "Bw125Cr45Sf128", "modemPresetDescription": "Short/Slow"},
    {"profile": 3, "modemPreset": (0x82, 0xA4, 0x04), "modemPresetConfig": "Bw250Cr47Sf1024", "modemPresetDescription": "Medium/Fast"},
    {"profile": 4, "modemPreset": (0x84, 0xB4, 0x04), "modemPresetConfig": "Bw250Cr46Sf2048", "modemPresetDescription": "Medium/Slow"},
    {"profile": 5, "modemPreset": (0x48, 0x94, 0x04), "modemPresetConfig": "Bw31_25Cr48Sf512", "modemPresetDescription": "Long/Fast"},
    {"profile": 6, "modemPreset": (0x78, 0xC4, 0x0C), "modemPresetConfig": "Bw125Cr48Sf4096", "modemPresetDescription": "Long/Slow"},
]


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

    # Create dict to track if items have been saved
    configTrackDict = {}
    for k in config_settings:
        configTrackDict[k] = False

    with open(CONFIG_FILENAME + ".old", "r") as f_old:
        with open(CONFIG_FILENAME, "w") as f_new:
            conf_old = f_old.readlines()
            for line in conf_old:
                if line.strip().startswith("#"):  # Comment
                    if line.endswith("\n"):
                        f_new.write(line)
                    else:
                        f_new.write(line + "\n")
                    continue

                keyvalPair = line.split("=")
                if(len(keyvalPair) != 2):  # Not key value pair
                    if line.endswith("\n"):
                        f_new.write(line)
                    else:
                        f_new.write(line + "\n")
                    continue

                key = keyvalPair[0].strip()

                if key not in config_settings:  # Ignore key is not a setting
                    if line.endswith("\n"):
                        f_new.write(line)
                    else:
                        f_new.write(line + "\n")
                    continue

                if isinstance(globals()[key], str):
                    f_new.write(key + " = \"" + globals()[key] + "\"\n")
                    configTrackDict[key] = True
                else:
                    f_new.write(key + " = " + str(globals()[key]) + "\n")
                    configTrackDict[key] = True

            for dkey, dval in configTrackDict.items():
                if not dval:
                    if isinstance(globals()[dkey], str):
                        f_new.write(dkey + " = \"" + globals()[dkey] + "\"\n")
                    else:
                        f_new.write(dkey + " = " + str(globals()[dkey]) + "\n")

    if fileExists(CONFIG_FILENAME + ".old"):
        os.remove(CONFIG_FILENAME + ".old")

    return True


# print("--- Default Settings ---")
# printConfigProperties()
readConfig()
# print("--- Configuration File Settings ---")
# printConfigProperties()

# writeConfig()

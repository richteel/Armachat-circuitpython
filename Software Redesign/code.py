'''

'''

import gc
from armachat import ac_globals
from armachat import ui_hw_info
from armachat import ui_main
from armachat import ui_setup
from armachat import ui_splash
from armachat.ui_messages import ui_messages as ui_messages

import storage
import supervisor

ac_vars = ac_globals.ac_globals()
gui_splash = ui_splash.ui_splash(ac_vars)
gui_main = ui_main.ui_main(ac_vars)
gui_setup = ui_setup.ui_setup(ac_vars)
gui_hw_info = ui_hw_info.ui_hw_info(ac_vars)
gui_messages = ui_messages(ac_vars)

gui_splash.show()

# melody_list = sound.get_melodyNames()
# print(melody_list)

# sound.play_melody(len(melody_list) -1)
# melodyIdx = (len(melody_list) -1)
# sound.play_melody(melodyIdx)

# if not connected to USB, set the filesystem to read/write
if not supervisor.runtime.usb_connected:
    storage.remount("/", False)  # RW

while True:
    gc.collect()
    k = gui_main.show()

    # ['n', 'm', 'i', 'p', 's']
    if k["key"] == 'n':
        print("New Message")
    elif k["key"] == 'm':
        print("Show Messages")
        gui_messages.show()
    elif k["key"] == 'i':
        print("HW Information")
        gui_hw_info.show()
    elif k["key"] == 'p':
        print("Ping")
    elif k["key"] == 's':
        print("Setup")
        gui_setup.show()
    else:
        print("Unknown")
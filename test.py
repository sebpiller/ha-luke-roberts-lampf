import time

from custom_components.lukeroberts_lampf.lampf_bt import LampFBle, Scene

lampf = LampFBle(mac="C4:AC:05:42:73:A4").connect_if_needed()

lampf.scene = Scene.INDIRECT_SCENE
time.sleep(5)

lampf.color = [0xf0, 0x80, 0xf0]
time.sleep(5)

lampf.immediate_light(bottom_brightness=10, bottom_temperature=250, top_color=[0xff, 0x77, 0x77])

print("Done !")

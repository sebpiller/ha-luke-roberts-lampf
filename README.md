## Usage:
```yaml
lights:
  platform: lukeroberts-lampf
  mac: C4:AC:05:42:73:A4
  name: Lamp Living Room
```

## Configuration variables:
Field | Value | Necessity | Description
--- | --- | --- | ---
platform | `lukeroberts_lampf` | *Required* | The platform name.
mac | C4:AC:05:42:73:A4 | *Required* | Bluetooth MAC address of the lamp.
name | Lamp Living Room | Optional | Name of the Lamp.
***

## Host installation
```shell
sudo apt install bluetooth libbluetooth-dev
python3 -m pip install pybluez
```

## Sample code for LR Lamp F

```python
import time
from custom_components.lukeroberts_lampf.lampf_bt import LampFBle, Scene

lampf = LampFBle("C4:AC:05:42:73:A4").connect_if_needed()

lampf.scene = Scene.INDIRECT_SCENE
time.sleep(5)

lampf.color = [0xf0, 0x80, 0xf0]
time.sleep(5)

lampf.immediate_light(bottom_brightness=10, bottom_temperature=2900, top_color=[0xff, 0x77, 0x77])

print("Done !")
```
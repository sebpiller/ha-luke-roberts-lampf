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
platform | `lukeroberts-lampf` | *Required* | The platform name.
mac | C4:AC:05:42:73:A4 | *Required* | Bluetooth MAC address of the lamp.
name | Lamp Living Room | Optional | Name of the Lamp.
***

## Host installation
```shell
sudo apt install bluetooth libbluetooth-dev
python3 -m pip install pybluez
```
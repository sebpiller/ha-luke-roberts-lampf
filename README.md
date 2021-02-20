[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg?style=for-the-badge)](https://github.com/custom-components/hacs)

## Usage:
```yaml
fan:
  platform: philips-airpurifier
  host: 192.168.0.17
  protocol: 2
```

## Configuration variables:
Field | Value | Necessity | Description
--- | --- | --- | ---
platform | `philips-airpurifier` | *Required* | The platform name.
host | 192.168.0.17 | *Required* | IP address of your Purifier.
name | Philips Air Purifier | Optional | Name of the Fan.
protocol | 2 | Optional | Protocol version (1=HTTP, 2=PLAIN COAP 3=COAP encrypted)
***

"""Luke Roberts Lamp F"""
import colorsys
import logging
from enum import Enum
from typing import Callable, List

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from bluepy.btle import Peripheral, ADDR_TYPE_RANDOM, UUID, Characteristic
from homeassistant.components.light import (
    ATTR_BRIGHTNESS, PLATFORM_SCHEMA, LightEntity, SUPPORT_BRIGHTNESS)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_NAME
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.typing import HomeAssistantType

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = "Luke Roberts Lamp F"
# ICON = "mdi:light"

# Validation of the user's configuration
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST): cv.string,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    # vol.Optional(CONF_PASSWORD): cv.string,
})


def _async_create_entities(hass, config):
    _LOGGER.warning("_async_create_entities " + hass + " " + config)
    host = config[CONF_HOST]
    name = config[CONF_NAME]
    _LOGGER.warning("   host: " + host + ", name: " + name)
    lights = [LampFLight(LampFBle(host, name))]
    return lights


async def async_setup_entry(
        hass: HomeAssistantType,
        entry: ConfigEntry,
        async_add_entities: Callable[[List[Entity], bool], None],
) -> None:
    _LOGGER.warning("async_setup_entry " + hass + " " + entry)
    async_add_entities(await _async_create_entities(hass, entry), True)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    _LOGGER.warning("async_setup_platform " + hass + " " + config)
    async_add_entities(await _async_create_entities(hass, config))


def setup_platform(hass, config, add_entities, discovery_info=None):
    _LOGGER.warning("setup_platform " + hass + " " + config)
    add_entities(await _async_create_entities(hass, config))


class Scene(Enum):
    """ Scenes from the default Luke Roberts configuration. """
    DEFAULT_SCENE = 0xFF
    SHUTDOWN_SCENE = 0x00
    READING_SCENE = 0x06
    CANDLE_LIGHT_SCENE = 0x04
    SHINY_SCENE = 0x03
    WELCOME_SCENE = 0x01
    INDIRECT_SCENE = 0x05
    HIGHLIGHTS_SCENE = 0x02
    BRIGHT_SCENE = 0x07


class LampFBle:
    """
    A wrapper class that connects a "Luke Roberts - Lamp F" with Bluetooth Low Energy and send commands to it.
    Lazily connects to the lamp if not done.
    """

    def __init__(self, mac="C4:AC:05:42:73:A4"):
        _LOGGER.info('building LampFBle...')

        """ Constructor. """
        self._mac = mac
        self._peripheral = Peripheral()

        self.__charac = None
        self.__bottom_temperature = 3400  # assume a default value
        self.__bottom_brightness = 10  # assume a default value

        self._connected = False
        self._power = False
        self._scene = None
        self._color = None

    def __del__(self):
        """ Destructor. Try to disconnect before recycling this object. """
        print("destructor " + str(self))
        self.disconnect()

    def connect_if_needed(self):
        """ Connects the Bluetooth Lamp if not done yet. """
        if not self._connected:
            self._peripheral.connect(addr=self._mac, iface=0, addrType=ADDR_TYPE_RANDOM)
            self._connected = True
            print("Connected to {}.".format(self._mac))
        return self

    def disconnect(self):
        """ Cleanly disconnect the currently connected lamp. """
        self._connected = False
        self._peripheral.disconnect()
        return self

    def _fetch_charac(self,
                      svc_uuid: UUID = UUID("44092840-0567-11e6-b862-0002a5d5c51b"),
                      charac_uuid: UUID = UUID("44092842-0567-11e6-b862-0002a5d5c51b")
                      ) -> Characteristic:
        """
        Searches a characteristic on the connected bluetooth peripheral. By default, it fetches the characteristic
        corresponding to the External API endpoint of Luke Roberts Lamp F.

        @param svc_uuid: A connected peripheral's service UUID.
        @param charac_uuid: A connected peripheral's characteristic UUID.
        """
        svcs = self._peripheral.discoverServices()
        svc = svcs.get(svc_uuid)
        # print(svc)

        charac = svc.getCharacteristics(charac_uuid).pop()
        # print(charac)

        print("found characteristic: {}".format(charac))
        return charac

    def send_command(self, i: List):
        """ Sends a command to the standard characteristic of the device. """
        self.connect_if_needed()

        # transform integer passed in argument to bytes
        b = list(map(lambda val: val.to_bytes(1, byteorder='big'), i))
        bs = b''.join(b)  # funny syntax
        self._charac.write(bs, False)
        return self

    # ----------

    @property
    def _charac(self):
        if self.__charac is None:
            self.__charac = self._fetch_charac()

        return self.__charac

    # ----------

    @property
    def power(self):
        return self._power

    @power.setter
    def power(self, power):
        print("setting power to " + str(power))
        self.scene = Scene.DEFAULT_SCENE if power else Scene.SHUTDOWN_SCENE

    # ----------

    @property
    def scene(self) -> Scene:
        return self._scene

    @scene.setter
    def scene(self, s: Scene = Scene.SHUTDOWN_SCENE):
        ss = s if s is not None else Scene.SHUTDOWN_SCENE
        print("setting scene to " + repr(ss))
        self.send_command([0xA0, 0x02, 0x05, ss.value, ])
        self._scene = ss
        self._power = ss is not Scene.SHUTDOWN_SCENE

    # ----------

    @property
    def temperature(self) -> int:
        return self.__bottom_temperature

    @temperature.setter
    def temperature(self, val: int = 4000):
        s = min(max(2700, val), 4000)
        print("setting temperature to " + str(s))
        x = val.to_bytes(2, byteorder='big')
        self.send_command([0xA0, 0x02, 0x04, x[0], x[1]])
        self.__bottom_temperature = s

    # ----------

    @property
    def color(self) -> List[int]:
        return self._color

    @color.setter
    def color(self, color=None):
        if color is None:
            color = [0xFF, 0xFF, 0xFF]
        self.immediate_light(top_color=color)

    # ----------

    @property
    def bottom_temperature(self) -> int:
        return self.__bottom_temperature

    @bottom_temperature.setter
    def bottom_temperature(self, tt: int):
        self.immediate_light(bottom_temperature=tt)

    @property
    def bottom_brightness(self) -> int:
        return self.__bottom_brightness

    @bottom_brightness.setter
    def bottom_brightness(self, b: int):
        self.immediate_light(bottom_brightness=b)

    # -----------

    def immediate_light(self,
                        top_color: List[int] = None, top_temperature: int = None,
                        bottom_temperature: int = None, bottom_brightness: int = None):
        """
        Use the service immediateLight to set the color of the top bulb and/or the brightness and temperatures of
        the main bulb.

          - If all arguments are null, then this method does nothing.
          - If the top_color or top_temperature are defined, then the actual color of the top bulb will be modified
            accordingly.
          - If the top_color is provided, it takes precedence over the top_temperature argument, unless
            the top_color has a 0-saturation value after converted to HSL color space (typically, black color).
          - If the bottom_temperature or bottom_brightness are provided, the main bulb will be modified accordingly. If
            not both arguments are provided, then the value of the other will stay unchanged. Be careful, before the
            first call of this method, all values are undefined.
        :param top_color: Color of the top bulb.
        :param top_temperature: Temperature of the top bulb.
        :param bottom_temperature: Temperature of the main bulb.
        :param bottom_brightness: Brightness of the main bulb.
        :returns: self for chaining
        """
        hue = 0
        bri = 0
        sat = 0
        bt = None
        bb = None
        r = None
        g = None
        b = None

        change_top_block = False  # do we need to alter the top bulb values ?
        change_bottom_block = False  # do we need to alter the bottom bulb values ?

        # --- If we are changing the color of the top bulb
        if top_color is not None:
            if len(top_color) != 3:
                raise ValueError(
                    "color must contain 3 int in range 0..255 (actual: {} elements provided)".format(len(top_color)))

            change_top_block = True
            r = min(max(0, top_color[0]), 0xFF)
            g = min(max(0, top_color[1]), 0xFF)
            b = min(max(0, top_color[2]), 0xFF)

            # to HLS (Hue Lighting Saturation) color space
            hls = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)

            hue = int(hls[0] * 65535)
            bri = int(hls[1] * 255)
            sat = int(hls[2] * 255)

        # When sat is 0 (eg. r=0,g=0,b=0), hue parameter becomes a color temperature
        if top_temperature is not None:
            change_top_block = True
            if sat == 0:
                hue = top_temperature
            else:
                # if saturation is not 0, we ignore the temperature
                pass

        if sat == 0:
            self._color = None
        else:
            self._color = [r, g, b]

        # --- If we are changing the main bulb settings
        if bottom_temperature is not None:
            bt = min(max(2700, bottom_temperature), 4000)
            change_bottom_block = True
        if bottom_brightness is not None:
            bb = bottom_brightness
            change_bottom_block = True

        if change_bottom_block:
            if bt is None:
                bt = self.__bottom_temperature
            if bb is None:
                bb = self.__bottom_brightness

        # --- Build and send the command bytes
        # command content
        if change_top_block and change_bottom_block:
            command_content = 0x03
        elif change_top_block:
            command_content = 0x01
        elif change_bottom_block:
            command_content = 0x02
        else:
            # No-Op
            return

        command = [0xA0, 0x01, 0x02, command_content]
        # duration (forever at the moment)
        command.append(0x00)
        command.append(0x00)

        if change_top_block:
            # Block uplight
            hues = hue.to_bytes(2, byteorder='big')
            command.append(sat)  # saturation
            command.append(hues[0])  # color or temperature for top bulb
            command.append(hues[1])  # color or temperature for top bulb
            command.append(bri)  # brightness

        if change_bottom_block:
            # Block downlight
            bts = bt.to_bytes(2, byteorder='big')
            command.append(bts[0])  # main bulb temperature
            command.append(bts[1])  # main bulb temperature
            command.append(bb)  # main bulb brightness
            self.__bottom_temperature = bt
            self.__bottom_brightness = bb

        self.send_command(command)
        self._scene = None  # no specific scene anymore
        self._power = True  # we can not shutdown the lamp with immediate_light
        return self


class LampFLight(LightEntity):
    """Representation of an Awesome Li§ght."""

    def __init__(self, lampf: LampFBle, name):
        # super().__init__(
        #     availability_template=availability_template,
        #     icon_template=icon_template,
        #     entity_picture_template=entity_picture_template,
        # )

        _LOGGER.warning("creating LampFLight entity ")
        """Initialize an AwesomeLight."""
        self._light = lampf
        self._name = name
        self._state = False
        self._brightness = 0
        self.update()

    @property
    def name(self):
        """Return the display name of this light."""
        return self._name

    # brightness	int	None	Return the brightness of this light between 0..255
    # color_temp	int	None	Return the CT color value in mireds.
    # effect	String	None	Return the current effect.
    # effect_list	list	None	Return the list of supported effects.
    # hs_color	list	None	Return the hue and saturation color value [float, float].
    # is_on	bool	bool	Returns if the light entity is on or not.
    # max_mireds	int	int	Return the warmest color_temp that this light supports.
    # min_mireds	int	int	Return the coldest color_temp that this light supports.
    # supported_features	int	int	Flag supported features.
    # white_value	int	None	Return the white value of this light between 0..255.

    @property
    def brightness(self):
        """Return the brightness of the light.
        This method is optional. Removing it indicates to Home Assistant
        that brightness is not supported for this light.
        """
        return self._brightness

    @brightness.setter
    def brightness(self, b):
        self._light.bottom_brightness = b
        self._brightness = b

    @property
    def is_on(self):
        """Return true if light is on."""
        return self._state

    def turn_on(self, **kwargs):
        """Instruct the light to turn on.
        You can skip the brightness part if your light does not support
        brightness control.
        """
        self._light.power = True
        self._state = True
        self.brightness = kwargs.get(ATTR_BRIGHTNESS, 255)

    def turn_off(self, **kwargs):
        """Instruct the light to turn off."""
        self._state = False
        self._light.power = False

    # async def async_turn_on(self, **kwargs):
    #     """Turn device on."""
    #
    # async def async_turn_off(self, **kwargs):
    #     """Turn device off."""

    def update(self):
        """Fetch new state data for this light.
        This is the only method that should fetch new data for Home Assistant.
        """
        try:
            # self._light.update()
            self._state = self._light.power
            self._brightness = self._light.bottom_brightness
        except Exception as e:
            print(type(e))
            print(e.args)
            print(e)
            print("End of try of update!")

    @property
    def supported_features(self):
        """Flag supported features."""
        supports = SUPPORT_BRIGHTNESS
        # supports |= SUPPORT_COLOR
        # supports |= SUPPORT_COLOR_TEMP
        # supports |= SUPPORT_EFFECT
        # supports |= SUPPORT_FLASH
        # supports |= SUPPORT_TRANSITION
        return supports

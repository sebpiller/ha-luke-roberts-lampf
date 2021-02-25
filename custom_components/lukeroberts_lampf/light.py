"""Luke Roberts Lamp F"""

import logging

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
# Import the device class from the component that you want to support
from homeassistant.components.light import (
    ATTR_BRIGHTNESS, PLATFORM_SCHEMA, LightEntity, SUPPORT_BRIGHTNESS, SUPPORT_COLOR_TEMP, SUPPORT_COLOR,
    SUPPORT_EFFECT, SUPPORT_FLASH, SUPPORT_TRANSITION)
from homeassistant.const import CONF_HOST

from .lampf_bt import LampFBle

_LOGGER = logging.getLogger(__name__)

# Validation of the user's configuration
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST): cv.string,
    # vol.Optional(CONF_USERNAME, default='admin'): cv.string,
    # vol.Optional(CONF_PASSWORD): cv.string,
})


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up Tuya light platform."""
    if discovery_info is None:
        return
    """Set up the Awesome Light platform."""
    # Assign configuration variables.
    # The configuration check takes care they are present.
    host = config[CONF_HOST]
    # username = config[CONF_USERNAME]
    # password = config.get(CONF_PASSWORD)

    # Setup connection with devices/cloud
    # hub = awesomelights.Hub(host, username, password)

    # Verify that passed in configuration works
    # if not hub.is_valid_login():
    #     _LOGGER.error("Could not connect to AwesomeLight hub")
    #     return

    # Add devices
    add_entities(LampFLight(LampFBle()))


class LampFLight(LightEntity):
    """Representation of an Awesome Li§ght."""

    def __init__(self, lampf: LampFBle):
        """Initialize an AwesomeLight."""
        self._light = lampf
        self._name = "LampF"
        self._state = None
        self._brightness = None

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
        self.brightness = kwargs.get(ATTR_BRIGHTNESS, 255)

    def turn_off(self, **kwargs):
        """Instruct the light to turn off."""
        self._light.power = False

    async def async_turn_on(self, **kwargs):
        """Turn device on."""

    async def async_turn_off(self, **kwargs):
        """Turn device off."""

    def update(self):
        """Fetch new state data for this light.
        This is the only method that should fetch new data for Home Assistant.
        """
        self._light.update()
        self._state = self._light.power
        self._brightness = self._light.bottom_brightness

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

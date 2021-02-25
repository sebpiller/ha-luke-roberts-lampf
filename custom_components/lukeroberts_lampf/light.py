"""Luke Roberts Lamp F"""

import logging

import voluptuous as vol

import homeassistant.helpers.config_validation as cv
# Import the device class from the component that you want to support
from homeassistant.components.light import (
    ATTR_BRIGHTNESS, PLATFORM_SCHEMA, LightEntity)
from homeassistant.const import CONF_HOST
import awesomelights

from .lampf_bt import LampFBle

_LOGGER = logging.getLogger(__name__)

# Validation of the user's configuration
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST): cv.string,
    # vol.Optional(CONF_USERNAME, default='admin'): cv.string,
    # vol.Optional(CONF_PASSWORD): cv.string,
})


def setup_platform(hass, config, add_entities, discovery_info=None):
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
    add_entities(LampFLight(light) for light in hub.lights())


class LampFLight(LightEntity):
    """Representation of an Awesome Li§ght."""

    def __init__(self):
        """Initialize an AwesomeLight."""
        self._light = LampFBle()
        self._name = "dfgsdg"
        self._state = None
        self._brightness = None

    @property
    def name(self):
        """Return the display name of this light."""
        return self._name

    @property
    def brightness(self):
        """Return the brightness of the light.
        This method is optional. Removing it indicates to Home Assistant
        that brightness is not supported for this light.
        """
        # return self._brightness
        return self._light.bottom_brightness

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
        self._light.bottom_brightness = kwargs.get(ATTR_BRIGHTNESS, 255)

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

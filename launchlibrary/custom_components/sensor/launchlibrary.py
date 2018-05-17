"""
A component which allows you to get information about next launches
For more details about this component, please refer to the documentation at
https://github.com/HalfDecent/HA-Custom_components/launchlibrary
"""
import requests
import voluptuous as vol
from datetime import timedelta
from homeassistant.helpers.entity import Entity

ATTR_STREAM = 'stream'
ATTR_LAUNCH_NAME = 'launch name'

SCAN_INTERVAL = timedelta(seconds=60)

def setup_platform(hass, config, add_devices, discovery_info=None):
    dev = []
    dev.append(ExampleSensor('mdi:rocket'))
    add_devices(dev, True)

class ExampleSensor(Entity):
    """Representation of a Sensor."""

    def __init__(self, icon):
        """Initialize the sensor."""
        self._state = None
        self._icon = icon

    def update(self):
        baseurl = "https://launchlibrary.net/1.4/"
        fetchurl = baseurl + 'launch/next/1'
        launch = requests.get(fetchurl).json()['launches'][0]
        self._state = launch["windowstart"]
        self._launchname = launch["name"]
        self._launchstream = launch["vidURLs"][0]

    @property
    def name(self):
        return 'nextlaunch'

    @property
    def state(self):
        return self._state

    @property
    def icon(self):
        return self._icon

    @property
    def device_state_attributes(self):
        return {
            ATTR_LAUNCH_NAME: self._launchname,
            ATTR_STREAM: self._launchstream
        }
"""
A component which allows you to get information about next departure from spesified stop.
For more details about this component, please refer to the documentation at
https://github.com/HalfDecent/HA-Custom_components/ruter
"""
import logging
import requests
import dateutil.parser
import voluptuous as vol
from datetime import timedelta
from homeassistant.helpers.entity import Entity
import homeassistant.helpers.config_validation as cv
from homeassistant.components.switch import (PLATFORM_SCHEMA)

CONF_STOPID = 'stopid'

ATTR_DESTINATION = 'destination'
ATTR_LINE = 'line'
ATTR_COMPONENT = 'component'
ATTR_STOPID = 'stopid'

SCAN_INTERVAL = timedelta(seconds=10)

ICON = 'mdi:bus'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_STOPID): cv.string,
})

_LOGGER = logging.getLogger(__name__)

def setup_platform(hass, config, add_devices, discovery_info=None):
    stopid = config.get(CONF_STOPID)
    add_devices([RuterSensor(stopid)])

class RuterSensor(Entity):
    def __init__(self, stopid):
        self._state = None
        self._line = None
        self._destination = None
        self._stopid = stopid
        self._component = 'ruter'

    def update(self):
        baseurl = "http://reisapi.ruter.no/StopVisit/GetDepartures/"
        fetchurl = baseurl + self._stopid
        try:
            departure = requests.get(fetchurl, timeout=3).json()[0]
        except:
            _LOGGER.debug("Error fetching new state")
        else:
            self._line = departure['MonitoredVehicleJourney']['LineRef']
            self._destination = departure['MonitoredVehicleJourney']['DestinationName']
            time = departure['MonitoredVehicleJourney']['MonitoredCall']['ExpectedDepartureTime']
            deptime = dateutil.parser.parse(time)
            self._state = deptime.strftime("%H:%M")


    @property
    def name(self):
        return 'ruter'

    @property
    def state(self):
        return self._state

    @property
    def icon(self):
        return ICON

    @property
    def device_state_attributes(self):
        return {
            ATTR_LINE: self._line,
            ATTR_DESTINATION: self._destination,
            ATTR_COMPONENT: self._component,
            ATTR_STOPID: self._stopid
        }
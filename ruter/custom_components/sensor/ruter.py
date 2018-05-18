"""
A component which allows you to get information about next departure from spesified stop.
For more details about this component, please refer to the documentation at
https://github.com/HalfDecent/HA-Custom_components/ruter
"""
import requests
import voluptuous as vol
from datetime import timedelta
from homeassistant.helpers.entity import Entity
import homeassistant.helpers.config_validation as cv
from homeassistant.components.switch import (PLATFORM_SCHEMA)

CONF_STOPID = 'stopid'

ATTR_TIME = 'DepartureTime'
ATTR_COMPONENT = 'component'
ATTR_STOPID = 'stopid'

SCAN_INTERVAL = timedelta(seconds=5)

ICON = 'mdi:bus'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_STOPID): cv.string,
})

def setup_platform(hass, config, add_devices, discovery_info=None):
    stopid = config.get(CONF_STOPID)
    add_devices([RuterSensor(stopid)])

class RuterSensor(Entity):
    def __init__(self, stopid):
        self._state = None
        self._time = None
        self._stopid = stopid
        self._component = 'ruter'

    def update(self):
        baseurl = "http://reisapi.ruter.no/StopVisit/GetDepartures/"
        fetchurl = baseurl + self._stopid
        departure = requests.get(fetchurl).json()[0]
        line = departure['MonitoredVehicleJourney']['LineRef']
        destination = departure['MonitoredVehicleJourney']['DestinationName']
        time = departure['MonitoredVehicleJourney']['MonitoredCall']['ExpectedDepartureTime']
        self._state = line + ' ' + destination
        self._time = time


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
            ATTR_TIME: self._time,
            ATTR_COMPONENT: self._component,
            ATTR_STOPID: self._stopid
        }
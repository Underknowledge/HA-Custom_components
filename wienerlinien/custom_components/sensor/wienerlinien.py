"""
A component which allows you to get information about next departure from spesified stop.
For more details about this component, please refer to the documentation at
https://github.com/HalfDecent/HA-Custom_components/wienerlinien
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
CONF_APIKEY = 'apikey'

ATTR_STOPID = 'stopid'
ATTR_NEXT_DEPARTURE = 'next_departure'
ATTR_COMPONENT = 'component'
ATTR_COMPONENT_VERSION = 'component_version'

SCAN_INTERVAL = timedelta(seconds=30)

ICON = 'mdi:bus'
COMPONENT_NAME = 'wienerlinien'
COMPONENT_VERSION = '1.0.1'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_STOPID): cv.string,
    vol.Required(CONF_APIKEY): cv.string,
})

BASE_URL = 'http://www.wienerlinien.at/ogd_realtime/monitor'

_LOGGER = logging.getLogger(__name__)

def setup_platform(hass, config, add_devices, discovery_info=None):
    stopid = config.get(CONF_STOPID)
    apikey = config.get(CONF_APIKEY)
    add_devices([WienerlinienSensor(stopid, apikey)])

class WienerlinienSensor(Entity):
    def __init__(self, stopid, apikey):
        self._state = 'N/A'
        self._nextdeparture = 'N/A'
        self._stopid = stopid
        self._apikey = apikey
        self._component = COMPONENT_NAME
        self._componentversion = COMPONENT_VERSION

    def update(self):
        fetchurl = BASE_URL + '?rbl=' + self._stopid + '&sender=' + self._apikey
        try:
            departure = requests.get(fetchurl, timeout=5).json()['data']
        except:
            _LOGGER.debug("Error fetching new state")
        else:
            try:
                departure['monitors'][0]['lines'][0]['departures']['departure'][0]['departureTime']['countdown']
            except:
                countdown = 'N/A'
                nextDeparture = 'N/A'
            else:
                countdown = departure['monitors'][0]['lines'][0]['departures']['departure'][0]['departureTime']['countdown']
                nextDeparture = departure['monitors'][0]['lines'][0]['departures']['departure'][1]['departureTime']['countdown']
            self._state = countdown
            self._nextdeparture = nextDeparture


    @property
    def name(self):
        return 'Wienerlinien - Departure'

    @property
    def state(self):
        return self._state

    @property
    def icon(self):
        return ICON

    @property
    def unit_of_measurement(self):
        return 'min(s)'

    @property
    def device_state_attributes(self):
        return {
            ATTR_NEXT_DEPARTURE: self._nextdeparture,
            ATTR_STOPID: self._stopid,
            ATTR_COMPONENT: self._component,
            ATTR_COMPONENT_VERSION: self._componentversion
        }
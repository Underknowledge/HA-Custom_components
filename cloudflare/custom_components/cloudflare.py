"""
A component which allows you to update the IP adderesses of your Cloudflare DNS records.
For more details about this component, please refer to the documentation at
https://github.com/HalfDecent/HA-Custom_components/cloudflare
"""
import time
import json
import asyncio
import logging
import requests
import voluptuous as vol
from datetime import timedelta
from homeassistant.helpers.entity import Entity
from homeassistant.loader import bind_hass
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.aiohttp_client import async_get_clientsession

DOMAIN = 'cloudflare'

CONF_EMAIL = 'email'
CONF_KEY = 'key'
CONF_ZONE = 'zone'
CONF_RECORDS = 'records'

INTERVAL = timedelta(minutes=60)
SERVICE_UPDATE = 'update_records'

COMPONENT_NAME = 'cloudflare'
COMPONENT_VERSION = '1.0.0'
BASE_URL = 'https://api.cloudflare.com/client/v4/zones'
EXT_IP_URL = 'https://api.ipify.org'

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_EMAIL): cv.string,
        vol.Required(CONF_KEY): cv.string,
        vol.Required(CONF_ZONE): cv.string,
        vol.Optional(CONF_RECORDS, default='None'): 
            vol.All(cv.ensure_list, [cv.string]),
})
}, extra=vol.ALLOW_EXTRA)

_LOGGER = logging.getLogger(__name__)

@bind_hass
@asyncio.coroutine
def async_setup(hass, config):
    email = config[DOMAIN][CONF_EMAIL]
    key = config[DOMAIN][CONF_KEY]
    zone = config[DOMAIN][CONF_ZONE]
    records = config[DOMAIN][CONF_RECORDS]
    session = async_get_clientsession(hass)

    @asyncio.coroutine
    def update_domain_interval(now):
        """Update the Cloudflare entry."""
        _update_cloudflare(session, email, key, zone, records)

    @asyncio.coroutine
    def update_domain_service(call):
        """Update the Cloudflare entry."""
        _update_cloudflare(session, email, key, zone, records)

    async_track_time_interval(hass, update_domain_interval, INTERVAL)
    hass.services.async_register(
        DOMAIN, SERVICE_UPDATE, update_domain_service)
    return True

def _update_cloudflare(session, email, key, zone, records):
    _LOGGER.info('Starting update for zone %s', zone)
    IP = requests.get(EXT_IP_URL).text
    headers = {'X-Auth-Email': email, 'X-Auth-Key': key , 'Content-Type': 'application/json'}
    zoneIDurl = BASE_URL + '?name=' + zone
    zoneID = requests.get(zoneIDurl, headers=headers).json()['result'][0]['id']
    if 'None' in records:
        _LOGGER.debug('Records not defined, scanning for records...')
        getRecordsUrl = BASE_URL + '/' + zoneID + '/dns_records&per_page=100'
        getRecords = requests.get(getRecordsUrl, headers=headers).json()['result']
        dev = []
        num = 0
        for items in getRecords:
            recordName = getRecords[num]['name']
            dev.append(recordName)
            num = num + 1
        records = dev
    for record in records:
        if zone in record:
            RecordFullname = record
        else:
            RecordFullname = record + '.' + zone
        _LOGGER.info('Updating record %s', RecordFullname)
        recordIDurl = BASE_URL + '/' + zoneID + '/dns_records?name=' + RecordFullname
        recordInfo = requests.get(recordIDurl, headers=headers, timeout=10).json()['result'][0]
        RecordID = recordInfo['id']
        RecordType = recordInfo['type']
        RecordProxy = str(recordInfo['proxied'])
        if RecordProxy == 'True':
            proxied = True
        else:
            proxied = False
        data = json.dumps({'id': zoneID, 'type': RecordType, 'name': RecordFullname, 'content': IP, 'proxied': proxied})
        fetchurl = BASE_URL + '/' + zoneID + '/dns_records/' + RecordID
        if RecordType == 'A':
            result = requests.put(fetchurl, headers=headers, data=data).json()
            _LOGGER.debug('Update successfully: %s', result['success'])
        else:
            _LOGGER.debug('Record type for %s is not A, skipping update', RecordFullname)
        _LOGGER.info('Update for zone %s is complete.', zone)
    return str(True)

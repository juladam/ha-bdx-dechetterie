from datetime import timedelta
import logging

import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity
import requests

from .const import ( CONF_IDENT, ATTR_STATUS, ATTR_HORAIRES, ATTR_NOM)

_LOGGER = logging.getLogger(__name__)

DOMAIN = 'bdx_dechetterie'
SCAN_INTERVAL = timedelta(seconds=30*60)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_IDENT, default='1'): cv.string
})



def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the Dechetterie platform."""
    entities = [DechetterieEntity(config)]
    add_entities(entities, True)


class DechetterieEntity(Entity):
    """Dechetterie Entity."""

    def __init__(self, config):
        """Init the Dechetterie Entity."""
        self._attr = {
            ATTR_NOM: {},
            ATTR_STATUS: {},
            ATTR_HORAIRES: {}
        }

        self.ident = config[CONF_IDENT]

    def update(self):
        """Update data."""
        self._attr = {
            ATTR_NOM: {},
            ATTR_STATUS: {},
            ATTR_HORAIRES: {}
        }

        url = "https://opendata.bordeaux-metropole.fr/api/explore/v2.1/catalog/datasets/dechetteries-en-temps-reel/records?limit=20"

        response = requests.get(url)
        data = response.json()
        for result in data['results']:
            if result['gid'] == self.ident:
                self._attr[ATTR_NOM] = result['nom']
                self._attr[ATTR_STATUS] = result['statut']
                horaires = result['horaires_osm']
                horaires_list = horaires.split('; ')
                horaires_dict = {}
                for horaire in horaires_list:
                    day, hours = horaire.split(' ')
                    day_mapping = {
                        'Mo': 'Lundi',
                        'Tu': 'Mardi',
                        'We': 'Mercredi',
                        'Th': 'Jeudi',
                        'Fr': 'Vendredi',
                        'Sa': 'Samedi',
                        'Su': 'Dimanche'
                    }
                    day = day_mapping.get(day, day)
                    hours_list = hours.split(',')
                    horaires_dict[day] = hours_list
                self._attr[ATTR_HORAIRES] = horaires_dict
                break

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._attr[ATTR_NOM]

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._attr[ATTR_STATUS]

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return self._attr

    @property
    def icon(self):
        """Return the icon to use in the frontend."""
        return 'mdi:recycle'

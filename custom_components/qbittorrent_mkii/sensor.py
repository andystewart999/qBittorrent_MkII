"""Support for monitoring the qBittorrent API."""
from __future__ import annotations

import logging

import qbittorrentapi
from qbittorrentapi import Client, LoginFailed, APIConnectionError
from requests.exceptions import RequestException, ConnectTimeout
import voluptuous as vol

from homeassistant.components.sensor import (
    PLATFORM_SCHEMA,
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.config_entries import SOURCE_IMPORT, ConfigEntry
from homeassistant.const import (
    CONF_NAME,
    CONF_PASSWORD,
    CONF_URL,
    CONF_USERNAME,
    CONF_SCAN_INTERVAL,
    STATE_IDLE,
    UnitOfDataRate,
    UnitOfTime
)
from homeassistant.core import DOMAIN as HOMEASSISTANT_DOMAIN, HomeAssistant
from homeassistant.helpers import issue_registry as ir
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .const import *
from .helpers import get_version
from urllib.parse import urlparse

_LOGGER = logging.getLogger(__name__)

SENSOR_TYPE_CURRENT_STATUS = "current_status"
SENSOR_TYPE_DOWNLOAD_SPEED = "download_speed"
SENSOR_TYPE_UPLOAD_SPEED = "upload_speed"
SENSOR_TYPE_DOWNLOADING_TOTAL = "downloading"
SENSOR_TYPE_LONGEST_ETA = "eta"

SENSOR_TYPES: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        key=SENSOR_TYPE_CURRENT_STATUS,
        name="status",
        icon="mdi:cloud",
    ),
    SensorEntityDescription(
        key=SENSOR_TYPE_DOWNLOAD_SPEED,
        name="download speed",
        icon="mdi:cloud-download",
        device_class=SensorDeviceClass.DATA_RATE,
        native_unit_of_measurement=UnitOfDataRate.KIBIBYTES_PER_SECOND,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=SENSOR_TYPE_UPLOAD_SPEED,
        name="upload speed",
        icon="mdi:cloud-upload",
        device_class=SensorDeviceClass.DATA_RATE,
        native_unit_of_measurement=UnitOfDataRate.KIBIBYTES_PER_SECOND,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=SENSOR_TYPE_DOWNLOADING_TOTAL,
        name="downloading",
        icon="mdi:file-cloud",
        native_unit_of_measurement="torrents"
    ),
    SensorEntityDescription(
        key=SENSOR_TYPE_LONGEST_ETA,
        name="ETA",
        icon="mdi:cloud-clock",
        native_unit_of_measurement=UnitOfTime.SECONDS
    ),
)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_URL): cv.url,
        vol.Required(CONF_USERNAME): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    }
)

async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:

    """Set up the qBittorrent platform."""
    hass.async_create_task(
        hass.config_entries.flow.async_init(
            DOMAIN, context={"source": SOURCE_IMPORT}, data=config
        )
    )

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:

    """Set up qBittorrent sensor entries."""
    client: Client = hass.data[DOMAIN][config_entry.entry_id]
    qb_version = await hass.async_add_executor_job(get_version, client)
    
    entities = [
        QBittorrentSensor(hass, description, config_entry, client, qb_version)
        for description in SENSOR_TYPES
    ]

    async_add_entities(entities, True)


def format_speed(speed):
    """Return a bytes/s measurement as a human readable string."""
    kb_spd = float(speed) / 1024
    return round(kb_spd, 2 if kb_spd < 0.1 else 1)


class QBittorrentSensor(SensorEntity):
    """Representation of an qBittorrent sensor."""

    def __init__(
        self,
        hass,
        description: SensorEntityDescription,
        config_entry: ConfigEntry,
        qbittorrent_client: Client,
        qb_version: str
    ) -> None:

        """Initialize the qBittorrent sensor."""
        self.hass = hass
        self.entity_description = description
        self.config_entry = config_entry
        self.client = qbittorrent_client
        self.qb_version = qb_version

        self._attr_unique_id = f"{config_entry.entry_id}-{description.key}"
        self._attr_name = f"{config_entry.title} {description.name}"

    def update(self) -> None:
        """Get the latest data from qBittorrent and updates the state."""
        data = None

        try:
            if not self._attr_available:
                # Try to log in again to recreate the session or update the cookie
                LOGGER.debug(f"Attempting to log in after disconnection")
                self.client.auth_log_in()

            if self.client.is_logged_in:
                # Get the most recent data from the API
                data = self.client.sync_maindata()
                self._attr_available = True

        except LoginFailed as ex:
            # Bad username or password - assume that something has changed at the QBittorrent end
            LOGGER.warning(f"Error {ex} attempting to re-authenticate")
            self.hass.add_job(self.config_entry.async_start_reauth, self.hass)
            self._attr_available = False
            
            return

        except Forbidden403Error as ex:
            LOGGER.warning(f"Error {ex} attempting to re-authenticate")
            self._attr_available = False

            return
            
        except APIConnectionError as ex:
            LOGGER.warning(f"Error {ex} attempting to connect to API")
            self._attr_available = False
            
            return

        except ConnectTimeout as ex:
            LOGGER.error(f"Timed out attempting to retrieve data with error {ex}")
            self._attr_available = False

            return

        except RequestException as ex:
            LOGGER.error(f"Error {ex} attempting to retrieve data")
            self._attr_available = False

            return

        except Exception as ex:
            # General failure
            LOGGER.error(f"Error {ex} attempting to retrieve data")
            self._attr_available = False

            return

        if data is None:
            LOGGER.debug(f"No data returned from update")

            return

        sensor_type = self.entity_description.key
        download = data["server_state"]["dl_info_speed"]
        upload = data["server_state"]["up_info_speed"]
        
        if sensor_type == SENSOR_TYPE_CURRENT_STATUS:
            if upload > 0 and download > 0:
                self._attr_native_value = "Uploading and downloading"
    
            elif upload > 0 and download == 0:
                self._attr_native_value = "Uploading"

            elif upload == 0 and download > 0:
                self._attr_native_value = "Downloading"

            else:
                self._attr_native_value = STATE_IDLE

        elif sensor_type == SENSOR_TYPE_DOWNLOAD_SPEED:
            self._attr_native_value = format_speed(download)
        
        elif sensor_type == SENSOR_TYPE_UPLOAD_SPEED:
            self._attr_native_value = format_speed(upload)
        
        elif sensor_type == SENSOR_TYPE_DOWNLOADING_TOTAL:
            downloading = 0
            try:
                torrents = data["torrents"]
                for torrent in torrents:
                    if torrents[torrent]["state"][:-2] == "DL" or torrents[torrent]["state"] == "downloading":
                        downloading += 1     

                self._attr_available = True

            except:
                self._attr_available = False

            self._attr_native_value = downloading

        elif sensor_type == SENSOR_TYPE_LONGEST_ETA:
            longest_eta = 0
            try:
                torrents = data["torrents"]
                for torrent in torrents:
                    if torrents[torrent]["eta"] != 8640000 and torrents[torrent]["eta"] > longest_eta:
                        longest_eta = torrents[torrent]["eta"]

                self._attr_available = True

            except:
                self._attr_available = False

            self._attr_native_value = longest_eta

    @property
    def device_info(self):
        """Return device info for this sensor."""
        return  {
            "identifiers": {(DOMAIN, urlparse(self.config_entry.data[CONF_URL]).hostname)},
            "name": f"qBittorrent - {urlparse(self.config_entry.data[CONF_URL]).hostname}",
            "manufacturer": "The qBittorrent project",
            "model": self.qb_version,
            "configuration_url": self.config_entry.data[CONF_URL]
        }
        

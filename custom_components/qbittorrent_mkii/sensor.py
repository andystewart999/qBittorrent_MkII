"""Support for monitoring the qBittorrent API."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import voluptuous as vol

from homeassistant.components.sensor import (
    PLATFORM_SCHEMA,
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import SOURCE_IMPORT
from homeassistant.const import (
    CONF_NAME,
    CONF_PASSWORD,
    CONF_URL,
    CONF_USERNAME,
    STATE_IDLE,
    UnitOfDataRate,
    UnitOfTime
)
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType, StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import *
from .coordinator import QBittorrentConfigEntry, QBittorrentDataUpdateCoordinator
from urllib.parse import urlparse


def format_speed(speed):
    """Return a bytes/s measurement as a human readable string."""
    kb_spd = float(speed) / 1024
    return round(kb_spd, 2 if kb_spd < 0.1 else 1)


def get_status(data: dict[str, Any]) -> str:
    """Return a description of the current upload/download activity."""
    download = data["server_state"]["dl_info_speed"]
    upload = data["server_state"]["up_info_speed"]

    if upload > 0 and download > 0:
        return "Uploading and downloading"

    elif upload > 0 and download == 0:
        return "Uploading"

    elif upload == 0 and download > 0:
        return "Downloading"

    return STATE_IDLE


def count_downloading(data: dict[str, Any]) -> int:
    """Return the number of torrents that are currently downloading."""
    downloading = 0
    for torrent in data.get("torrents", {}).values():
        if torrent["state"][:-2] == "DL" or torrent["state"] == "downloading":
            downloading += 1

    return downloading


def get_longest_eta(data: dict[str, Any]) -> int:
    """Return the longest ETA of any torrent, ignoring the 'infinite' value."""
    longest_eta = 0
    for torrent in data.get("torrents", {}).values():
        if torrent["eta"] != 8640000 and torrent["eta"] > longest_eta:
            longest_eta = torrent["eta"]

    return longest_eta


@dataclass(frozen=True, kw_only=True)
class QBittorrentSensorEntityDescription(SensorEntityDescription):
    """Describes a qBittorrent sensor and how its value is derived from the API data."""

    value_fn: Callable[[dict[str, Any]], StateType]


SENSOR_TYPES: tuple[QBittorrentSensorEntityDescription, ...] = (
    QBittorrentSensorEntityDescription(
        key=SENSOR_TYPE_CURRENT_STATUS,
        name="status",
        icon="mdi:cloud",
        value_fn=get_status,
    ),
    QBittorrentSensorEntityDescription(
        key=SENSOR_TYPE_DOWNLOAD_SPEED,
        name="download speed",
        icon="mdi:cloud-download",
        device_class=SensorDeviceClass.DATA_RATE,
        native_unit_of_measurement=UnitOfDataRate.KIBIBYTES_PER_SECOND,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: format_speed(data["server_state"]["dl_info_speed"]),
    ),
    QBittorrentSensorEntityDescription(
        key=SENSOR_TYPE_UPLOAD_SPEED,
        name="upload speed",
        icon="mdi:cloud-upload",
        device_class=SensorDeviceClass.DATA_RATE,
        native_unit_of_measurement=UnitOfDataRate.KIBIBYTES_PER_SECOND,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: format_speed(data["server_state"]["up_info_speed"]),
    ),
    QBittorrentSensorEntityDescription(
        key=SENSOR_TYPE_DOWNLOADING_TOTAL,
        name="downloading",
        icon="mdi:file-cloud",
        native_unit_of_measurement="torrents",
        value_fn=count_downloading,
    ),
    QBittorrentSensorEntityDescription(
        key=SENSOR_TYPE_LONGEST_ETA,
        name="ETA",
        icon="mdi:cloud-clock",
        native_unit_of_measurement=UnitOfTime.SECONDS,
        value_fn=get_longest_eta,
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
    config_entry: QBittorrentConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:

    """Set up qBittorrent sensor entries."""
    coordinator = config_entry.runtime_data

    async_add_entities(
        QBittorrentSensor(coordinator, description, config_entry)
        for description in SENSOR_TYPES
    )


class QBittorrentSensor(CoordinatorEntity[QBittorrentDataUpdateCoordinator], SensorEntity):
    """Representation of an qBittorrent sensor."""

    entity_description: QBittorrentSensorEntityDescription

    def __init__(
        self,
        coordinator: QBittorrentDataUpdateCoordinator,
        description: QBittorrentSensorEntityDescription,
        config_entry: QBittorrentConfigEntry,
    ) -> None:

        """Initialize the qBittorrent sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self.config_entry = config_entry

        self._attr_unique_id = f"{config_entry.entry_id}-{description.key}"
        self._attr_name = f"{config_entry.title} {description.name}"

    @property
    def native_value(self) -> StateType:
        """Return the sensor value from the most recent coordinator data."""
        return self.entity_description.value_fn(self.coordinator.data)

    @property
    def device_info(self):
        """Return device info for this sensor."""
        return  {
            "identifiers": {(DOMAIN, urlparse(self.config_entry.data[CONF_URL]).hostname)},
            "name": f"qBittorrent - {urlparse(self.config_entry.data[CONF_URL]).hostname}",
            "manufacturer": "The qBittorrent project",
            "model": self.coordinator.qb_version,
            "configuration_url": self.config_entry.data[CONF_URL]
        }

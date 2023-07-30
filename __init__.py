"""The qbittorrent component."""
#import logging
from datetime import timedelta

from qbittorrent.client import LoginRequired
from requests.exceptions import RequestException

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_PASSWORD,
    CONF_URL,
    CONF_USERNAME,
    CONF_VERIFY_SSL,
    CONF_SCAN_INTERVAL,
    Platform,
)
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.event import async_track_time_interval

from .const import *
from .helpers import setup_client
from .events import QBEventsAndServices

PLATFORMS = [Platform.SENSOR]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up qBittorrent from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    try:
        hass.data[DOMAIN][entry.entry_id] = await hass.async_add_executor_job(
            setup_client,
            entry.data[CONF_URL],
            entry.data[CONF_USERNAME],
            entry.data[CONF_PASSWORD],
            entry.data[CONF_VERIFY_SSL],
        )
        
        client: Client = hass.data[DOMAIN][entry.entry_id]
        event_handler = QBEventsAndServices(hass, entry)

    except LoginRequired as err:
        raise ConfigEntryNotReady("Invalid credentials") from err
    except RequestException as err:
        raise ConfigEntryNotReady("Failed to connect") from err

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload qBittorrent config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        del hass.data[DOMAIN][entry.entry_id]
        if not hass.data[DOMAIN]:
            del hass.data[DOMAIN]
    return unload_ok

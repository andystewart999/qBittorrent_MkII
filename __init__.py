"""The qbittorrent component."""
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

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up qBittorrent from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    
    try:
        hass.data[DOMAIN][config_entry.entry_id] = await hass.async_add_executor_job(
            setup_client,
            config_entry.data[CONF_URL],
            config_entry.data[CONF_USERNAME],
            config_entry.data[CONF_PASSWORD],
            config_entry.data[CONF_VERIFY_SSL],
        )
        
        client: Client = hass.data[DOMAIN][config_entry.entry_id]
        event_handler = QBEventsAndServices(hass, config_entry)

    except LoginRequired as err:
        raise ConfigEntryNotReady("Invalid credentials") from err
    except RequestException as err:
        raise ConfigEntryNotReady("Failed to connect") from err

    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)

    try:
        """Cancel any currently running event timer"""
        hass.data[DOMAIN][CONF_EVENT_SCAN_INTERVAL]()
    except:
        pass
    
    """Create a new event timer"""
    hass.data[DOMAIN][CONF_EVENT_SCAN_INTERVAL] = async_track_time_interval(
        hass, event_handler.raise_events,
        timedelta(seconds=config_entry.options.get(CONF_EVENT_SCAN_INTERVAL, DEFAULT_EVENT_SCAN_INTERVAL))
    )
    
    return True


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Unload qBittorrent config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(config_entry, PLATFORMS):
        del hass.data[DOMAIN][config_entry.entry_id]
        if not hass.data[DOMAIN]:
            del hass.data[DOMAIN]
    return unload_ok
    
#async def update_listener(hass: HomeAssistant, entry: ConfigEntry):
#    """Handle options update.  Really just the timer"""
#    LOGGER.error('in update_listener')
#    self.event_unsub()
#    LOGGER.error('recreating event')
#    self.event_unsub = async_track_time_interval(hass, event_handler.raise_events, timedelta(seconds = entry.data[CONF_EVENT_SCAN_INTERVAL]))

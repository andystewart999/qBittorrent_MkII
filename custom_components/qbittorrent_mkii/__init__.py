"""The qbittorrent component."""
from datetime import timedelta

from qbittorrentapi import Client, APIConnectionError, LoginFailed, HTTPError, Forbidden403Error, InternalServerError500Error 
from requests.exceptions import RequestException, ConnectTimeout

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_PASSWORD,
    CONF_URL,
    CONF_PORT,
    CONF_USERNAME,
    CONF_VERIFY_SSL,
    CONF_SCAN_INTERVAL,
    Platform,
)
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady, ConfigEntryAuthFailed
from homeassistant.helpers.event import async_track_time_interval

from .const import *
from .helpers import setup_client
from .events import QBEventsAndActions

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SENSOR]

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up qBittorrent from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    
    try:

        client = await hass.async_add_executor_job(
            setup_client,
            config_entry.data[CONF_URL],
            config_entry.data[CONF_USERNAME],
            config_entry.data[CONF_PASSWORD],
            config_entry.data[CONF_VERIFY_SSL],
        )
        hass.data[DOMAIN][config_entry.entry_id] = client

    # Raising ConfigEntryNotReady means HA will automatically retry setup again later
    # Raising ConfigEntryAuthFailed means HA will show the re-auth process and stop retrying until new credtentials are provided

    except LoginFailed as ex:
        raise ConfigEntryAuthFailed(f"Invalid credentials") from ex

    except Forbidden403Error as ex:
        raise ConfigEntryNotReady(f"Login denied") from ex

    except APIConnectionError as ex:
        raise ConfigEntryNotReady(f"Unknown API failure") from ex

    except ConnectTimeout as ex:
        raise ConfigEntryNotReady(f"Connection timeout") from ex

    except Exception as ex:
        raise ConfigEntryNotReady(f"Unknown error") from ex

    event_handler = QBEventsAndActions(hass, config_entry)

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

#    # Reload if the options change
#    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    
    return True


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Unload qBittorrent config entry."""

    try:
        # Disconnect the qBittorrent client
        hass.data[DOMAIN][config_entry.entry_id].auth_log_out()
    except:
        pass

    if unload_ok := await hass.config_entries.async_unload_platforms(config_entry, PLATFORMS):
        del hass.data[DOMAIN][config_entry.entry_id]
        if not hass.data[DOMAIN]:
            del hass.data[DOMAIN]

    return unload_ok

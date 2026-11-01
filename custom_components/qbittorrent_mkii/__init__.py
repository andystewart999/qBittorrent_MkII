"""The qbittorrent component."""
from datetime import timedelta

from qbittorrentapi import APIConnectionError, LoginFailed, Forbidden403Error
from requests.exceptions import ConnectTimeout

from homeassistant.const import (
    CONF_PASSWORD,
    CONF_URL,
    CONF_USERNAME,
    CONF_VERIFY_SSL,
    Platform,
)
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady, ConfigEntryAuthFailed
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.typing import ConfigType

from .const import *
from .coordinator import QBittorrentConfigEntry, QBittorrentDataUpdateCoordinator
from .helpers import setup_client, get_version
from .events import QBEvents
from .services import async_setup_services

PLATFORMS = [Platform.SENSOR]

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the qBittorrent actions, which are shared by all config entries."""
    async_setup_services(hass)

    return True


async def async_setup_entry(hass: HomeAssistant, config_entry: QBittorrentConfigEntry) -> bool:
    """Set up qBittorrent from a config entry."""
    try:

        client = await hass.async_add_executor_job(
            setup_client,
            config_entry.data[CONF_URL],
            config_entry.data[CONF_USERNAME],
            config_entry.data[CONF_PASSWORD],
            config_entry.data[CONF_VERIFY_SSL],
        )

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

    qb_version = await hass.async_add_executor_job(get_version, client)

    coordinator = QBittorrentDataUpdateCoordinator(hass, config_entry, client, qb_version)
    await coordinator.async_config_entry_first_refresh()
    config_entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)

    """Create the event timer, which is cancelled automatically when the entry is unloaded"""
    event_handler = QBEvents(hass, config_entry, client)
    config_entry.async_on_unload(
        async_track_time_interval(
            hass, event_handler.raise_events,
            timedelta(seconds=config_entry.options.get(CONF_EVENT_SCAN_INTERVAL, DEFAULT_EVENT_SCAN_INTERVAL))
        )
    )

    return True


async def async_unload_entry(hass: HomeAssistant, config_entry: QBittorrentConfigEntry) -> bool:
    """Unload qBittorrent config entry."""

    if unload_ok := await hass.config_entries.async_unload_platforms(config_entry, PLATFORMS):
        try:
            # Disconnect the qBittorrent client
            await hass.async_add_executor_job(config_entry.runtime_data.client.auth_log_out)
        except Exception:
            pass

    return unload_ok

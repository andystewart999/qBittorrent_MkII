"""Data update coordinator for qBittorrent_MkII"""
from __future__ import annotations

from datetime import timedelta
from typing import Any

from qbittorrentapi import Client, LoginFailed

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_SCAN_INTERVAL
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import *

type QBittorrentConfigEntry = ConfigEntry[QBittorrentDataUpdateCoordinator]


class QBittorrentDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Retrieve qBittorrent data once per interval and share it with every sensor"""

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: QBittorrentConfigEntry,
        client: Client,
        qb_version: str | None
    ) -> None:

        super().__init__(
            hass,
            LOGGER,
            config_entry=config_entry,
            name=config_entry.title,
            update_interval=timedelta(seconds=config_entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SENSOR_SCAN_INTERVAL)),
        )

        self.client = client
        self.qb_version = qb_version

    def _fetch_maindata(self) -> dict[str, Any]:
        if not self.last_update_success:
            # Try to log in again to recreate the session or update the cookie
            LOGGER.debug(f"Attempting to log in after disconnection")
            self.client.auth_log_in()

        return self.client.sync_maindata()

    async def _async_update_data(self) -> dict[str, Any]:
        # The coordinator logs the first failure and the recovery, but not every failure in between
        try:
            return await self.hass.async_add_executor_job(self._fetch_maindata)

        except LoginFailed as ex:
            # Bad username or password - HA will start the re-auth process
            raise ConfigEntryAuthFailed(f"Invalid credentials") from ex

        except Exception as ex:
            raise UpdateFailed(f"Error {ex} attempting to retrieve data") from ex

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from qbittorrentapi import Client

from .const import *
from .helpers import compare_torrents

class QBEvents:
    """Encapsulates logic for raising events based on torrent activity"""

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        client: Client,
    ):

        #Capture event yes/no info plus event timings
        self.client = client
        self.config_entry = config_entry
        self.hass = hass

        # Torrent list from the last successful check, kept per config entry
        self.torrents_prev = []


    # This function is called periodically as per the ConfigFlow value
    async def raise_events(self, now=None):
        """Review current torrent info and determine if any events should be raised"""
        try:
            completed_torrents, added_torrents, removed_torrents, self.torrents_prev = await self.hass.async_add_executor_job(
                compare_torrents, self.client, self.torrents_prev
            )

        except Exception as ex:
            # Connection failures are already logged once by the sensor coordinator, which polls the same client
            LOGGER.debug(f"Error {ex} attempting to check {self.config_entry.title} for torrent events")

            return

        #Has anything changed that we care about?  Raise events as required
        if completed_torrents and self.config_entry.options.get(CONF_EVENT_COMPLETE, DEFAULT_EVENT_COMPLETE):
            for torrent in completed_torrents:
                self.hass.bus.async_fire(EVENT_COMPLETED, torrent)

        if added_torrents and self.config_entry.options.get(CONF_EVENT_ADDED, DEFAULT_EVENT_ADDED):
            for torrent in added_torrents:
                self.hass.bus.async_fire(EVENT_ADDED, torrent)

        if removed_torrents and self.config_entry.options.get(CONF_EVENT_REMOVED, DEFAULT_EVENT_REMOVED):
            for torrent in removed_torrents:
                self.hass.bus.async_fire(EVENT_REMOVED, torrent)

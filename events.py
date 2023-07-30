from homeassistant.core import HomeAssistant, ServiceCall, ServiceResponse, SupportsResponse
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.event import async_track_time_interval
from datetime import timedelta

from qbittorrent.client import Client, LoginRequired
from .const import *
from .helpers import compare_torrents, pause_downloads, resume_downloads, get_torrent_info, shutdown


class QBEventsAndServices:
    """Encapsulates logic for raising events based on torrent activity"""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
    ):
        
        #Capture event yes/no info plus event timings
        self.client = hass.data[DOMAIN][entry.entry_id]
        self.hass = hass
        self.raise_completed_events = entry.data[CONF_EVENT_COMPLETE]
        self.raise_added_events = entry.data[CONF_EVENT_ADDED]
        self.raise_removed_events = entry.data[CONF_EVENT_REMOVED]
        self.raise_removed_events = entry.data[CONF_EVENT_REMOVED]

        async_track_time_interval(hass, self.raise_events, timedelta(seconds = entry.data[CONF_EVENT_SCAN_INTERVAL]))

        async def service_get_torrent_info(call: ServiceCall) -> ServiceResponse:
            try:
                hash = call.data.get('hash','all')
            except Exception as err:
                hash = 'all'

            return await self.hass.async_add_executor_job(get_torrent_info, self.client, hash)

        async def service_pause_downloads(call: ServiceCall):
            await self.hass.async_add_executor_job(pause_downloads, self.client)
            return
        
        async def service_resume_downloads(call: ServiceCall):
            await self.hass.async_add_executor_job(resume_downloads, self.client)
            return

        async def service_shutdown(call: ServiceCall):
            await self.hass.async_add_executor_job(shutdown, self.client)
            return

        hass.services.async_register(DOMAIN, SERVICE_GET_TORRENT_INFO, service_get_torrent_info, supports_response=SupportsResponse.ONLY)
        hass.services.async_register(DOMAIN, SERVICE_PAUSE_DOWLOADS, service_pause_downloads)
        hass.services.async_register(DOMAIN, SERVICE_RESUME_DOWLOADS, service_resume_downloads)
        hass.services.async_register(DOMAIN, SERVICE_SHUTDOWN, service_shutdown)


    async def raise_events(self, hass):
        """Review current torrent info and determine if any events should be raised"""
        completed_torrents, added_torrents, removed_torrents = await self.hass.async_add_executor_job(compare_torrents, self.client)

        #Has anything changed that we care about?  Raise events as required
        if completed_torrents and self.raise_completed_events:
            self.hass.bus.async_fire(EVENT_COMPLETED, completed_torrents)

        if added_torrents and self.raise_added_events:
            self.hass.bus.async_fire(EVENT_ADDED, added_torrents)

        if removed_torrents and self.raise_removed_events:
            self.hass.bus.async_fire(EVENT_REMOVED, removed_torrents)

        return

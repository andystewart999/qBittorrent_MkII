from homeassistant.core import HomeAssistant, ServiceCall, ServiceResponse, SupportsResponse
from homeassistant.config_entries import ConfigEntry
#from homeassistant.helpers.event import async_track_time_interval
#from datetime import timedelta

from qbittorrent.client import Client, LoginRequired
from .const import *
from .helpers import compare_torrents, pause_downloads, resume_downloads, get_torrent_info, shutdown

class QBEventsAndServices:
    """Encapsulates logic for raising events based on torrent activity"""

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
    ):
        
        #Capture event yes/no info plus event timings
        self.client = hass.data[DOMAIN][config_entry.entry_id]
        self.config_entry = config_entry
        self.hass = hass

        async def service_get_torrent_info(call: ServiceCall) -> ServiceResponse:
            try:
                hash = call.data.get('hash','all')
            except Exception as err:
                hash = 'all'

            return await self.hass.async_add_executor_job(get_torrent_info, self.client, hash)

        async def service_pause_downloads(call: ServiceCall):
            try:
                hash = call.data.get('hash','all')
            except Exception as err:
                hash = 'all'

            return await self.hass.async_add_executor_job(pause_downloads, self.client, hash)
        
        async def service_resume_downloads(call: ServiceCall):
            try:
                hash = call.data.get('hash','all')
            except Exception as err:
                hash = 'all'

            return await self.hass.async_add_executor_job(resume_downloads, self.client, hash)

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
        if completed_torrents and self.config_entry.options.get(CONF_EVENT_COMPLETE, DEFAULT_EVENT_COMPLETE):
            for torrent in completed_torrents:
                self.hass.bus.async_fire(EVENT_COMPLETED, torrent)

        if added_torrents and self.config_entry.options.get(CONF_EVENT_ADDED, DEFAULT_EVENT_ADDED):
            for torrent in added_torrents:
                self.hass.bus.async_fire(EVENT_ADDED, torrent)

        if removed_torrents and self.config_entry.options.get(CONF_EVENT_REMOVED, DEFAULT_EVENT_REMOVED):
            for torrent in removed_torrents:
                self.hass.bus.async_fire(EVENT_REMOVED, torrent)

        return

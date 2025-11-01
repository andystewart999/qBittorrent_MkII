from homeassistant.core import HomeAssistant, ServiceCall, ServiceResponse, SupportsResponse
from homeassistant.config_entries import ConfigEntry

import qbittorrentapi
from qbittorrentapi import Client

from .const import *
from .helpers import compare_torrents, pause_downloads, resume_downloads, get_torrent_info, delete_torrent, shutdown

class QBEventsAndActions:
    """Encapsulates logic for raising events based on torrent activity, and for actions that Home Assistant can call"""

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
    ):
        
        #Capture event yes/no info plus event timings
        self.client = hass.data[DOMAIN][config_entry.entry_id]
        self.config_entry = config_entry
        self.hass = hass

        # Action that returns a JSON array of torrents that meet the criteria
        async def action_get_torrent_info(call: ServiceCall) -> ServiceResponse:
            try:
                hash = call.data.get('hash', None)
                status_filter = call.data.get('status_filter', 'all')

            except Exception as err:
                hash = None
                status_filter = "all"

            return await self.hass.async_add_executor_job(get_torrent_info, self.client, hash, status_filter)

        # Action that pauses the targeted torrent(s)
        async def action_pause_downloads(call: ServiceCall):
            try:
                hash = call.data.get('hash','all')
            except Exception as err:
                hash = 'all'

            return await self.hass.async_add_executor_job(pause_downloads, self.client, hash)
        
        # Action that resumes the targeted torrent(s)
        async def action_resume_downloads(call: ServiceCall):
            try:
                hash = call.data.get('hash','all')
            except Exception as err:
                hash = 'all'

            return await self.hass.async_add_executor_job(resume_downloads, self.client, hash)

        # Action that deletes the targeted torrrent
        async def action_delete_torrent(call: ServiceCall):
            try:
                hash = call.data.get('hash', None)
                delete_files = call.data.get('delete_files', False)
                
            except Exception as err:
                hash = None

            if hash is not None:
                return await self.hass.async_add_executor_job(delete_torrent, self.client, hash, delete_files)

        # Action that attempts to shut down the remote qBittorrent app
        async def action_service_shutdown(call: ServiceCall):
            await self.hass.async_add_executor_job(shutdown, self.client)
            return

        # Register all actions so they appear in the Actions dropdown in the Developer screen
        hass.services.async_register(DOMAIN, ACTION_GET_TORRENT_INFO, action_get_torrent_info, supports_response=SupportsResponse.ONLY)
        hass.services.async_register(DOMAIN, ACTION_PAUSE_DOWLOADS, action_pause_downloads)
        hass.services.async_register(DOMAIN, ACTION_RESUME_DOWLOADS, action_resume_downloads)
        hass.services.async_register(DOMAIN, ACTION_DELETE_TORRENT, action_delete_torrent)
        hass.services.async_register(DOMAIN, ACTION_SERVICE_SHUTDOWN, action_service_shutdown)


    # This function is called periodically as per the ConfigFlow value
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

"""Actions that Home Assistant can call"""
from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import ATTR_CONFIG_ENTRY_ID
from homeassistant.core import HomeAssistant, ServiceCall, ServiceResponse, SupportsResponse, callback
from homeassistant.exceptions import ServiceValidationError

from qbittorrentapi import Client

from .const import *
from .helpers import pause_downloads, resume_downloads, get_torrent_info, delete_torrent, shutdown


def get_client(hass: HomeAssistant, call: ServiceCall) -> Client:
    """Return the client for the targeted qBittorrent instance"""
    entries = [
        entry for entry in hass.config_entries.async_entries(DOMAIN)
        if entry.state is ConfigEntryState.LOADED
    ]

    # Target a specific instance if config_entry_id is set, otherwise there must be only one
    if entry_id := call.data.get(ATTR_CONFIG_ENTRY_ID):
        entries = [entry for entry in entries if entry.entry_id == entry_id]
        if not entries:
            raise ServiceValidationError(f"qBittorrent instance '{entry_id}' is not loaded")

    elif not entries:
        raise ServiceValidationError("No qBittorrent instance is loaded")

    elif len(entries) > 1:
        raise ServiceValidationError("More than one qBittorrent instance is configured - set config_entry_id to choose one")

    return entries[0].runtime_data.client


@callback
def async_setup_services(hass: HomeAssistant) -> None:
    """Register the actions once, for all qBittorrent instances"""

    # Action that returns a JSON array of torrents that meet the criteria
    async def action_get_torrent_info(call: ServiceCall) -> ServiceResponse:
        client = get_client(hass, call)
        hash = call.data.get('hash', None)
        status_filter = call.data.get('status_filter', 'all')

        return await hass.async_add_executor_job(get_torrent_info, client, hash, status_filter)

    # Action that pauses the targeted torrent(s)
    async def action_pause_downloads(call: ServiceCall):
        client = get_client(hass, call)
        hash = call.data.get('hash', 'all')

        await hass.async_add_executor_job(pause_downloads, client, hash)

    # Action that resumes the targeted torrent(s)
    async def action_resume_downloads(call: ServiceCall):
        client = get_client(hass, call)
        hash = call.data.get('hash', 'all')

        await hass.async_add_executor_job(resume_downloads, client, hash)

    # Action that deletes the targeted torrrent
    async def action_delete_torrent(call: ServiceCall):
        client = get_client(hass, call)
        hash = call.data.get('hash', None)
        delete_files = call.data.get('delete_files', False)

        if hash is not None:
            await hass.async_add_executor_job(delete_torrent, client, hash, delete_files)

    # Action that attempts to shut down the remote qBittorrent app
    async def action_service_shutdown(call: ServiceCall):
        client = get_client(hass, call)

        await hass.async_add_executor_job(shutdown, client)

    # Register all actions so they appear in the Actions dropdown in the Developer screen
    hass.services.async_register(DOMAIN, ACTION_GET_TORRENT_INFO, action_get_torrent_info, supports_response=SupportsResponse.ONLY)
    hass.services.async_register(DOMAIN, ACTION_PAUSE_DOWLOADS, action_pause_downloads)
    hass.services.async_register(DOMAIN, ACTION_RESUME_DOWLOADS, action_resume_downloads)
    hass.services.async_register(DOMAIN, ACTION_DELETE_TORRENT, action_delete_torrent)
    hass.services.async_register(DOMAIN, ACTION_SERVICE_SHUTDOWN, action_service_shutdown)

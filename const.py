"""Constants for qBittorrent_MkII"""
from typing import Final
from datetime import timedelta
import voluptuous as vol
import logging

DOMAIN: Final = "qbittorrent_mkii"

#Defaults
DEFAULT_NAME = "qBittorrent" #This is the base sensor and display name, that will have the target hostname added for uniqueness
DEFAULT_URL = "http://192.168.1.1:8080"
DEFAULT_VERIFY_SSL = False
DEFAULT_SENSOR_SCAN_INTERVAL = 60
DEFAULT_EVENT_SCAN_INTERVAL = 10
DEFAULT_EVENT_COMPLETE = True
DEFAULT_EVENT_ADDED = False
DEFAULT_EVENT_REMOVED = False

#Events
CONF_EVENT_COMPLETE = "torrent_complete"
CONF_EVENT_ADDED = "torrent_added"
CONF_EVENT_REMOVED = "torrent_removed"
CONF_EVENT_SCAN_INTERVAL= "event_scan_interval"

EVENT_COMPLETED = DOMAIN + "_" + CONF_EVENT_COMPLETE
EVENT_ADDED = DOMAIN + "_" + CONF_EVENT_ADDED
EVENT_REMOVED = DOMAIN + "_" + CONF_EVENT_REMOVED

#Services
ACTION_RESUME_DOWLOADS = 'action_resume_downloads'
ACTION_PAUSE_DOWLOADS = 'action_pause_downloads'
ACTION_GET_TORRENT_INFO = 'action_get_torrent_info'
ACTION_DELETE_TORRENT = 'action_delete_torrent'
ACTION_SERVICE_SHUTDOWN = 'action_service_shutdown'

#Logging
LOGGER = logging.getLogger(__package__)

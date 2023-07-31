"""Constants for qBittorrent_MkII"""
from typing import Final
from datetime import timedelta
import voluptuous as vol
import logging

DOMAIN: Final = "qbittorrent_MkII"
CONF_EVENT_COMPLETE = "torrent_complete"
CONF_EVENT_ADDED = "torrent_added"
CONF_EVENT_REMOVED = "torrent_removed"
CONF_EVENT_SCAN_INTERVAL= "event_scan_interval"

#Events
EVENT_COMPLETED = DOMAIN + "_" + CONF_EVENT_COMPLETE
EVENT_ADDED = DOMAIN + "_" + CONF_EVENT_ADDED
EVENT_REMOVED = DOMAIN + "_" + CONF_EVENT_REMOVED

DEFAULT_NAME = "qBittorrentTest"
DEFAULT_URL = "http://192.168.1.233:8080"
DEFAULT_SENSOR_SCAN_INTERVAL = 60
DEFAULT_EVENT_SCAN_INTERVAL = 10
DEFAULT_EVENT_COMPLETE = True
DEFAULT_EVENT_ADDED = False
DEFAULT_EVENT_REMOVED = False

SERVICE_RESUME_DOWLOADS = 'service_resume_downloads'
SERVICE_PAUSE_DOWLOADS = 'service_pause_downloads'
SERVICE_GET_TORRENT_INFO = 'service_get_torrent_info'
SERVICE_SHUTDOWN = 'service_shutdown'


LOGGER = logging.getLogger(__package__)

"""Maybe this should live elsewhere?  Closer to the functions that need to know this, for example the event or sensor py?"""
TORRENT_STATES: dict[str, str] = {
    "error": "An error occurred (applies to paused torrents)",
    "missingFiles": "At least one file in the torrent is misssing",
    "uploading": "Torrent has finished downloading and is now seeding",
    "pausedUP": "Torrent has finished downloading and is now paused",
    "queuedUP": "Torrent has finished downloading and is queued for seeding",
    "stalledUP": "Torrent is seeding but there are no peer connections",
    "checkingUP": "Torrent has finished downloading and is being checked",
    "forcedUP": "Torrent has finished downloading and has been forced to seed",
    "allocating": "Torrent is being allocated disk space",
    "downloading": "Torrent is downloading",
    "metaDL": "Torrent is fetching metadata",
    "pausedDL": "Torrent was downloading but has been paused",
    "queuedDL": "Torrent is queued and is waiting to start downloading",
    "stalledDL": "Torrent is waiting to download but there are no peer connections",
    "checkingDL": "Torrent is being checked but has not finished downloading",
    "forcedDL": "Torrent has been forced to start downloading",
    "checkingResumeData": "Torrent is checking its resume data",
    "moving": "Torrent is being moved",
    "unknown": "Torrent is in an unknown state",
    }

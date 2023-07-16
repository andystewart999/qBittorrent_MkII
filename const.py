"""Constants for qBittorrent-HA"""
from typing import Final

DOMAIN: Final = "qbittorrent-ha"
EVENT_NAME = DOMAIN + "_event"
CONF_EVENT_COMPLETE = DOMAIN + "_torrent_complete"
CONF_EVENT_ADDED = DOMAIN + "_torrent_added"
CONF_EVENT_REMOVED = DOMAIN + "_torrent_removed"

DEFAULT_NAME = "qBittorrent"
DEFAULT_URL = "http://127.0.0.1:8080"
DEFAULT_SENSOR_SCAN_INTERVAL = timedelta(seconds=60)
DEFAULT_EVENT_SCAN_INTERVAL = timedelta(seconds=10)

"""Maybe this should live elsewhere?  Closer to the functions that need to know this, for example the event or sensor py?
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

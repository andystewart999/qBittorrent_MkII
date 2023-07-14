"""Constants for qBittorrent."""
from typing import Final

DOMAIN: Final = "qbittorrent-ha"

DEFAULT_NAME = "qBittorrent"
DEFAULT_URL = "http://127.0.0.1:8080"
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
    "pausedDL": "Torrent is downloading but has been paused",
    "queuedDL": "en",
    "stalledDL": "za",
    "checkingDL": "za",
    "forcedDL": "za",
    "checkingResumeData": "za",
    "moving": "za",
    "unknown": "za",
    }

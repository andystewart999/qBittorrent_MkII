# qBittorrent MkII
My version of Home Assistant's built-in qBittorrent integration

Adds the following capabilites:
- An event is raised whenever a torrent is added, completed or removed (at the users' choice)

Todo:
- An additional sensor showing how many torrents are still in 'downloading' state
- An additional sensor showing the overall percentage completion of all active torrents
- A pause/resume service for a specific torrent, or for all torrents
- Service to request information on a specific torrent via hash
- Service to shut down qBitorrent


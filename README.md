# qBittorrent MkII
My version of Home Assistant's built-in qBittorrent integration

Adds the following capabilites:
- An event is raised whenever a torrent is added, completed or removed (at the users' choice)

Todo:
- Additional optional sensors showing:
    * How many torrents are still in 'downloading' state
    * The highest ETA of all downloading torrents 
- A control service supporting the following options:
    * Pause/resume all torrents, or a specific torrent via an optional hash
    * Return information on all torrents, or a specific torrent via an optional hash
    * Shut down the remote qBittorrent client

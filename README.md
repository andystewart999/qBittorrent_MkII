# qBittorrent MkII
My version of Home Assistant's built-in qBittorrent integration

Adds the following features:
- Additional sensors showing:
    * How many torrents are still in 'downloading' state
    * The longest ETA of all downloading torrents 

- Events can be raised whenever a torrent is added, completed or removed (at the users' choice)

- Services supporting the following options:
    * Pause/resume all torrents, (or a specific torrent via an optional hash, pending)
    * Return information on all torrents, or a specific torrent via an optional hash
    * Shut down the remote qBittorrent client (although the underlying API call doesn't work in my environment for some reason)

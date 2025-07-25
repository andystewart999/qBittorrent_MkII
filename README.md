# qBittorrent MkII
Enhanced version of Home Assistant's built-in qBittorrent integration

Adds the following features:
- Additional sensors showing:
    * How many torrents are still in 'downloading' state
    * The longest ETA of all downloading torrents 

- Events can be raised whenever a torrent is added, completed or removed (at the users' choice)
```yaml
qbittorrent_mkii_torrent_complete
qbittorrent_mkii_torrent_added
qbittorrent_mkii_torrent_removed
```
- Four new services:
    * Pause/resume all torrents, or a specific torrent via an optional hash
    * Delete a specific torrent, optionally including the associated files as well
    * Return information on all torrents, or a specific torrent via an optional hash
    * Shut down the remote qBittorrent client


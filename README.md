# qBittorrent MkII
My version of Home Assistant's built-in qBittorrent integration

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
- Three new services:
    * Pause/resume all torrents, or a specific torrent via an optional hash
    * Return information on all torrents, or a specific torrent via an optional hash
    * Shut down the remote qBittorrent client (although the underlying API call doesn't work in my environment for some reason)


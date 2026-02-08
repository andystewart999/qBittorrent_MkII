# qBittorrent MkII
[![Last release version](https://img.shields.io/github/v/release/andystewart999/qBittorrent_MkII)](https://github.com/andystewart999/qBittorrent_MkII/releases)
[![Last release date](https://img.shields.io/github/release-date/andystewart999/qBittorrent_MkII)](https://github.com/andystewart999/qBittorrent_MkII/releases)
[![Contributors](https://img.shields.io/github/contributors/andystewart999/qBittorrent_MkII)](https://github.com/andystewart999/qBittorrent_MkII/graphs/contributors)
[![Project license](https://img.shields.io/github/license/andystewart999/qBittorrent_MkII)](https://github.com/andystewart999/qBittorrent_MkII/blob/master/LICENSE)
![hacs](https://img.shields.io/badge/hacs-standard_installation-darkorange.svg)
![type](https://img.shields.io/badge/type-custom_component-forestgreen.svg)

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


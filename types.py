from __future__ import annotations

from typing import TypedDict


class qTorrent(TypedDict):
    added_on: int
    completion_on: int
    eta: int
    hash: str
    name: str
    progress: float
    size: int
    state: string

qTorrentResults = dict[int, qTorrent]

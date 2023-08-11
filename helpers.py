"""Helper functions for qBittorrent."""
from qbittorrent.client import Client
from .const import *

all_torrents_prev = []

def setup_client(url: str, username: str, password: str, verify_ssl: bool) -> Client:
    """Create a qBittorrent client."""
    client = Client(url, verify=verify_ssl, timeout=10)
    client.login(username, password)

    # Get an arbitrary attribute to test if connection succeeds
    client.qbittorrent_version
    return client


def find_torrent(torrent_list, default=None):
    for x in torrent_list:
        return x
    return default

def get_detail(torrent, attribute):
    value = ''
    try:
        value = torrent[attribute]
    except Exception as err:
        pass
    
    return value
    
def get_version(client: Client):
    return client.qbittorrent_version

def compare_torrents(client: Client):
    #Return a dict containing all changed torrents and their new state
    global all_torrents_prev
    
    completed_torrents= {}
    added_torrents= {}
    removed_torrents = {}

    #Retrieve current torrent info    
    all_torrents = client.torrents()

    #Cater for a fresh startup - we don't want to raise a ton of events straight away
    if all_torrents_prev:
        for torrent in all_torrents_prev:
            #See if each torrent is still in the new list
            #If not, it's been deleted
            #If so, check the completion_on value - has it finished?
            prev_name = torrent['name']
            prev_hash = torrent['hash']
            prev_completion_on = torrent['completion_on']

            found_torrent = find_torrent(x for x in all_torrents if x['hash'] == prev_hash)
            if found_torrent is not None:
                if found_torrent['completion_on'] != prev_completion_on:
                    #See if it's just completed downloading
                    if found_torrent['completion_on'] > 0:
                        #It's just finished downloading
                        completed_torrents[prev_hash] = prev_name
            else:
                removed_torrents[prev_hash] = prev_name

        for torrent in all_torrents:
            #See if any new torrents have been added - it won't be in the previous list
            name = torrent['name']
            hash = torrent['hash']
            new_torrent = find_torrent(x for x in all_torrents_prev if x['hash'] == hash)
            if new_torrent is None:
                added_torrents[hash] = name

    all_torrents_prev = all_torrents
 
    return completed_torrents, added_torrents, removed_torrents

def pause_downloads(client: Client, hash: str):
    if hash != '' and hash != 'all':
        try:
            client.pause(hash)
        except Exception as err:
            pass
    else:
        client.pause_all()
    
    return

def resume_downloads(client: Client, hash:str):
    if hash != '' and hash != 'all':
        try:
            client.resume(hash)
        except Exception as err:
            pass
    else:
        client.resume_all()
    
    return

def get_torrent_info(client: Client, hash: str):
    if hash != '' and hash != 'all':
        try:
            torrent = client.get_torrent(hash)
            #LOGGER.error(torrent)
            return torrent
        except Exception as err:
            return {}
    else:
        torrents = client.torrents()
        #LOGGER.error(torrents)
        #For some reason, client.get_torrent() and client.torrents() have some differing key names!  I've decided to stay consistent with the get_torrent naming
        #Some of the values are still different, for example completion_date/completion_on for incomplete torrents are -36000 and -1
        return {
            "torrents": [
                {
                    "hash": get_detail(torrent, "hash"),
                    "name": get_detail(torrent, "name"),
                    "addition_date": get_detail(torrent, "added_on"),
                    "completion_date": get_detail(torrent, "completion_on"),
                    "eta": get_detail(torrent, "eta"),
                    "save_path": get_detail(torrent, "save_path"),
                    "seeds": get_detail(torrent, "num_seeds"),
                    "state": get_detail(torrent, "state"),
                    "category": get_detail(torrent, "category"),
                    "tags": get_detail(torrent, "tags"),
                    "total_downloaded": get_detail(torrent, "completed"),
                    "total_size": get_detail(torrent, "size")
                } for torrent in torrents
            ],
        }

def shutdown(client: Client):
    try:
        client.shutdown()
    except Exception as err:
        LOGGER.error(err)
        pass
    return

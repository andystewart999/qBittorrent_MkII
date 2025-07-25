"""Helper functions for qbittorrentapi"""
import qbittorrentapi
from qbittorrentapi import Client

from .const import *
import logging

all_torrents_prev = []

def setup_client(url: str, username: str, password: str, verify_ssl: bool) -> Client:
    try:
        client = qbittorrentapi.Client(host = url, username = username, password = password, VERIFY_WEBUI_CERTIFICATE = verify_ssl, SIMPLE_RESPONSES = True, REQUESTS_ARGS={'timeout': (3, 5)})

        # Get an arbitrary attribute to test if connection succeeded and we're passing data
        version = client.app.version

        return client

    except Exception as ex:
        LOGGER.error(f"Error {ex} setting up qBittorent client")

        return None

# Return all torrents in the list
def find_torrent(torrent_list, default=None):
    for x in torrent_list:
        return x

    return default

# Return a specific torrent attribute or an empty string
def get_detail(torrent, attribute):
    try:
        value = torrent[attribute]
    except Exception as err:
        return ""
    
    return value
    
# Return the version of the remote client
def get_version(client: Client):
    return client.app.version

# Compare the list of torrents with the last check, looking for newly added, removed and completed torrents
def compare_torrents(client: Client):
    #Return a list containing all changed torrents and their new state
    global all_torrents_prev
    
    completed_torrents= []
    added_torrents= []
    removed_torrents = []

    #Retrieve current torrent info    
    all_torrents = client.torrents_info()

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
                        completed_torrents.append (found_torrent)

            else:
                removed_torrents.append(torrent)

        for torrent in all_torrents:
            #See if any new torrents have been added - it won't be in the previous list
            name = torrent['name']
            hash = torrent['hash']

            new_torrent = find_torrent(x for x in all_torrents_prev if x['hash'] == hash)
            if new_torrent is None:
                added_torrents.append(torrent)

    all_torrents_prev = all_torrents
 
    return completed_torrents, added_torrents, removed_torrents

# Pause the targeted torrent(s)
def pause_downloads(client: Client, hash: str):
    if hash != '' and hash != 'all':
        try:
            client.torrents_pause(hash)
        except Exception as err:
            LOGGER.warn(f"Unable to pause torrent '{hash}'")
    else:
        client.torrents_pause('all')
    

# Resume the targeted torrent(s)
def resume_downloads(client: Client, hash: str):
    if hash != '' and hash != 'all':
        try:
            client.torrents_resume(hash)
        except Exception as err:
            LOGGER.warn(f"Unable to resume torrent '{hash}'")
    else:
        client.torrents_resume('all')
    

# Delete the targeted torrent
def delete_torrent(client: Client, hash: str, delete_files: bool):
    if hash is not None:
        try:
            client.torrents_delete(delete_files, hash)
        except Exception as err:
            LOGGER.warn(f"Unable to delete torrent '{hash}'")

# Return an array of torrent information based on the provided criteria
def get_torrent_info(client: Client, hash: str = None, status_filter: str = "all"):
    if hash == "" or hash == "all":
        hash = None

    try:
        torrents = client.torrents_info(torrent_hashes = hash, status_filter = status_filter, SIMPLE_RESPONSES = True)

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

    except Exception as err:
            LOGGER.warn(f"Unable to get info for torrent '{hash}' with status_filter {status_filter}")

            return {}

# Attempt to shut down the remote client
def shutdown(client: Client):
    try:
        client.app.shutdown()

    except Exception as err:
        LOGGER.error(err)

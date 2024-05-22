# Load .env
from env import Settings
config = Settings()

from const import RESULT_FAIL
import inspect
from RequestResult import RequestResult
import json
from MpdServer import MpdServer
from MpdStatus import MpdStatus
from typing import List
import mpdUtils
from mpd import MPDClient

def get_mpd_server_list():
    status_list, result_list = mpdUtils.get_mpd_server_list()
    return result_list

def get_mpd_status(serverName:str):
    if config.IS_DEBUG:
        print(f'[{inspect.getfile(inspect.currentframe())}][{inspect.stack()[0][3]}] serverName:', serverName)

    status_server, result_server = mpdUtils.get_mpd_server_by_name(serverName)
    if config.IS_DEBUG:
        print(f'[{inspect.getfile(inspect.currentframe())}][{inspect.stack()[0][3]}] status_server:', status_server)


    if status_server:
        return status_server
    
    if config.IS_DEBUG:
        print(f'[{inspect.getfile(inspect.currentframe())}][{inspect.stack()[0][3]}] result_server:', result_server)

    status_connect, client_connect = mpdUtils.mpd_connect_by_server(result_server)
    if status_connect:
        return status_connect
    
    if config.IS_DEBUG:
        print(f'[{inspect.getfile(inspect.currentframe())}][{inspect.stack()[0][3]}] client_connect:', client_connect)

    

    mpd_status = client_connect.status()
    if config.IS_DEBUG:
        print(f'[{inspect.getfile(inspect.currentframe())}][{inspect.stack()[0][3]}] mpd_status:', mpd_status)

    mpd_stats = client_connect.stats()
    if config.IS_DEBUG:
        print(f'[{inspect.getfile(inspect.currentframe())}][{inspect.stack()[0][3]}] mpd_stats:', mpd_stats)


    client_connect.disconnect()

    result = {**mpd_status, **mpd_stats}

    return result




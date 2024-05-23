# Load .env
from env import Settings
config = Settings()

from const import RESULT_FAIL
from const import MPD_COMMAND_PLAY, MPD_COMMAND_PAUSE, MPD_COMMAND_RESUME, MPD_COMMAND_STOP, MPD_COMMAND_STATUS


import inspect
from RequestResult import RequestResult
import mpdUtils
from MpdItem import MpdItem


def get_mpd_server_list():
    status_list, result_list = mpdUtils.get_mpd_server_list()
    return result_list

def get_mpd_status(mpdItem:MpdItem):
    if config.IS_DEBUG:
        print(f'[{inspect.getfile(inspect.currentframe())}][{inspect.stack()[0][3]}] mpdItem:', mpdItem)

    status_server, result_server = mpdUtils.get_mpd_server_by_name(mpdItem.server_name)
    if status_server:
        return status_server
    
    status_connect, client_connect = mpdUtils.mpd_connect_by_server(result_server)
    if status_connect:
        return status_connect
    
    mpd_status = client_connect.status()
    mpd_stats = client_connect.stats()
    client_connect.disconnect()

    result = {**mpd_status, **mpd_stats}
    if config.IS_DEBUG:
        print(f'[{inspect.getfile(inspect.currentframe())}][{inspect.stack()[0][3]}] mpd_status:', mpd_status)
        print(f'[{inspect.getfile(inspect.currentframe())}][{inspect.stack()[0][3]}] mpd_stats:', mpd_stats)
        print(f'[{inspect.getfile(inspect.currentframe())}][{inspect.stack()[0][3]}] result:', result)

    return result



def set_mpd_command(mpdItem:MpdItem):
    if config.IS_DEBUG:
        print(f'[{inspect.getfile(inspect.currentframe())}][{inspect.stack()[0][3]}] mpdItem:', mpdItem)

    status_server, result_server = mpdUtils.get_mpd_server_by_name(mpdItem.server_name)
    if status_server:
        return status_server
    
    status_connect, client_connect = mpdUtils.mpd_connect_by_server(result_server)
    if status_connect:
        return status_connect
    
    if mpdItem.command == MPD_COMMAND_PLAY:
        client_connect.play(0)
    elif mpdItem.command == MPD_COMMAND_STOP:
        client_connect.stop()
    elif mpdItem.command == MPD_COMMAND_PAUSE:
        client_connect.pause(1)
    elif mpdItem.command == MPD_COMMAND_RESUME:
        client_connect.pause(0)
    else:
        print(f'[{inspect.getfile(inspect.currentframe())}][{inspect.stack()[0][3]}] os exception:', str(e))
        requestResult = RequestResult()
        requestResult.result = RESULT_FAIL
        requestResult.msg = f"정의되지 않은 COMMAND입니다.[{mpdItem.command}]"
        requestResult.method = f'{inspect.stack()[0][3]}'
        return requestResult        

    client_connect.disconnect()
    return mpdItem
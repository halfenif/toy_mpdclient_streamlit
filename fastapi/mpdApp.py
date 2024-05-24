# Load .env
from env import Settings
config = Settings()

from const import RESULT_FAIL
from const import MPD_COMMAND_PLAY, MPD_COMMAND_PAUSE, MPD_COMMAND_RESUME, MPD_COMMAND_STOP, MPD_COMMAND_STATUS, MPD_COMMAND_PREVIOUS, MPD_COMMAND_NEXT, MPD_COMMAND_VOLUME
from const import MPD_COMMAND_REPEAT, MPD_COMMAND_SINGLE, MPD_COMMAND_RANDOM, MPD_COMMAND_CONSUME

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
    
    try:
        if mpdItem.command == MPD_COMMAND_PLAY:
            client_connect.play(0)
        elif mpdItem.command == MPD_COMMAND_STOP:
            client_connect.stop()
        elif mpdItem.command == MPD_COMMAND_PAUSE:
            client_connect.pause(1)
        elif mpdItem.command == MPD_COMMAND_RESUME:
            client_connect.pause(0)
        elif mpdItem.command == MPD_COMMAND_PREVIOUS:
            client_connect.previos()
        elif mpdItem.command == MPD_COMMAND_NEXT:
            client_connect.next()   
        elif mpdItem.command == MPD_COMMAND_VOLUME:
            client_connect.setvol(mpdItem.command_value_int)
        elif mpdItem.command == MPD_COMMAND_REPEAT:
            client_connect.repeat(mpdItem.command_value_int)
        elif mpdItem.command == MPD_COMMAND_SINGLE:
            client_connect.single(mpdItem.command_value_int)
        elif mpdItem.command == MPD_COMMAND_RANDOM:
            client_connect.random(mpdItem.command_value_int)
        elif mpdItem.command == MPD_COMMAND_CONSUME:
            client_connect.consume(mpdItem.command_value_int)
        else:
            print(f'[{inspect.getfile(inspect.currentframe())}][{inspect.stack()[0][3]}] os exception:', str(e))
            requestResult = RequestResult()
            requestResult.result = RESULT_FAIL
            requestResult.msg = f"정의되지 않은 COMMAND입니다.[{mpdItem.command}]"
            requestResult.method = f'{inspect.stack()[0][3]}'
            return requestResult
    except Exception as e:
        print(f'[{inspect.getfile(inspect.currentframe())}][{inspect.stack()[0][3]}] MPD command exception:', str(e))
        requestResult = RequestResult()
        requestResult.result = RESULT_FAIL
        requestResult.msg = f"MPD command exception입니다.[{str(e)}]"
        requestResult.method = f'{inspect.stack()[0][3]}'
        return requestResult
    
    client_connect.disconnect()
    return mpdItem
# Load .env
from env import Settings
config = Settings()

from const import RESULT_FAIL
from const import PATH_LOCATION_TARGET
from const import MPD_ITEM_PLAYLIST_QUEE, MPD_ITEM_DISPLAY_NAME
from const import MPD_COMMAND_PLAY, MPD_COMMAND_PAUSE, MPD_COMMAND_RESUME, MPD_COMMAND_STOP, MPD_COMMAND_STATUS, MPD_COMMAND_PREVIOUS, MPD_COMMAND_NEXT, MPD_COMMAND_VOLUME
from const import MPD_COMMAND_REPEAT, MPD_COMMAND_SINGLE, MPD_COMMAND_RANDOM, MPD_COMMAND_CONSUME
from const import MPD_COMMAND_QUEE_CLEAR, MPD_COMMAND_QUEE_DELETE, MPD_COMMAND_QUEE_ADD

import inspect
from RequestResult import RequestResult
import mpdUtils
from MpdItem import MpdItem
import fileUtils

import os

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
    mpd_quee_info = client_connect.playlistinfo()

    client_connect.disconnect()

    result = {**mpd_status, **mpd_stats}
    if mpd_quee_info:
        mpd_quee_info_result = []

        for item in mpd_quee_info:
            baseFileName = os.path.basename(item["file"])

            if config.UI_OPTION_SHORT_FILE_NAME:
                item[MPD_ITEM_DISPLAY_NAME] = fileUtils.getDisplayFileName(baseFileName)
            else:
                item[MPD_ITEM_DISPLAY_NAME] = baseFileName
            mpd_quee_info_result.append(item)
        result[MPD_ITEM_PLAYLIST_QUEE] = mpd_quee_info_result
    

    if config.IS_DEBUG:
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
        elif mpdItem.command == MPD_COMMAND_QUEE_CLEAR:
            client_connect.clear()
        elif mpdItem.command == MPD_COMMAND_QUEE_DELETE:
            client_connect.deleteid(mpdItem.song_id)
        elif mpdItem.command == MPD_COMMAND_QUEE_ADD:
            # 경로에 대한 이해
            # 본 프로젝트의 file & folder navigation은 filemover project에서 가지고 온것이다. (https://github.com/halfenif/toy_filemover_streamlit)
            # 그러다 보니, Encode Path는 /로 시작한다. (원래는 [SOURCE & TARGET] + Encode Path인 것이다.)
            # 그런데, 화면상에서 올라오는 Encode Path의 root와 MPD Music Folder의 root가 동일(상대경로)한 것을 가정하고 구현하기 때문에, Encode Path의 맨 앞 /만 없으면 경로가 동일해야 한다.
            result_path_docode = fileUtils.getPathDecode(mpdItem.song_path_encode)[1:]

            if config.IS_DEBUG:
                print(f'[{inspect.getfile(inspect.currentframe())}][{inspect.stack()[0][3]}] result_path_docode:', result_path_docode)

            client_connect.add(result_path_docode)
        else:
            requestResult = RequestResult()
            requestResult.result = RESULT_FAIL
            requestResult.msg = f"정의되지 않은 COMMAND입니다.[{mpdItem.command}]"
            requestResult.method = f'{inspect.stack()[0][3]}'
            print(f'[{inspect.getfile(inspect.currentframe())}][{inspect.stack()[0][3]}] ', requestResult.msg)
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
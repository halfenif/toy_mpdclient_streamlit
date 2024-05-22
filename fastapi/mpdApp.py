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

def get_mpd_server_list():
    if config.IS_DEBUG:
        print(f'[{inspect.getfile(inspect.currentframe())}][{inspect.stack()[0][3]}] config.MPD_SERVER_LIST:', config.MPD_SERVER_LIST)

    try:
        servers = json.loads(config.MPD_SERVER_LIST)["servers"]
    except json.JSONDecodeError as e:
        print(f'[{inspect.getfile(inspect.currentframe())}][{inspect.stack()[0][3]}] Exception:', str(e))
        requestResult = RequestResult()
        requestResult.result = RESULT_FAIL
        requestResult.msg = f"MPD_SERVER_IP의 JSON문자열을 확인하시기 바랍니다. {str(e)}"
        requestResult.method = f'{inspect.stack()[0][3]}'
        return requestResult 
    
    result = []
    
    for server in servers:
        if config.IS_DEBUG:
            print(f'[{inspect.getfile(inspect.currentframe())}][{inspect.stack()[0][3]}] server:', server)
        
        mpdServer = MpdServer()
        mpdServer.name = server["NAME"]
        mpdServer.display_name = f'{server["IP"]}:{server["PORT"]}'
        mpdServer.ip = server["IP"]
        mpdServer.port = server["PORT"]

        result.append(mpdServer)
        
    return result

def get_mpd_status():
    if config.IS_DEBUG:
        print(f'[{inspect.getfile(inspect.currentframe())}][{inspect.stack()[0][3]}] config.MPD_SERVER_LIST:', config.MPD_SERVER_LIST)

    try:
        servers = json.loads(config.MPD_SERVER_LIST)["servers"]
    except json.JSONDecodeError as e:
        print(f'[{inspect.getfile(inspect.currentframe())}][{inspect.stack()[0][3]}] Exception:', str(e))
        requestResult = RequestResult()
        requestResult.result = RESULT_FAIL
        requestResult.msg = f"MPD_SERVER_IP의 JSON문자열을 확인하시기 바랍니다. {str(e)}"
        requestResult.method = f'{inspect.stack()[0][3]}'
        return requestResult 
    
    mpdStatus = MpdStatus()
    
    for server in servers:
        if config.IS_DEBUG:
            print(f'[{inspect.getfile(inspect.currentframe())}][{inspect.stack()[0][3]}] server:', server)
        
        mpdServer = MpdServer()
        mpdServer.name = server["NAME"]
        mpdServer.display_name = f'{server["IP"]}:{server["PORT"]}'
        mpdServer.ip = server["IP"]
        mpdServer.port = server["PORT"]

        mpdStatus.servers.append(mpdServer)


    return mpdStatus
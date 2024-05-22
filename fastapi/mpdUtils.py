# Load .env
from env import Settings
config = Settings()

from mpd import MPDClient
from const import RESULT_FAIL
import inspect
from RequestResult import RequestResult
import json
from MpdServer import MpdServer

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
        return requestResult, None
    
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

    return None, result

def get_mpd_server_by_name(serverName:str):
    if config.IS_DEBUG:
        print(f'[{inspect.getfile(inspect.currentframe())}][{inspect.stack()[0][3]}] serverName:', serverName)

    status_list, result_list = get_mpd_server_list()

    if status_list:
        if config.IS_DEBUG:
            print(f'[{inspect.getfile(inspect.currentframe())}][{inspect.stack()[0][3]}] status_list:', status_list)        
        return status_list, None
    
    if config.IS_DEBUG:
        print(f'[{inspect.getfile(inspect.currentframe())}][{inspect.stack()[0][3]}] result_list:', result_list)

    for server in result_list:
        if config.IS_DEBUG:
            print(f'[{inspect.getfile(inspect.currentframe())}][{inspect.stack()[0][3]}] type of server:', type(server))
            print(f'[{inspect.getfile(inspect.currentframe())}][{inspect.stack()[0][3]}] server:', server)
        
        

        if server.name == serverName:
            if config.IS_DEBUG:
                print(f'[{inspect.getfile(inspect.currentframe())}][{inspect.stack()[0][3]}] Find Server:', server)
            return None, server
        
    # 여기까지 오면 없는 것임
    requestResult = RequestResult()
    requestResult.result = RESULT_FAIL
    requestResult.msg = f"MPD SERVER의 NAME이 존재하지 않습니다. {serverName}"
    requestResult.method = f'{inspect.stack()[0][3]}'

    if config.IS_DEBUG:
        print(f'[{inspect.getfile(inspect.currentframe())}][{inspect.stack()[0][3]}] requestResult:', requestResult)

    return requestResult, None



def mpd_connect_by_server(server:MpdServer):
    if config.IS_DEBUG:
        print(f'[{inspect.getfile(inspect.currentframe())}][{inspect.stack()[0][3]}] server:', server)

    client = MPDClient()

    try:
        client.connect(server.ip, server.port)
        if config.IS_DEBUG:
            print(f'[{inspect.getfile(inspect.currentframe())}][{inspect.stack()[0][3]}] mpd_version:', client.mpd_version)        
        if not client.mpd_version:
            requestResult = RequestResult()
            requestResult.result = RESULT_FAIL
            requestResult.msg = f'MPD에 연결 할 수 없습니다.[{server.displayName}]'
            requestResult.method = f'{inspect.stack()[0][3]}'
            return requestResult, None
        
        return None, client

    except Exception as e:
        print(f'[{inspect.getfile(inspect.currentframe())}][{inspect.stack()[0][3]}] Exception:', str(e))
        requestResult = RequestResult()
        requestResult.result = RESULT_FAIL
        requestResult.msg = f'{str(e)}, {server.displayName}'
        requestResult.method = f'{inspect.stack()[0][3]}'
        return requestResult, None


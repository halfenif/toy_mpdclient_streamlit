# Load .env
from env import Settings
config = Settings()

import requests
import streamlit as st
import const
import inspect


# interact with FastAPI endpoint
backend = config.URL_BACKEND


## Utils ----------------
def result_check(response: any):
    if response.status_code == 200:

        #Result Check
        try:
            result_state_str = response.json()["Result"]
            if(result_state_str == const.RESULT_FAIL):
                message = response.json()["Message"] + ' @ ' + response.json()["Method"]
                st.error(message, icon="🚨")
                return "", 500
            
            # 정상응답인경우
            return response.status_code, response.json()
        except:
            # Arrry에는 Result가 없다.
            return response.status_code, response.json()

    else:
        # Server에서 오류응답인경우
        message = "호출오류: Http Status Code is " + str(response.status_code)
        st.error(message, icon="🔥")        
        return response.status_code, ""

def result_check_binary(response: any):
    if response.status_code == 200:

        #Result Check
        try:
            result_state_str = response.json()["Result"]
            if(result_state_str == const.RESULT_FAIL):
                message = response.json()["Message"] + ' @ ' + response.json()["Method"]
                st.error(message, icon="🚨")
                return "", 500
            
            # 정상응답인경우
            return response.status_code, response.content
        except:
            # 정상응답인경우
            return response.status_code, response.content

    else:
        # Server에서 오류응답인경우
        message = "호출오류: Http Status Code is " + str(response.status_code)
        st.error(message, icon="🔥")        
        return response.status_code, ""


def request_exception(e: any, client_method: str):
    message = "호출오류:" + str(e) + ' @ ' + client_method
    st.error(message, icon="🔥")

## Method ----------------
def api_test():
    try:
        response = requests.get(backend + inspect.stack()[0][3], params={})
        return result_check(response)
    except requests.exceptions.RequestException as e:
        request_exception(e, inspect.stack()[0][3])

def get_mpd_server_list():
    try:
        response = requests.get(backend + inspect.stack()[0][3], params={})
        return result_check(response)
    except requests.exceptions.RequestException as e:
        request_exception(e, inspect.stack()[0][3])

def get_mpd_status(mpdItem: any):
    try:
        response = requests.get(backend + inspect.stack()[0][3], params=mpdItem)
        return result_check(response)
    except requests.exceptions.RequestException as e:
        request_exception(e, inspect.stack()[0][3])

def set_mpd_command(mpdItem: any):
    try:
        response = requests.get(backend + inspect.stack()[0][3], params=mpdItem)
        return result_check(response)
    except requests.exceptions.RequestException as e:
        request_exception(e, inspect.stack()[0][3])





def list_folder_and_file_by_path(rootType: str, pathEncode: str):
    try:
        response = requests.get(backend + inspect.stack()[0][3], params={'rootType':rootType, 'pathEncode':pathEncode})
        return result_check(response)
    except requests.exceptions.RequestException as e:
        request_exception(e, inspect.stack()[0][3])

    
def download_file_by_path(rootType: str, pathEncode: str):
    try:
        response = requests.get(backend + inspect.stack()[0][3], params={'rootType':rootType, 'pathEncode':pathEncode})
        return result_check_binary(response)
    except requests.exceptions.RequestException as e:
        request_exception(e, inspect.stack()[0][3])
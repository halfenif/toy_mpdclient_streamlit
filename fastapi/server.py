# Load .env
from env import Settings
config = Settings()

print(f'config.ENV_TYPE:{config.ENV_TYPE}')

from fastapi import FastAPI, Depends, File, Request
import inspect

import folderApp
import tagApp

from FileItem import FileItem
from TagItem import TagItem
from FolderItem import FolderItem
from MpdItem import MpdItem
import const
from RequestResult import RequestResult
import fileUtils

import mpdApp



# --------------------------------------------------------------
# Application
app = FastAPI(
    title="FastAPI for FileMover",
    description="""Wow""",
    version="0.1.0",
)


# --------------------------------------------------------------
# Router

# API Test
@app.get("/api_test")
def api_test():
    print(f'test:')
    return {"name":"Name is Name"}

# MPD Server List
@app.get("/get_mpd_server_list")
def get_mpd_server_list():
    return mpdApp.get_mpd_server_list()

# MPD Status
@app.get("/get_mpd_status")
def get_mpd_status(mpdItem:MpdItem = Depends()):
    return mpdApp.get_mpd_status(mpdItem)

# MPD command
@app.get("/set_mpd_command")
def set_mpd_command(mpdItem:MpdItem = Depends()):
    return mpdApp.set_mpd_command(mpdItem)








# Folder And File List
@app.get("/list_folder_and_file_by_path")
def list_folder_and_file_by_path(rootType: str, pathEncode: str):
    # Debug
    if config.IS_DEBUG:
        print(f'[{inspect.getfile(inspect.currentframe())}][{inspect.stack()[0][3]}] rootType:', rootType)
        print(f'[{inspect.getfile(inspect.currentframe())}][{inspect.stack()[0][3]}] pathDecode:', pathEncode)    
    return folderApp.list_folder_and_file_by_path(rootType, pathEncode)




# Read Tag Info
@app.get("/file_read_taginfo_by_path")
def file_read_taginfo_by_path(fileItem: FileItem = Depends()):
    # Debug
    if config.IS_DEBUG:
        print(f'[{inspect.getfile(inspect.currentframe())}][{inspect.stack()[0][3]}] fileItem:', fileItem)

    return tagApp.file_read_taginfo_by_path(fileItem)



# Folder Action
@app.get("/folder_action")
def folder_action(folderItem: FolderItem = Depends()):
    # Debug
    if config.IS_DEBUG:
        print(f'[{inspect.getfile(inspect.currentframe())}][{inspect.stack()[0][3]}] folderItem:', folderItem)

    return folderApp.folder_action(folderItem)


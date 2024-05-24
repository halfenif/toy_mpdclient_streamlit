# Load .env
from env import Settings
config = Settings()

print(f'config.ENV_TYPE:{config.ENV_TYPE}')

from fastapi import FastAPI, Depends, File, Request
import inspect

import folderApp
from MpdItem import MpdItem
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

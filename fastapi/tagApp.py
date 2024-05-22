# Load .env
from env import Settings
config = Settings()

import os
from genericpath import isdir
import inspect

from const import PATH_LOCATION_SOURCE, PATH_LOCATION_TARGET, RESULT_FAIL
import fileUtils
from TagItem import TagItem
from RequestResult import RequestResult

import tagUtils

from FileItem import FileItem

from pathlib import Path


# 파일의 mp3 tag를 Read하는 함수
def file_read_taginfo_by_path(fileItem: FileItem):

    # Debug
    if config.IS_DEBUG:
        print(f'[{inspect.getfile(inspect.currentframe())}][{inspect.stack()[0][3]}] fileItem:', fileItem)

    stateCheck, pathFull, isRoot = fileUtils.getFullPath(fileItem.root_type, fileItem.path_encode)
    if stateCheck:
        return stateCheck
    
    stateCheck, tagItem = tagUtils.get_tag(pathFull, fileItem)
    if stateCheck:
        return stateCheck    

    if config.IS_DEBUG:
        print(f'[{inspect.getfile(inspect.currentframe())}][{inspect.stack()[0][3]}] tagItem:', tagItem)

    return tagItem


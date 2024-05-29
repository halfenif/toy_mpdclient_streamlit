DATE_FORMAT = "%Y-%m-%d"

ENC_TYPE = 'utf-8'

PATH_TYPE_FOLDER = "FOLDER"
PATH_TYPE_FILE = "FILE"
PATH_TYPE_PARENT_FOLDER = "PARENT-FOLDER"

PATH_LOCATION_SOURCE = "SOURCE"
PATH_LOCATION_TARGET = "TARGET"

RESULT_SUCCESS = "SUCCESS"
RESULT_FAIL = "FAIL"

# Docker Internal
FOLDER_CONFIG = {
    'SOURCE': '/app/source',
    'TARGET': '/app/target'
}


SUPPORT_EXT = [".mp3",".flac",".ogg"]

MPD_ITEM_PLAYLIST_QUEE="playlist_quee"
MPD_ITEM_DISPLAY_NAME="display_name"
MPD_ITEM_CURRENT_SONG="current_song"

MPD_COMMAND_STATUS="status"
MPD_COMMAND_PLAY="play"
MPD_COMMAND_STOP="stop"
MPD_COMMAND_PAUSE="pause"
MPD_COMMAND_RESUME="resume"
MPD_COMMAND_NEXT="next"
MPD_COMMAND_PREVIOUS="previous"
MPD_COMMAND_VOLUME="volume"

MPD_COMMAND_LOOP="loop"
MPD_COMMAND_REPEAT="repeat"
MPD_COMMAND_SINGLE="single"
MPD_COMMAND_RANDOM="random"
MPD_COMMAND_CONSUME="consume"

MPD_COMMAND_QUEE_CLEAR="quee-clear"
MPD_COMMAND_QUEE_DELETE="quee-delete-item"
MPD_COMMAND_QUEE_DOWN="quee-down-item"
MPD_COMMAND_QUEE_UP="quee-up-item"
MPD_COMMAND_QUEE_ADD="quee-add-item"
MPD_COMMAND_QUEE_PLAY="quee-play-item"
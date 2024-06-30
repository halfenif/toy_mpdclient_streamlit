# Load .env
from env import Settings
config = Settings()

from const import PATH_LOCATION_TARGET, PATH_TYPE_FOLDER, PATH_TYPE_FILE


from session import S_SERVER_LIST, S_CURRENT_SERVER_NAME
from session import S_CURRENT_TARGET_FOLDER # rerun() 했을 때 화면 갱신용
from session import S_CURRENT_TARGET_FOLDER_DISPLAY # rerun() 했을 때 화면 갱신용

from session import S_UI_VOLUME, S_UI_LOOP_REPEAT, S_UI_LOOP_SINGLE, S_UI_LOOP_RANDOM, S_UI_LOOP_CONSUME, S_UI_QUEE_CLEAR
from session import S_UI_SELECT_COMMAND_PLAY, S_UI_SELECT_COMMAND_LOOP, S_UI_SELECT_COMMAND_QUEE, S_UI_SELECT_COMMAND_TARGET

from session import S_UI_COMMON_ITEM_SELECT_INIT, S_UI_QUEE_ITEM_COMMAND_CLEAR, S_UI_QUEE_ITEM_COMMAND_REMOVE, S_UI_QUEE_ITEM_COMMAND_UP, S_UI_QUEE_ITEM_COMMAND_DOWN, S_UI_QUEE_ITEM_COMMAND_PLAY
from session import S_UI_TARGET_ITEM_COMMAND_ADD_QUEE, S_UI_TARGET_ITEM_COMMAND_VIEW_TAG, S_UI_TARGET_ITEM_COMMAND_DOWNLOAD

from session import S_CURRENT_SELECT_ITEM_QUEE, S_CURRENT_SELECT_ITEM_TARGET

from const import MPD_ITEM_STATE, MPD_ITEM_PLAYLIST_QUEE, MPD_ITEM_DISPLAY_NAME, MPD_ITEM_CURRENT_SONG

from const import MPD_COMMAND_PLAY, MPD_COMMAND_STOP, MPD_COMMAND_PAUSE, MPD_COMMAND_RESUME, MPD_COMMAND_STATUS, MPD_COMMAND_PREVIOUS, MPD_COMMAND_NEXT, MPD_COMMAND_VOLUME
from const import MPD_COMMAND_LOOP, MPD_COMMAND_REPEAT, MPD_COMMAND_SINGLE, MPD_COMMAND_RANDOM, MPD_COMMAND_CONSUME
from const import MPD_COMMAND_QUEE_CLEAR, MPD_COMMAND_QUEE_DELETE, MPD_COMMAND_QUEE_ADD, MPD_COMMAND_QUEE_DOWN, MPD_COMMAND_QUEE_UP, MPD_COMMAND_QUEE_PLAY


from const import EMOJI_PLAY, EMOJI_STOP, EMOJI_QUEE_DELETE, EMOJI_REFRESH, EMOJI_UP, EMOJI_DOWN


import streamlit as st
from api import list_folder_and_file_by_path, get_mpd_server_list ,get_mpd_status, set_mpd_command, download_file_by_path
import uuid

from MpdItem import MpdItem

import copy

# Session -------------------
if S_SERVER_LIST not in st.session_state:
    status_server_list, result_server_list = get_mpd_server_list()
    if not status_server_list == 200:
        st.stop()
    
    # Server List
    st.session_state[S_SERVER_LIST] = result_server_list

    # Default Server
    for server in result_server_list:
        st.session_state[S_CURRENT_SERVER_NAME] = server["name"]
        break



if S_CURRENT_TARGET_FOLDER not in st.session_state:
    st.session_state[S_CURRENT_TARGET_FOLDER] = ''
    st.session_state[S_CURRENT_TARGET_FOLDER_DISPLAY] = ''

if S_CURRENT_SELECT_ITEM_QUEE not in st.session_state:
    st.session_state[S_CURRENT_SELECT_ITEM_QUEE] = S_UI_QUEE_ITEM_COMMAND_REMOVE

if S_CURRENT_SELECT_ITEM_TARGET not in st.session_state:
    st.session_state[S_CURRENT_SELECT_ITEM_TARGET] = S_UI_TARGET_ITEM_COMMAND_ADD_QUEE




# Page Setup
st.set_page_config(
    page_title="MPD Client for Home",
    page_icon=":musical_note:",
    menu_items={
        'About': """
# MPD Client for Home
Simple is BEST.

---

GitHub: [halfenif/toy_mpdclient_streamlit](https://github.com/halfenif/toy_mpdclient_streamlit)

Blog: [Enif's small talk](https://blog.enif.page/blog/)

---

[MPD](https://www.musicpd.org/) : Music Player Daemon.  
[python-mpd2](https://python-mpd2.readthedocs.io/en/latest/index.html) : Python MPD lib.
[Home Assistant](https://www.home-assistant.io/) : My favorite Home Automation platform.  

---

"""
    }
)



# Sidebar Width
st.markdown(
    "<style> section[data-testid='stSidebar'] { width: " + f"{config.UI_OPTION_SIDEBAR_WIDTH}" + "px !important; } </style>",
    unsafe_allow_html=True,
)

#---------------------------------------------------------------------
# Function

def fn_display_page_header():

    # Title
    if config.UI_OPTION_TITLE:
        st.title(config.UI_OPTION_TITLE)
    
    if config.UI_OPTION_DESC:
        st.write(config.UI_OPTION_DESC)

    if config.UI_OPTION_LINK_TITLE and config.UI_OPTION_LINK_URL:
        st.link_button(config.UI_OPTION_LINK_TITLE , config.UI_OPTION_LINK_URL)

def fn_file_select(fileitem):
    if st.session_state[S_CURRENT_SELECT_ITEM_TARGET] == S_UI_TARGET_ITEM_COMMAND_ADD_QUEE:
        fn_mpd_quee(MPD_COMMAND_QUEE_ADD, fileitem)
    elif st.session_state[S_CURRENT_SELECT_ITEM_TARGET] == S_UI_TARGET_ITEM_COMMAND_DOWNLOAD:
        status_file, result_file =  download_file_by_path(fileitem["rootType"], fileitem["pathEncode"])

        if status_file == 200:
            st.download_button(f'Download File: {fileitem["fileName"]}', result_file, fileitem["fileName"])

    elif st.session_state[S_CURRENT_SELECT_ITEM_TARGET] == S_UI_TARGET_ITEM_COMMAND_VIEW_TAG:
        # Sidebar Tag Info
        st.write(st.session_state[S_CURRENT_SELECT_ITEM_TARGET])
    else:
        st.error(f"정의되지않은 Target Command 유형입니다. {st.session_state[S_CURRENT_SELECT_ITEM_TARGET]}")
    
    
#---------------------------------------------------------------------
def fn_folder_select(fileitem):
    # Body Folder Select
    if fileitem["rootType"] == PATH_LOCATION_TARGET:
        st.session_state[S_CURRENT_TARGET_FOLDER] = fileitem["pathEncode"]
        st.session_state[S_CURRENT_TARGET_FOLDER_DISPLAY] = fileitem["folderCurrent"]

#---------------------------------------------------------------------
def fn_make_button_lable(fileitem):

    buttonEmoji = ""
    if fileitem["pathType"] == PATH_TYPE_FOLDER:
        buttonEmoji = ":file_folder:"
    elif fileitem["pathType"] == PATH_TYPE_FILE:

        if st.session_state[S_CURRENT_SELECT_ITEM_TARGET] == S_UI_TARGET_ITEM_COMMAND_ADD_QUEE:
            buttonEmoji = ":musical_note:"
        elif st.session_state[S_CURRENT_SELECT_ITEM_TARGET] == S_UI_TARGET_ITEM_COMMAND_VIEW_TAG:
            buttonEmoji = ":id:"
        elif st.session_state[S_CURRENT_SELECT_ITEM_TARGET] == S_UI_TARGET_ITEM_COMMAND_DOWNLOAD:
            buttonEmoji = ":floppy_disk:"
        else:
            buttonEmoji = EMOJI_QUEE_DELETE    

    if fileitem["isParent"]:
        buttonEmoji = ":back:"

    display_file_name = buttonEmoji + " " + fileitem["fileNameDisplay"]

       
    return display_file_name

#---------------------------------------------------------------------
def fn_make_button_callback(fileitem):
    if fileitem["pathType"] == PATH_TYPE_FILE:
        return fn_file_select
    else:
        return fn_folder_select
    

def fn_check_int_bool(int_value:str):
    if int(int_value) == 0:
        return False
    else:
        return True
    
def fn_check_bool_int(bool_value:bool):
    if bool_value == True:
        return 1
    else:
        return 0

def fn_mpd_command(mpdItem:MpdItem):
    mpdItem.server_name = str(st.session_state[S_CURRENT_SERVER_NAME])
    status_command, result_command = set_mpd_command(mpdItem)
    # if not status_command == 200:
    #     st.stop()

def fn_mpd_volume():
    # Init MPD Item
    mpdItem = MpdItem()
    mpdItem.command = MPD_COMMAND_VOLUME
    mpdItem.command_value_int = int(st.session_state[S_UI_VOLUME])
    fn_mpd_command(mpdItem)


#----------------------------------------        
# UI에서 Item을 변경 한 경우
def fn_select_command_loop():
    # Init MPD Item
    mpdItem = MpdItem()
    mpdItem.command = MPD_COMMAND_LOOP

    # Loop Conteol은 multi select이고 uuid를 key로 매번 생성된다.
    loop_selected = st.session_state[st.session_state[S_UI_SELECT_COMMAND_LOOP]]

    if MPD_COMMAND_REPEAT in loop_selected:
        mpdItem.loop_repeat = 1

    if MPD_COMMAND_RANDOM in loop_selected:
        mpdItem.loop_random = 1

    if MPD_COMMAND_SINGLE in loop_selected:
        mpdItem.loop_single = 1

    if MPD_COMMAND_CONSUME in loop_selected:
        mpdItem.loop_consume = 1
    
    fn_mpd_command(mpdItem)

#----------------------------------------
def fn_select_command_play_select():
    if not st.session_state[S_UI_SELECT_COMMAND_PLAY] == S_UI_COMMON_ITEM_SELECT_INIT:
        # Init MPD Item
        mpdItem = MpdItem()
        mpdItem.command = st.session_state[S_UI_SELECT_COMMAND_PLAY]
        st.session_state[S_UI_SELECT_COMMAND_PLAY] = S_UI_COMMON_ITEM_SELECT_INIT
        fn_mpd_command(mpdItem)
    else:
        st.error("Current S_UI_SELECT_COMMAND_PLAY is S_UI_COMMON_ITEM_SELECT_INIT")
    
def fn_select_command_play_button(play_command: str):
    # Init MPD Item
    mpdItem = MpdItem()
    mpdItem.command = play_command
    fn_mpd_command(mpdItem)
    st.rerun()


# Quee Select Changed
def fn_select_command_quee():
    if st.session_state[S_UI_SELECT_COMMAND_QUEE] == S_UI_QUEE_ITEM_COMMAND_CLEAR:
        # Init MPD Item
        mpdItem = MpdItem()
        mpdItem.command = MPD_COMMAND_QUEE_CLEAR
        fn_mpd_command(mpdItem)

    elif st.session_state[S_UI_SELECT_COMMAND_QUEE] == S_UI_QUEE_ITEM_COMMAND_REMOVE:
        st.session_state[S_CURRENT_SELECT_ITEM_QUEE] = S_UI_QUEE_ITEM_COMMAND_REMOVE
    elif st.session_state[S_UI_SELECT_COMMAND_QUEE] == S_UI_QUEE_ITEM_COMMAND_PLAY:
        st.session_state[S_CURRENT_SELECT_ITEM_QUEE] = S_UI_QUEE_ITEM_COMMAND_PLAY

    elif st.session_state[S_UI_SELECT_COMMAND_QUEE] == S_UI_QUEE_ITEM_COMMAND_UP:
        st.session_state[S_CURRENT_SELECT_ITEM_QUEE] = S_UI_QUEE_ITEM_COMMAND_UP
    elif st.session_state[S_UI_SELECT_COMMAND_QUEE] == S_UI_QUEE_ITEM_COMMAND_DOWN:
        st.session_state[S_CURRENT_SELECT_ITEM_QUEE] = S_UI_QUEE_ITEM_COMMAND_DOWN
    else:
        st.error(f"Not defined quee command: {st.session_state[S_CURRENT_SELECT_ITEM_QUEE]}")
        
# Quee Button Clicked
def fn_mpd_quee(command:str, item:any):
    # Init MPD Item
    mpdItem = MpdItem()
    mpdItem.command = command

    if command == MPD_COMMAND_QUEE_DELETE or command == MPD_COMMAND_QUEE_PLAY or command == MPD_COMMAND_QUEE_UP or command == MPD_COMMAND_QUEE_DOWN:
        if not "id" in item:
            st.error(f'{command}: item no attribute playlist quee song "id"')
            st.stop()
        mpdItem.song_id = int(item["id"])
    elif command == MPD_COMMAND_QUEE_ADD:
        mpdItem.song_path_encode = item["pathEncode"]

    fn_mpd_command(mpdItem)

def fn_select_command_target():
    st.session_state[S_CURRENT_SELECT_ITEM_TARGET] = st.session_state[S_UI_SELECT_COMMAND_TARGET]

#---------------------------------------------------------------------




# Page Header
fn_display_page_header()

# Colums
c_status, c_target = st.columns(2, gap="small")

# Container MPD Status
with c_status:
    # st.write(st.session_state[S_CURRENT_SERVER_NAME])
    # st.write(st.session_state[S_SERVER_LIST])


    # Init MPD Server
    select_server_options = []
    select_index: int = 0
    loop_i = 0
    for server in st.session_state[S_SERVER_LIST]:
        select_server_options.append(server["name"])
        if st.session_state[S_CURRENT_SERVER_NAME] == server["name"]:
            select_index = loop_i
        loop_i += 1


    # Display Select
    select_server_changed = st.selectbox("Server", select_server_options, select_index)
    if not select_server_changed == st.session_state[S_CURRENT_SERVER_NAME]:
        st.session_state[S_CURRENT_SERVER_NAME] = select_server_changed
        st.rerun()

    # Init MPD Item
    mpdItem = MpdItem()
    mpdItem.server_name = str(st.session_state[S_CURRENT_SERVER_NAME])

    # Call MPD Status
    mpdItem.command = MPD_COMMAND_STATUS
    # st.write(mpdItem)
    # st.stop()

    status_mpd_status, result_mpd_status = get_mpd_status(mpdItem)
    if not status_mpd_status == 200:
        st.stop()
    

    if MPD_ITEM_STATE in result_mpd_status:

        refresh_clicked = st.button(f"{EMOJI_REFRESH} Refresh")
        if refresh_clicked:
            st.rerun()

        # Current Song if play
        if result_mpd_status[MPD_ITEM_STATE] == MPD_COMMAND_PLAY:
            if MPD_ITEM_CURRENT_SONG in result_mpd_status:
                st.write("Playing")
                st.info(f"{result_mpd_status[MPD_ITEM_CURRENT_SONG]}")

        # Volume
        if MPD_COMMAND_VOLUME in result_mpd_status:
            volume_control = st.empty()
            volume_control.slider("Volume", min_value=0, max_value=100, value=int(result_mpd_status["volume"]), step=5, on_change=fn_mpd_volume, key=S_UI_VOLUME)
        else:
            st.warning(f'{str(st.session_state[S_CURRENT_SERVER_NAME])} not support volume')

        # play button
        if result_mpd_status[MPD_ITEM_STATE] == MPD_COMMAND_STOP:
            play_command_options = [S_UI_COMMON_ITEM_SELECT_INIT, MPD_COMMAND_PLAY]

            btn_clicked = st.button(f"{EMOJI_PLAY} Play")
            if btn_clicked:
                fn_select_command_play_button(MPD_COMMAND_PLAY)
        else:
            btn_clicked = st.button(f"{EMOJI_STOP} Stop")
            if btn_clicked:
                fn_select_command_play_button(MPD_COMMAND_STOP)

            if result_mpd_status[MPD_ITEM_STATE] == MPD_COMMAND_PAUSE:
                play_command_options = [S_UI_COMMON_ITEM_SELECT_INIT, MPD_COMMAND_PLAY, MPD_COMMAND_RESUME]
            elif result_mpd_status[MPD_ITEM_STATE] == MPD_COMMAND_PLAY:
                play_command_options = [S_UI_COMMON_ITEM_SELECT_INIT, MPD_COMMAND_PLAY, MPD_COMMAND_STOP, MPD_COMMAND_PREVIOUS, MPD_COMMAND_PAUSE, MPD_COMMAND_NEXT]
            else:
                play_command_options = [f"? not defined {result_mpd_status[MPD_ITEM_STATE]}"]
       
            st.selectbox("Other Play Command", play_command_options, index=0, on_change=fn_select_command_play_select, key=S_UI_SELECT_COMMAND_PLAY)


        # Loop Muliti Select
        loop_base = [MPD_COMMAND_REPEAT, MPD_COMMAND_SINGLE, MPD_COMMAND_RANDOM, MPD_COMMAND_CONSUME]
        
        # Init
        loop_selected = []
        
        # Check Server value
        if MPD_COMMAND_REPEAT in result_mpd_status:
            bool_value = fn_check_int_bool(result_mpd_status[MPD_COMMAND_REPEAT])
            if bool_value:
                loop_selected.append(MPD_COMMAND_REPEAT)

        if MPD_COMMAND_SINGLE in result_mpd_status:
            bool_value = fn_check_int_bool(result_mpd_status[MPD_COMMAND_SINGLE])
            if bool_value:
                loop_selected.append(MPD_COMMAND_SINGLE)
        
        if MPD_COMMAND_RANDOM in result_mpd_status:
            bool_value = fn_check_int_bool(result_mpd_status[MPD_COMMAND_RANDOM])
            if bool_value:
                loop_selected.append(MPD_COMMAND_RANDOM)

        if MPD_COMMAND_CONSUME in result_mpd_status:
            bool_value = fn_check_int_bool(result_mpd_status[MPD_COMMAND_CONSUME])
            if bool_value:
                loop_selected.append(MPD_COMMAND_CONSUME)
        

        # Create Widget Every Time
        st.session_state[S_UI_SELECT_COMMAND_LOOP] = uuid.uuid4()
        st.multiselect("Loop Options", loop_base, loop_selected, on_change=fn_select_command_loop, key=st.session_state[S_UI_SELECT_COMMAND_LOOP])

        

    #-------------------------
    # Quee
    if MPD_ITEM_PLAYLIST_QUEE in result_mpd_status:

        quee_command_options = [S_UI_QUEE_ITEM_COMMAND_REMOVE, S_UI_QUEE_ITEM_COMMAND_PLAY, S_UI_QUEE_ITEM_COMMAND_UP, S_UI_QUEE_ITEM_COMMAND_DOWN, S_UI_QUEE_ITEM_COMMAND_CLEAR]
        st.selectbox("Quee Button Type & Clear", quee_command_options, on_change=fn_select_command_quee, key=S_UI_SELECT_COMMAND_QUEE)

        
        if st.session_state[S_CURRENT_SELECT_ITEM_QUEE] == S_UI_QUEE_ITEM_COMMAND_REMOVE:
            emoji_quee = EMOJI_QUEE_DELETE
            command_quee = MPD_COMMAND_QUEE_DELETE
        elif st.session_state[S_CURRENT_SELECT_ITEM_QUEE] == S_UI_QUEE_ITEM_COMMAND_PLAY:
            emoji_quee = EMOJI_PLAY
            command_quee = MPD_COMMAND_QUEE_PLAY
        elif st.session_state[S_CURRENT_SELECT_ITEM_QUEE] == S_UI_QUEE_ITEM_COMMAND_UP:
            emoji_quee = EMOJI_UP
            command_quee = MPD_COMMAND_QUEE_UP
        elif st.session_state[S_CURRENT_SELECT_ITEM_QUEE] == S_UI_QUEE_ITEM_COMMAND_DOWN:
            emoji_quee = EMOJI_DOWN
            command_quee = MPD_COMMAND_QUEE_DOWN
        else:
            emoji_quee = EMOJI_QUEE_DELETE

            
        for item in result_mpd_status[MPD_ITEM_PLAYLIST_QUEE]:
            st.button(f'{emoji_quee} {item[MPD_ITEM_DISPLAY_NAME]}', on_click=fn_mpd_quee, args=[command_quee, item], key=uuid.uuid4())
    else:
        st.warning("Playlist Quee is empty")
                

    #Debug
    if config.IS_DEBUG:
        st.write(result_mpd_status)

    # status_mpd_status, result_mpd_status= get_mpd_status()
    # if status_mpd_status == 200:
    #     st.write(result_mpd_status)

# Container Target
with c_target:
    c_target.divider()    

    # Target
    #target_command_options = [S_UI_TARGET_ITEM_COMMAND_ADD_QUEE, S_UI_TARGET_ITEM_COMMAND_VIEW_TAG, S_UI_TARGET_ITEM_COMMAND_DOWNLOAD]
    target_command_options = [S_UI_TARGET_ITEM_COMMAND_ADD_QUEE, S_UI_TARGET_ITEM_COMMAND_DOWNLOAD]
    st.selectbox("Target Button Type", target_command_options, on_change=fn_select_command_target, key=S_UI_SELECT_COMMAND_TARGET)



    # Display File
    status_code, result = list_folder_and_file_by_path(PATH_LOCATION_TARGET, str(st.session_state[S_CURRENT_TARGET_FOLDER]))

    if status_code == 200:
        
        for fileitem in result:
            button_label = fn_make_button_lable(fileitem)
            button_callback = fn_make_button_callback(fileitem)            
            st.button(button_label, on_click=button_callback, args=[fileitem], key=uuid.uuid4())

# Load .env
from env import Settings
config = Settings()

from const import PATH_LOCATION_SOURCE, PATH_LOCATION_TARGET, PATH_TYPE_FOLDER, PATH_TYPE_FILE
from const import FOLDER_ACTION_RENAME_CURRENT, FOLDER_ACTION_ADD_SUB_FOLDER, FOLDER_ACTION_DELETE_CURRENT, FOLDER_ACTION_UPLOAD_FILE

from session import S_SERVER_LIST, S_CURRENT_SERVER_NAME
from session import S_CURRENT_SOURCE_FOLDER, S_CURRENT_TARGET_FOLDER # rerun() 했을 때 화면 갱신용
from session import S_CURRENT_SOURCE_FOLDER_DISPLAY, S_CURRENT_TARGET_FOLDER_DISPLAY # rerun() 했을 때 화면 갱신용
from session import S_CURRENT_TAG_ITEM # Tag Sidebar > API Server용
from session import S_CURRENT_FILE_ITEM # List > Tag Sidebar용
from session import S_CURRENT_ROOT_TYPE # 상단의 Header Folder용

from session import S_SB_STATE, S_SB_TAG_SELECT, S_SB_FOLDER_SELECT # Modal대신 Sidebar를 사용하긿 함

from session import S_UI_VOLUME, S_UI_LOOP_REPEAT, S_UI_LOOP_SINGLE, S_UI_LOOP_RANDOM, S_UI_LOOP_CONSUME, S_UI_QUEE_CLEAR

from const import MPD_ITEM_STATE, MPD_ITEM_PLAYLIST_QUEE, MPD_ITEM_DISPLAY_NAME, MPD_ITEM_CURRENT_SONG

from const import MPD_COMMAND_PLAY, MPD_COMMAND_STOP, MPD_COMMAND_PAUSE, MPD_COMMAND_RESUME, MPD_COMMAND_STATUS, MPD_COMMAND_PREVIOUS, MPD_COMMAND_NEXT, MPD_COMMAND_VOLUME
from const import MPD_COMMAND_REPEAT, MPD_COMMAND_SINGLE, MPD_COMMAND_RANDOM, MPD_COMMAND_CONSUME
from const import MPD_COMMAND_QUEE_CLEAR, MPD_COMMAND_QUEE_DELETE, MPD_COMMAND_QUEE_ADD

from const import EMOJI_NOT_EXIST, EMOJI_QUEE_CLEAR, EMOJI_QUEE_DELETE, EMOJI_REFRESH
from const import EMOJI_PLAY, EMOJI_STOP, EMOJI_PAUSE, EMOJI_RESUME, EMOJI_PREVIOUS, EMOJI_NEXT
from const import EMOJI_REPEAT, EMOJI_SINGLE, EMOJI_RANDOM, EMOJI_CONSUME

import streamlit as st
from api import list_folder_and_file_by_path, file_read_taginfo_by_path, file_write_taginfo_by_path, folder_action, get_mpd_server_list ,get_mpd_status, set_mpd_command
from datetime import datetime 
import uuid
import os
import utils

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

  



if S_SB_STATE not in st.session_state:
    st.session_state[S_SB_STATE] = "collapsed"
if S_SB_TAG_SELECT not in st.session_state:
    st.session_state[S_SB_TAG_SELECT] = False
if S_SB_FOLDER_SELECT not in st.session_state:
    st.session_state[S_SB_FOLDER_SELECT] = False

if S_CURRENT_SOURCE_FOLDER not in st.session_state:
    st.session_state[S_CURRENT_SOURCE_FOLDER] = ''
    st.session_state[S_CURRENT_SOURCE_FOLDER_DISPLAY] = ''
if S_CURRENT_TARGET_FOLDER not in st.session_state:
    st.session_state[S_CURRENT_TARGET_FOLDER] = ''
    st.session_state[S_CURRENT_TARGET_FOLDER_DISPLAY] = ''

# Page Setup
st.set_page_config(
    page_title="MPD Client for Home",
    page_icon=":musical_note:",
    initial_sidebar_state=st.session_state[S_SB_STATE],
    menu_items={
        'About': """
# MPD Client for Home
Simple is BEST.

---

GitHub: [halfenif/toy_mpdclient_streamlit](https://github.com/halfenif/toy_mpdclient_streamlit)

Blog: [Enif's small talk](https://blog.enif.page/blog/)

---

[MPD](https://www.musicpd.org/) : Music Player Daemon.  
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

def fn_display_page_header(isAddReload: bool):

    # Title
    if config.UI_OPTION_TITLE:
        st.title(config.UI_OPTION_TITLE)
    
    if config.UI_OPTION_DESC:
        st.write(config.UI_OPTION_DESC)
    
    if isAddReload:
        #Reload Button for not submit escape
        button_reload = st.button(":arrows_counterclockwise: Reload")
        if button_reload:
            st.session_state[S_SB_TAG_SELECT] = False
            st.session_state[S_SB_FOLDER_SELECT] = False
            st.session_state[S_SB_STATE] = "collapsed"        
            st.rerun()

def fn_file_select(fileitem):
    fn_mpd_quee(MPD_COMMAND_QUEE_ADD, fileitem)
    
#---------------------------------------------------------------------
def fn_folder_select(fileitem):
    # Body Folder Select
    if fileitem["rootType"] == PATH_LOCATION_SOURCE:
        st.session_state[S_CURRENT_SOURCE_FOLDER] = fileitem["pathEncode"]
        st.session_state[S_CURRENT_SOURCE_FOLDER_DISPLAY] = fileitem["folderCurrent"]
    if fileitem["rootType"] == PATH_LOCATION_TARGET:
        st.session_state[S_CURRENT_TARGET_FOLDER] = fileitem["pathEncode"]
        st.session_state[S_CURRENT_TARGET_FOLDER_DISPLAY] = fileitem["folderCurrent"]

#---------------------------------------------------------------------
def fn_make_button_lable(fileitem):

    buttonEmoji = ""
    if fileitem["pathType"] == PATH_TYPE_FOLDER:
        buttonEmoji = ":file_folder:"
    if fileitem["pathType"] == PATH_TYPE_FILE:
        buttonEmoji = ":musical_note:"
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
    set_mpd_command(mpdItem)

def fn_mpd_volume():
    # Init MPD Item
    mpdItem = MpdItem()
    mpdItem.command = MPD_COMMAND_VOLUME
    mpdItem.command_value_int = int(st.session_state[S_UI_VOLUME])
    fn_mpd_command(mpdItem)


        
def fn_mpd_loop(command:str, key:str):
    # Init MPD Item
    mpdItem = MpdItem()
    mpdItem.command = command

    bool_value = st.session_state[key]
    mpdItem.command_value_int = fn_check_bool_int(bool_value)

    fn_mpd_command(mpdItem)

def fn_mpd_quee(command:str, item:any):
    # Init MPD Item
    mpdItem = MpdItem()
    mpdItem.command = command

    if command == MPD_COMMAND_QUEE_DELETE:
        if not "id" in item:
            st.error(f'{command}: item no attribute playlist quee song "id"')
            st.stop()
        mpdItem.song_id = int(item["id"])
    elif command == MPD_COMMAND_QUEE_ADD:
        mpdItem.song_path_encode = item["pathEncode"]

    fn_mpd_command(mpdItem)

#---------------------------------------------------------------------




# Page Header
fn_display_page_header(False)

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
    select_server_changed = st.selectbox("Server:", select_server_options, select_index)
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

        if MPD_ITEM_CURRENT_SONG in result_mpd_status:
            st.info(f"Playing: {result_mpd_status[MPD_ITEM_CURRENT_SONG]}")

        # Volume
        if MPD_COMMAND_VOLUME in result_mpd_status:
            volume_control = st.empty()
            volume_control.slider("Volume", min_value=0, max_value=100, value=int(result_mpd_status["volume"]), step=5, on_change=fn_mpd_volume, key=S_UI_VOLUME)
        else:
            st.warning(f'{str(st.session_state[S_CURRENT_SERVER_NAME])} not support volume')

        #----------------------------        
        # Play Buttons        
        col_play_btn1, col_play_btn2, col_play_btn3, col_play_btn4, col_play_btn5, col_play_btn6, col_play_btn_right = st.columns([0.15, 0.15, 0.15, 0.15, 0.15, 0.15, 0.1])
        with col_play_btn1:
            mpdItemCopy = copy.copy(mpdItem)
            mpdItemCopy.command = MPD_COMMAND_PLAY
            st.button(EMOJI_PLAY, on_click=fn_mpd_command, args=[mpdItemCopy], help="Play From First Song")

        with col_play_btn2:
            mpdItemCopy = copy.copy(mpdItem)
            mpdItemCopy.command = MPD_COMMAND_STOP
            st.button(EMOJI_STOP, on_click=fn_mpd_command, args=[mpdItemCopy])
        
        # btn3 is empty
            
        with col_play_btn4:
            mpdItemCopy = copy.copy(mpdItem)
            mpdItemCopy.command = MPD_COMMAND_PREVIOUS
            st.button(EMOJI_PREVIOUS, on_click=fn_mpd_command, args=[mpdItemCopy])

        with col_play_btn5:
            mpdItemCopy = copy.copy(mpdItem)
            if result_mpd_status[MPD_ITEM_STATE] == MPD_COMMAND_PAUSE:            
                mpdItemCopy.command = MPD_COMMAND_RESUME
                st.button(EMOJI_RESUME, on_click=fn_mpd_command, args=[mpdItemCopy])
            elif result_mpd_status[MPD_ITEM_STATE] == MPD_COMMAND_PLAY:
                mpdItemCopy.command = MPD_COMMAND_PAUSE
                st.button(EMOJI_PAUSE, on_click=fn_mpd_command, args=[mpdItemCopy])
            # else is play == empty
                
        with col_play_btn6:
            mpdItemCopy = copy.copy(mpdItem)
            mpdItemCopy.command = MPD_COMMAND_NEXT
            st.button(EMOJI_NEXT, on_click=fn_mpd_command, args=[mpdItemCopy])

        #----------------------------        
        # Loop Buttons        
        col_loop_1, col_loop_2, col_loop_3, col_loop_4 = st.columns([0.25, 0.25, 0.25, 0.25])
        if MPD_COMMAND_REPEAT in result_mpd_status:
            with col_loop_1:
                bool_value = fn_check_int_bool(result_mpd_status[MPD_COMMAND_REPEAT])
                st.checkbox(f"{EMOJI_REPEAT}", value=bool_value, help="Repeat", on_change=fn_mpd_loop, args=[MPD_COMMAND_REPEAT, S_UI_LOOP_REPEAT], key=S_UI_LOOP_REPEAT)
        else:
            with col_loop_1:
                st.write(f"{EMOJI_NOT_EXIST}{EMOJI_REPEAT}")

        if MPD_COMMAND_SINGLE in result_mpd_status:
            with col_loop_2:
                bool_value = fn_check_int_bool(result_mpd_status[MPD_COMMAND_SINGLE])
                st.checkbox(f"{EMOJI_SINGLE}", value=bool_value, help="Single==Play once", on_change=fn_mpd_loop, args=[MPD_COMMAND_SINGLE, S_UI_LOOP_SINGLE], key=S_UI_LOOP_SINGLE)
        else:
            with col_loop_2:
                st.write(f"{EMOJI_NOT_EXIST}{EMOJI_SINGLE}")
        
        if MPD_COMMAND_RANDOM in result_mpd_status:
            with col_loop_3:
                bool_value = fn_check_int_bool(result_mpd_status[MPD_COMMAND_RANDOM])
                st.checkbox(f"{EMOJI_RANDOM}", value=bool_value, help="Random", on_change=fn_mpd_loop, args=[MPD_COMMAND_RANDOM, S_UI_LOOP_RANDOM], key=S_UI_LOOP_RANDOM)
        else:
            with col_loop_3:
                st.write(f"{EMOJI_NOT_EXIST}{EMOJI_RANDOM}")

        if MPD_COMMAND_CONSUME in result_mpd_status:
            with col_loop_4:
                bool_value = fn_check_int_bool(result_mpd_status[MPD_COMMAND_CONSUME])
                st.checkbox(f"{EMOJI_CONSUME}", value=bool_value, help="Consume==Remove song from playlist after play", on_change=fn_mpd_loop, args=[MPD_COMMAND_CONSUME, S_UI_LOOP_CONSUME], key=S_UI_LOOP_CONSUME)
        else:
            with col_loop_4:
                st.write(f"{EMOJI_NOT_EXIST}{EMOJI_CONSUME}")
        
        if MPD_ITEM_PLAYLIST_QUEE in result_mpd_status:
            col_quee_1, col_quee_2= st.columns([0.6, 0.4])
            with col_quee_2:
                st.button(f"{EMOJI_QUEE_CLEAR} Clear Quee", on_click=fn_mpd_quee, args=[MPD_COMMAND_QUEE_CLEAR, S_UI_QUEE_CLEAR], key=S_UI_QUEE_CLEAR)
            
            for item in result_mpd_status[MPD_ITEM_PLAYLIST_QUEE]:
                st.button(f'{EMOJI_QUEE_DELETE} {item[MPD_ITEM_DISPLAY_NAME]}', on_click=fn_mpd_quee, args=[MPD_COMMAND_QUEE_DELETE, item], key=uuid.uuid4())
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

    status_code, result = list_folder_and_file_by_path(PATH_LOCATION_TARGET, str(st.session_state[S_CURRENT_TARGET_FOLDER]))

    if status_code == 200:
        
        for fileitem in result:
            button_label = fn_make_button_lable(fileitem)
            button_callback = fn_make_button_callback(fileitem)            
            st.button(button_label, on_click=button_callback, args=[fileitem], key=uuid.uuid4())

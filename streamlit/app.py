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
from session import S_UI_VOLUME_CONTROL, S_UI_VOLUME_VALUE
from const import MPD_ITEM_STATE
from const import MPD_COMMAND_PLAY, MPD_COMMAND_STOP, MPD_COMMAND_PAUSE, MPD_COMMAND_RESUME, MPD_COMMAND_STATUS, MPD_COMMAND_PREVIOUS, MPD_COMMAND_NEXT
from const import EMOJI_PLAY, EMOJI_STOP, EMOJI_PAUSE, EMOJI_RESUME, EMOJI_REPEAT, EMOJI_REPEAT_ONE, EMOJI_PREVIOUS, EMOJI_NEXT

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
    st.session_state[S_SB_TAG_SELECT]=True
    st.session_state[S_CURRENT_FILE_ITEM] = fileitem
    st.session_state[S_SB_STATE] = "expanded"

if st.session_state[S_SB_TAG_SELECT]:
    # Page Header
    fn_display_page_header(True)

    fileitem = st.session_state[S_CURRENT_FILE_ITEM]

    #Get Tag
    status_code, result = file_read_taginfo_by_path(fileitem)
    
    if status_code == 200:
        with st.sidebar:
            with st.form("fileInfoForm"):

                # Set Serssion
                st.session_state[S_CURRENT_TAG_ITEM] = result

                # Set Form
                st.subheader(result["fileName"])
                st.text_input("File Base Name", result["fileBaseName"], key="tagItem_fileBaseName", max_chars=200)
                st.text_input("File Ext Name", result["fileExtName"], key="tagItem_fileExtName", max_chars=10, disabled=True)
                st.text_input("Title", result["tagTitle"], key="tagItem_tagTitle", max_chars=200)
                st.text_input("Album", result["tagAlbum"], key="tagItem_tagAlbum", max_chars=200)
                st.text_input("Artist", result["tagArtist"], key="tagItem_tagArtist", max_chars=200)
                st.text_input("Albumartist", result["tagAlbumartist"], key="tagItem_tagAlbumartist", max_chars=200)

                year_end = datetime.now().year
                if result["tagDate"].isnumeric():
                    st.number_input(f"Year({config.TAG_DATE_BEGIN}~{year_end})", key="tagItem_tagDate", min_value=config.TAG_DATE_BEGIN, max_value=year_end, value=int(result["tagDate"]), step=1)
                else:
                    st.number_input(f"Year({config.TAG_DATE_BEGIN}~{year_end})", key="tagItem_tagDate", min_value=config.TAG_DATE_BEGIN, max_value=year_end, value=config.TAG_DATE_BEGIN, step=1)

                if result["tagTracknumber"].isnumeric():
                    st.number_input("Tracknumber(1~20)", key="tagItem_tagTracknumber", min_value=1, max_value=config.TAG_TARCK_END, value=int(result["tagTracknumber"]), step=1)
                else:
                    st.number_input("Tracknumber(1~20)", key="tagItem_tagTracknumber", min_value=1, max_value=config.TAG_TARCK_END, value=1, step=1)

                # Options-Whip
                st.checkbox("Whip Tag :wastebasket: + :writing_hand:", key="tagItem_doWhip", value=config.TAG_OPTION_WHIP)
                
                # Options-Move To File
                if result["rootType"] == PATH_LOCATION_SOURCE:
                    st.checkbox(f"Move to :file_folder: :blue[Target > {st.session_state[S_CURRENT_TARGET_FOLDER_DISPLAY]}]", key="tagItem_doMove", value=config.TAG_OPTION_MOVE_SOURCE_TO_TARGET)
                elif result["rootType"] == PATH_LOCATION_TARGET:
                    st.checkbox(f"Move to :file_folder: :blue[Source > {st.session_state[S_CURRENT_SOURCE_FOLDER_DISPLAY]}]", key="tagItem_doMove", value=config.TAG_OPTION_MOVE_TARGET_TO_SOURCE)

                # Options-MPD
                st.checkbox("MPD Update :satellite_antenna: :loud_sound:", key="tagItem_doMpdUpdate", value=config.TAG_OPTION_MPD_UPDATE)

                # Options-MPD
                st.checkbox("DELETE File :boom:", key="tagItem_doDeleteFile", value=False)


                # Set Button
                btn_col1, btn_col2 = st.columns([1,1])

                with btn_col2:
                    form_canceled = st.form_submit_button(label='Cancel')
                    if form_canceled:
                        st.session_state[S_SB_TAG_SELECT] = False
                        st.session_state[S_SB_STATE] = "collapsed"
                        st.rerun()                

                with btn_col1:
                    form_submited = st.form_submit_button(label='Submit')
                    if form_submited:

                        tagItem = st.session_state[S_CURRENT_TAG_ITEM]

                        tagItem['fileBaseName'] = st.session_state['tagItem_fileBaseName']
                        tagItem['fileExtName'] = st.session_state['tagItem_fileExtName']
                        tagItem['tagTitle'] = st.session_state['tagItem_tagTitle']
                        tagItem['tagAlbum'] = st.session_state['tagItem_tagAlbum']
                        tagItem['tagArtist'] = st.session_state['tagItem_tagArtist']
                        tagItem['tagAlbumartist'] = st.session_state['tagItem_tagAlbumartist']
                        tagItem['tagDate'] = st.session_state['tagItem_tagDate']
                        tagItem['tagTracknumber'] = st.session_state['tagItem_tagTracknumber']

                        tagItem['doWhip'] = st.session_state['tagItem_doWhip']
                        tagItem['doMove'] = st.session_state['tagItem_doMove']
                        tagItem['doMpdUpdate'] = st.session_state['tagItem_doMpdUpdate']
                        tagItem['doDeleteFile'] = st.session_state['tagItem_doDeleteFile']

                        if tagItem['rootType'] == PATH_LOCATION_SOURCE:
                            tagItem['pathToMoveEncode'] = st.session_state[S_CURRENT_TARGET_FOLDER]
                        elif tagItem['rootType'] == PATH_LOCATION_TARGET:
                            tagItem['pathToMoveEncode'] = st.session_state[S_CURRENT_SOURCE_FOLDER]

                        # Call Server
                        tag_action_status_code, tag_action_result = file_write_taginfo_by_path(tagItem)
                        if not tag_action_status_code == 200:
                            st.stop()                        

                        st.session_state[S_SB_TAG_SELECT] = False
                        st.session_state[S_SB_STATE] = "collapsed"
                        st.rerun()




        # End Modal Logic. Stop
        st.stop()
        

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

def fn_make_root_lable(rootType: str, folderPath: str):
    return f":card_file_box: {rootType} > {folderPath}"

#---------------------------------------------------------------------
def fn_make_button_callback(fileitem):
    if fileitem["pathType"] == PATH_TYPE_FILE:
        return fn_file_select
    else:
        return fn_folder_select
    
#---------------------------------------------------------------------    
def fn_header_folder_select(rootType):
    # Header Folder Select
    st.session_state[S_SB_FOLDER_SELECT]=True
    st.session_state[S_CURRENT_ROOT_TYPE] = rootType
    st.session_state[S_SB_STATE] = "expanded"    

if st.session_state[S_SB_FOLDER_SELECT]:
    # Page Header
    fn_display_page_header(True)

    if st.session_state[S_CURRENT_ROOT_TYPE] == PATH_LOCATION_SOURCE:
        folderName = st.session_state[S_CURRENT_SOURCE_FOLDER_DISPLAY]
    elif st.session_state[S_CURRENT_ROOT_TYPE] == PATH_LOCATION_TARGET:
        folderName = st.session_state[S_CURRENT_TARGET_FOLDER_DISPLAY]

    with st.sidebar:
        with st.container(border=True):
            # st.subheader(f"{st.session_state[S_CURRENT_ROOT_TYPE]} > " + folderName)
            st.subheader(fn_make_root_lable(str(st.session_state[S_CURRENT_ROOT_TYPE]), folderName))

            r_item_rename: str = "Rename Current Folder"
            r_item_addSub: str = "Add Sub Folder"
            r_item_delete: str = "Delete Current Folder :boom:"
            r_item_upload: str = "Upload File to Current Folder :mag:"

            if not folderName:
                folderBaseName = ""
                genre = st.radio(
                    "Select Action",
                    [r_item_addSub, r_item_upload])
            else:
                folderBaseName = os.path.basename(folderName)
                genre = st.radio(
                    "Select Action",
                    [r_item_rename, r_item_addSub, r_item_delete, r_item_upload])

            # Display Control
            if genre == r_item_rename:
                folder_item_rename = st.text_input("Folder Name", folderBaseName, key="folderItem_folderBaseName", max_chars=200, disabled=False)
            elif genre == r_item_addSub:
                folder_item_add_sub = st.text_input("Sub Folder Name", "", key="folderItem_subFolderBaseName", max_chars=200)
            elif genre == r_item_upload:
                folder_item_upload = st.file_uploader("Select File", type=['mp3','flac', 'ogg'], label_visibility="hidden")

            # Set Button
            btn_col1, btn_col2 = st.columns([1,1])

            # Cancel 버튼을 먼저 그린다.
            with btn_col2:
                form_canceled = st.button(label='Cancel')
                if form_canceled:
                    st.session_state[S_SB_FOLDER_SELECT] = False
                    st.session_state[S_SB_STATE] = "collapsed"
                    st.rerun()            

            with btn_col1:
                form_submited = st.button(label='Submit')
                if form_submited:

                    # Param Class
                    folderItem = {}
                    folderItem["rootType"] = st.session_state[S_CURRENT_ROOT_TYPE]

                    # 
                    if st.session_state[S_CURRENT_ROOT_TYPE] == PATH_LOCATION_SOURCE:
                        folderItem["pathEncode"] = st.session_state[S_CURRENT_SOURCE_FOLDER]
                    elif st.session_state[S_CURRENT_ROOT_TYPE] == PATH_LOCATION_TARGET:
                        folderItem["pathEncode"] = st.session_state[S_CURRENT_TARGET_FOLDER]

                    # Request Control
                    decode_new_folder = ""  

                    if genre == r_item_rename or genre == r_item_addSub or genre == r_item_delete:
                        if genre == r_item_rename:
                            if not folder_item_rename:
                                st.error("Folder명을 입력하십시오.")
                                st.stop()

                            folderItem["folderCommand"] = FOLDER_ACTION_RENAME_CURRENT
                            decode_new_folder = folder_item_rename
                        elif genre == r_item_addSub:
                            if not folder_item_add_sub:
                                st.error("Folder명을 입력하십시오.")
                                st.stop()

                            folderItem["folderCommand"] = FOLDER_ACTION_ADD_SUB_FOLDER
                            decode_new_folder = folder_item_add_sub
                        elif genre == r_item_delete:
                            folderItem["folderCommand"] = FOLDER_ACTION_DELETE_CURRENT
                            decode_new_folder = ""

                        # New Folder Encode
                        encode_status, encode_new_folder = utils.getPathEncode(decode_new_folder)
                        if encode_status:
                            st.stop()
                        folderItem["newFolderNameEncode"] = encode_new_folder

                        # Call Server
                        folder_action_status_code, folder_action_result = folder_action(folderItem)
                        if not folder_action_status_code == 200:
                            st.stop()

                        # Success
                        if st.session_state[S_CURRENT_ROOT_TYPE] == PATH_LOCATION_SOURCE:
                            st.session_state[S_CURRENT_SOURCE_FOLDER] = folder_action_result["pathEncode"]
                            st.session_state[S_CURRENT_SOURCE_FOLDER_DISPLAY] = folder_action_result["newFolderNameDisplay"]
                        elif st.session_state[S_CURRENT_ROOT_TYPE] == PATH_LOCATION_TARGET:
                            st.session_state[S_CURRENT_TARGET_FOLDER] = folder_action_result["pathEncode"]
                            st.session_state[S_CURRENT_TARGET_FOLDER_DISPLAY] = folder_action_result["newFolderNameDisplay"]
                        

                    elif genre == r_item_upload:

                        if folder_item_upload is None:
                            st.error("File을 선택하십시오.")
                            st.stop()

                        folderItem["folderCommand"] = FOLDER_ACTION_UPLOAD_FILE
                        fileItem = {}
                        fileItem["rootType"] = st.session_state[S_CURRENT_ROOT_TYPE]
                        fileItem["pathEncode"] = st.session_state[S_CURRENT_SOURCE_FOLDER]
                        encode_status, encode_upload_file = utils.getPathEncode(folder_item_upload.name)
                        fileItem["fileName"] = encode_upload_file

                        upload_action_status_code, upload_action_result = upload_file(folder_item_upload, fileItem)
                        if not upload_action_status_code == 200:
                            st.stop()




                    # Sidebar Control
                    st.session_state[S_SB_FOLDER_SELECT] = False
                    st.session_state[S_SB_STATE] = "collapsed"                        
                    st.rerun()

        # Open Side인경우 본화면을 갱신하지 않기 위한 조치
        st.stop()


def fn_mpd_command(mpdItem:MpdItem):
    status_mpd_command, result_mpd_command = set_mpd_command(mpdItem)

    if not status_mpd_command == 200:
        st.stop()

def fn_mpd_volume():
    # st.session_state[S_UI_VOLUME]

    st.write(st.session_state[S_UI_VOLUME_VALUE])
    # st.write(st.session_state[S_UI_VOLUME_CONTROL])
    # status_mpd_command, result_mpd_command = set_mpd_command(mpdItem)

    # if not status_mpd_command == 200:
    #     st.stop()

    st.write("call")
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

        st.write(result_mpd_status)

        if "volume" in result_mpd_status:
            volume_control = st.empty()
            st.write(f"Volume exist:{int(result_mpd_status['volume'])}")
            st.session_state[S_UI_VOLUME_VALUE] = volume_control.slider("Volume", min_value=0, max_value=100, value=int(result_mpd_status["volume"]), step=5, on_change=fn_mpd_volume, key=uuid.uuid4())
        else:
            volume_control = st.empty()
            st.write("Volume not exist")
            st.session_state[S_UI_VOLUME_VALUE] = volume_control.slider("Volume", min_value=0, max_value=100, value=100, step=5, on_change=fn_mpd_volume, key=uuid.uuid4())

        


        
        
        
        col_play_btn1, col_play_btn2, col_play_btn3, col_play_btn4, col_play_btn5, col_play_btn6, col_play_btn_right = st.columns([0.15, 0.15, 0.15, 0.15, 0.15, 0.15, 0.1])
           

        with col_play_btn1:
            mpdItemCopy = copy.copy(mpdItem)
            mpdItemCopy.command = MPD_COMMAND_PLAY
            st.button(EMOJI_PLAY, on_click=fn_mpd_command, args=[mpdItemCopy])

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

    # status_mpd_status, result_mpd_status= get_mpd_status()
    # if status_mpd_status == 200:
    #     st.write(result_mpd_status)

# Container Target
# with c_target:
#     c_target.divider()    
#     st.button(fn_make_root_lable(PATH_LOCATION_TARGET, str(st.session_state[S_CURRENT_TARGET_FOLDER_DISPLAY])),
#               on_click=fn_header_folder_select,
#               args=[PATH_LOCATION_TARGET],
#               key=uuid.uuid4())
    

#     status_code, result = list_folder_and_file_by_path(PATH_LOCATION_TARGET, str(st.session_state[S_CURRENT_TARGET_FOLDER]))

#     # debug
#     # st.write(result)

#     if status_code == 200:
        
#         for fileitem in result:
#             button_label = fn_make_button_lable(fileitem)
#             button_callback = fn_make_button_callback(fileitem)            
#             st.button(button_label, on_click=button_callback, args=[fileitem], key=uuid.uuid4())

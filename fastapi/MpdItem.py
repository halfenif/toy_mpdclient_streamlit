# This Class share with FastAPI, Streamlit
from pydantic import BaseModel, Field

class MpdItem(BaseModel):
    server_name:        str = Field("")
    command:            str = Field("")
    command_value_int:  int = Field(0)
    song_id:            int = Field(0)
    song_path_encode:   str = Field("")
    loop_repeat:        int = Field(0)
    loop_single:        int = Field(0)
    loop_random:        int = Field(0)
    loop_consume:       int = Field(0)
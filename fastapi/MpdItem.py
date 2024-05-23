# This Class share with FastAPI, Streamlit
from pydantic import BaseModel, Field

class MpdItem(BaseModel):
    server_name:  str = Field("")
    command:      str = Field("")
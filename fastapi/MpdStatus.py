from typing import List
from pydantic import BaseModel, Field
from MpdServer import MpdServer

class MpdStatus(BaseModel):
    current_server_name:  str = Field("", alias='currentServerName')

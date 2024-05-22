from pydantic import BaseModel, Field

class MpdServer(BaseModel):
    name:                     str = Field("", alias='name')
    display_name:             str = Field("", alias='displayName')
    ip:                       str = Field("", alias='ip')
    port:                     int = Field("", alias="port")

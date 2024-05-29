from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    ENV_TYPE: str
    URL_BACKEND: str
    IS_DEBUG: bool
    UI_OPTION_TITLE: str
    UI_OPTION_DESC: str
    UI_OPTION_LINK_TITLE: str
    UI_OPTION_LINK_URL: str    
    UI_OPTION_SIDEBAR_WIDTH: int


    model_config = SettingsConfigDict(
        env_file=('.env.sample', '.env')
    )


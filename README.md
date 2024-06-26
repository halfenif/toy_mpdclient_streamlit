# MPD Client for Home

![Demo](doc/Screen01.png)

## Demo
[https://mpdclient.enif.page](https://mpdclient.enif.page)

MPD를 2개 설정 했습니다만.
1. server다 보니 mixer가 없어서 volume은 조절이 안됩니다.
2. flac 파일은 재생이 안됩니다.

## Feature
- Simple is BEST concept
- Multi MPD support

## Installation
**Requirements**
- Docker, Docker-Compose or Podman

### Clone
```bash
git clone https://github.com/halfenif/toy_mpdclient_streamlit.git
```

## Change Config
```bash
cp ./.env.sample ./.env
cp ./fastapi/.env.sample ./fastapi/.env
cp ./streamlit/.env.sample ./streamlit/.env
```

### Edit .env

**./.env**  
- FOLDER_TARGET="" # MPD music folder

1. Don't use symbolic link
2. Docker run user is root
3. Podman run user is login user
4. Be carefull folder and file permission


**fastapi/.env**
- ENV_TYPE = ".env.sample" > ".env" Display Information
- IS_DEBUG = bool
- MPD_SERVER_LIST = str(json format). Option. 
- UI_OPTION_SHORT_FILE_NAME = bool. Display button label short or not
- UI_OPTION_SHORT_FILE_LENGTH = int. Display button label char count

**streamlit/.env**
- ENV_TYPE = ".env.sample" > ".env" Display Information
- URL_BACKEND = fastAPI container URL
- UI_OPTION_TITLE = str, st.title(), if "" is None
- UI_OPTION_DESC = str, st.write(), if "" is None
- UI_OPTION_SIDEBAR_WIDTH = int, st.sidebar width


### Docker-Compose
```bash
docker-compose build
docker-compose up
```

### Podman
```bash
./rebuild_podman.sh
```


podman container stop mpdclient_streamlit
podman container stop mpdclient_fastapi

podman container rm mpdclient_streamlit
podman container rm mpdclient_fastapi

podman-compose build
podman-compose up --detach

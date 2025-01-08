# Setup Container 
install docker 
copy dockerfile and dockercompose
start dockercompose

# install caddy

sudo apt update
sudo apt install caddy

# setup caddy
sudo nano /etc/caddy/Caddyfile

paste:
domainname.de {
    reverse_proxy 127.0.0.1:port
}

# start caddy
sudo pkill caddy
sudo systemctl restart caddy
sudo systemctl status caddy


# make service file to start docker container
sudo systemctl enable docker
sudo nano /etc/systemd/system/docker-compose-streamlit.service

past:
[Unit]
Description=Docker Compose Streamlit App
Requires=docker.service
After=docker.service

[Service]
WorkingDirectory=/path/to/your/docker-compose-project
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
Restart=always

[Install]
WantedBy=multi-user.target

run:
sudo systemctl daemon-reload
sudo systemctl enable docker-compose-streamlit.service
sudo systemctl start docker-compose-streamlit.service

# verify
sudo reboot
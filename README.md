# GPTWOL a simple Wake On Lan gui

---
[![Docker Pulls](https://img.shields.io/docker/pulls/misterbabou/gptwol.svg?logo=docker)](https://hub.docker.com/r/misterbabou/gptwol)
[![GitHub Release](https://img.shields.io/github/release/Misterbabou/gptwol.svg?logo=github&logoColor=959DA5)](https://github.com/Misterbabou/gptwol/releases/latest)
[![GitHub last commit](https://img.shields.io/github/last-commit/Misterbabou/gptwol?logo=github&logoColor=959DA5)](https://github.com/Misterbabou/gptwol/commits/main)
[![MIT Licensed](https://img.shields.io/github/license/Misterbabou/gptwol.svg?logo=github&logoColor=959DA5)](https://github.com/Misterbabou/gptwol/blob/main/LICENSE.md)
---

GPTWOL is a simple and lightweight Wake on Lan gui made with python to wake up your computers on your LAN.
It was made mostly by chatGPT.

## Screenshot 

![gptwol-gui.png](/assets/gptwol-gui.png)

## Features 

- Docker Image to deploy
- Send Wake On Lan packets
- Add or Delete Computer
- Computers status check with ping request
- Very low power usage (20 mb RAM)
- Check if IP and MAC provided are valid
- cron job to wake up device
- Check if Cron provided is valid
- Search on cumputer Name, MAC or IP

## Special configuration you can change

- Ping Refresh to check Status availibility 
- Disable Delete or Add Computers
- Change the port of the Web UI

## Docker Conf

It's recommanded to use docker compose to run this application


Create `docker-compose.yml` file:
```
version: "3"
services:
  gptwol:
    container_name: gptwol
    image: misterbabou/gptwol:latest
    network_mode: host
    restart: unless-stopped
    environment:
      - PORT=8080 #Free Port on Your host default is 5000
      - TZ=Europe/Paris #Set your timezone for Cron default is UTC
      #- DISABLE_ADD_DEL=1 #Uncomment this line to disable Add or delete Computers default is to allow
      #- DISABLE_REFRESH=1 #Uncomment this line to prevent your browser to refresh Computer status default is to allow
      #- REFRESH_PING=15 # Uncomment this line to change ping status check, can be 15 or 60 (seconds) default value is 30 seconds
    volumes:
      - ./computers.txt:/app/computers.txt
      - ./appdata/cron:/etc/cron.d
```

Create the file for storing computers (the mounted file on docker-compose)
```
touch computers.txt
```

Run the application
```
docker-compose up -d
```

## :warning: Notes

- The app container needs to run in host network mode to send the wakeonlan command on your local network.
- Make sure that the PORT you are using is free on your host computer
- Make sure that BIOS settings and remote OS is configure to allow Wake On Lan
- Don't expose gptwol directly on internet without proper authentication

## Roadmap 

:heavy_check_mark: Add ARM version (Added in 1.0.1)

:heavy_check_mark: Add feature to plan automatic Wake on Lan (Cron) (Added in 1.0.3)

:heavy_check_mark: Add Search feature (Added in 1.0.4)

:heavy_check_mark: Remove Cron on Computer deletion (Added in 1.0.4)

- Improve load page performance. For now it takes more than 1 second to test if a computer is awake with ping. If computers are down the load of the page takes 1 second or more.

- Add filter buttons to filter computer by Name or IP
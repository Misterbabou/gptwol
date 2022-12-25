# GPTWOL a simple Wake On Lan gui

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
      #- DISABLE_ADD_DEL=1 #Uncomment this line to disable Add or delete Computers default is to allow
      #- DISABLE_REFRESH=1 #Uncomment this line to prevent your browser to refresh Computer status default is to allow
      #- REFRESH_PING=15 # Uncomment this line to change ping status check, can be 15 or 60 (seconds) default value is 30 seconds
    volumes:
      - ./computers.txt:/app/computers.txt
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
- Make sure that BIOS settings and OS is configure to allow Wake On Lan

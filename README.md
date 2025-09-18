<div align="center" width="100%">
    <img src="app/templates/images/gptwol.png" width="150" />
</div>

# GPTWOL a simple Wake/Sleep On Lan docker GUI

---
[![Docker Pulls](https://img.shields.io/docker/pulls/misterbabou/gptwol.svg?logo=docker)](https://hub.docker.com/r/misterbabou/gptwol)
[![GitHub Release](https://img.shields.io/github/release/Misterbabou/gptwol.svg?logo=github&logoColor=959DA5)](https://github.com/Misterbabou/gptwol/releases/latest)
[![GitHub last commit](https://img.shields.io/github/last-commit/Misterbabou/gptwol?logo=github&logoColor=959DA5)](https://github.com/Misterbabou/gptwol/commits/main)
[![MIT Licensed](https://img.shields.io/github/license/Misterbabou/gptwol.svg?logo=github&logoColor=959DA5)](https://github.com/Misterbabou/gptwol/blob/main/LICENSE.md)
---

GPTWOL is a simple and lightweight Wake/Sleep on Lan gui made with python to wake up and shutdown your computers on your LAN.

## Screenshot 

| Light Web                         | Dark Web                           |
| --------------------------------- | ---------------------------------- |
| ![](/assets/gptwol-web-light.png) | ![](/assets/gptwol-web-dark.png)   |

| Light Mobile                      | Dark Mobile                        |
| --------------------------------- | ---------------------------------- |
| ![](/assets/gptwol-mob-light.png) | ![](/assets/gptwol-mob-dark.png)   |

## Features 

- Docker Image to deploy
- Send Wake On Lan packets to wake up computers
- Send Sleep On Lan packets to shutdown computers
- Add or Delete Computer
- Computers status check with ping, arp or tcp request (timeout settings available)
- ARP-SCAN to add computers
- Very low power usage (20 mb RAM)
- Check if IP and MAC provided are valid
- cron job to wake up device
- Check if Cron provided is valid
- Search on computer Name, MAC or IP
- Dark mode
- Authentication (disable by default)

## Special configuration you can change

- Ping Refresh to check Status availability 
- Disable Delete or Add Computers
- Change the port of the Web UI
- Enable authentication (Local auth with only one user or OIDC)

![](/assets/authentication.png)

## Docker Configuration
> [!NOTE]
>
>It's recommended to use docker compose to run this application. [Install documentation](https://docs.docker.com/compose/install/)

> [!CAUTION]
>
>- The app container needs to run in host network mode to send the wakeonlan command on your local network.
>- Make sure that the PORT you are using is free on your host computer
>- Make sure that BIOS settings and remote OS is configure to allow Wake On Lan
>- Don't expose gptwol directly on internet without proper authentication

### With docker compose

Create `docker-compose.yml` file:
```
services:
  gptwol:
    container_name: gptwol
    image: misterbabou/gptwol:latest
    network_mode: host
    restart: unless-stopped
    environment:
      - TZ=Europe/Paris #Set your timezone for Cron; default is UTC
      #- PORT=5000 #Free Port on Your host; default is 5000
      #- IP=0.0.0.0 #App listening IPV4 or IPV6 (ex [::]) address; default is 0.0.0.0
      #- LOG_LEVEL=INFO #Can be DEBUG, INFO, WARN or ERROR
      #- ENABLE_LOGIN=false # Enable or disable local login; You would be able to access with USERNAME and PASSWORD; default is false
      #- USERNAME=admin # Set a username; default is admin
      #- PASSWORD=admin # Set a password; default is admin
      #- OIDC_ENABLED=true # Enable OIDC LOGIN; default is false
      #- OIDC_ISSUER=https://auth.exemple.com #  Base URL of the OIDC server - Should not include the `/.well-known/openid-configuration` part and no trailing `/`; default is not set
      #- OIDC_CLIENT_ID=oidcclientid # Your OIDC client ID; default is not set
      #- OIDC_CLIENT_SECRET=oidcclientsecret # Your OIDC Client Secret; default is not set
      #- OIDC_REDIRECT_URI=http(s)://urlofyourgptwol(:port) # Base URL of your GPTWOL instance; default is not set 
      #- SCRIPT_NAME=/my-app # Uncomment this line to run the app under a prefix; default is not set
      #- ENABLE_ADD_DEL=true # Enable or disable ADD computer and Delete computer buttons; default is true
      #- ENABLE_REFRESH=true # Enable or disable automatic status refresh; default is true
      #- REFRESH_INTERVAL=30 # Uncomment to change time between each status check for icmp, arp or tcp, can (in s); default value is 30 seconds
      #- PING_TIMEOUT=300 #Uncomment to change the time to wait for a ping answer in (in ms); default value is 300 milliseconds
      #- ARP_INTERFACE=eth0 #Uncomment this line to set an arp interface manually for scan and test; default is not set
      #- ARP_TIMEOUT=300 #Uncomment to change the time to wait for a arp answer (in ms); default value is 300 milliseconds
      #- TCP_TIMEOUT=1 #Uncomment to change the time to wait for a tcp check (in s);  default value 1 second
      #- ENABLE_L2_WOL_PACKET=false # Enable L2 WOL packet instead of L4, default is false
      #- L2_INTERFACE=eth0 # Set the default interface for L2 WOL (set this only if you set ENABLE_L2_WOL_PACKET to true), default is eth0
    volumes:
      - ./appdata/db:/app/db
      - ./appdata/cron:/etc/cron.d
```

Run the application
```
docker compose up -d
```

### With docker

Run the application
```
docker run -d \
  --name=gptwol \
  --network="host" \
  --restart unless-stopped \
  -e PORT=5000 \
  -e TZ=Europe/Paris \
  -v ./appdata/db:/app/db \
  -v ./appdata/cron:/etc/cron.d \
  misterbabou/gptwol:latest
```

## Configure Sleep on Lan

- Check the [Sleep on Lan Github](https://github.com/SR-G/sleep-on-lan) repo to download and configure
- GPTWOL send a reverse MAC wakeonlan packet on port 9 to shutdown your computer (you don't need to configure API)

Here is an example of a wol.json to shutdown a Debian based computer
```
{
    "Listeners": [
        "UDP:9"
    ],
    "LogLevel": "INFO",
    "Commands": [
        {
            "Operation": "shutdown",
            "Command": "poweroff",
            "Default": true
        }
    ]
}
```

## Roadmap 

:heavy_check_mark: Add ARM version (Added in 1.0.1)

:heavy_check_mark: Add feature to plan automatic Wake on Lan (Cron) (Added in 1.0.3)

:heavy_check_mark: Add Search feature (Added in 1.0.4)

:heavy_check_mark: Remove Cron on Computer deletion (Added in 1.0.4)

:heavy_check_mark: Improve load page performance due to ping timeout. (added in 1.0.5)

:heavy_check_mark: Add a TCP port option to check availability without using ICMP (added in 2.0.1)

:heavy_check_mark: Run app on subpath (added in 2.1.0)

:heavy_check_mark: Make app responsive for smaller screen (added in 2.1.0)

:heavy_check_mark: Add Dark Mode Switch (added in 2.1.3)

:heavy_check_mark: move computers.txt in an other directory not to mount a file but a directory to the docker container (added in 4.0.0)

:heavy_check_mark: Shutdown computers with Sleep on LAN (added in 4.1.0)

:heavy_check_mark: Add optional simple authentication (added in 4.2.0)

:heavy_check_mark: Add ARP SCAN to add you computer of for availability check (added in 5.0.0)

:heavy_check_mark: Add Sort button to sort computer by Name, IP or MAC (added in 5.2.0)

:heavy_check_mark: Migrate computers to a SQLite database (added in 7.0.0)

## Questions

<details>
<summary>Will OIDC be implemented?</summary>
<br>

**OIDC Authentication** will not be implemented but you can add it for instance by using:
- an oidc proxy [oauth2-proxy](https://github.com/oauth2-proxy/oauth2-proxy)
- a proxy provider configured on reverse proxy with [authelia](https://www.authelia.com/) or [authentik](https://goauthentik.io/)

</details>
<details>
<summary>Is there a GUI to configure automatic wakeup and shutdown?</summary>
<br>

Automatic shutdown and wakeup are made in the GUI using cron syntax. As I want to keep the application simple, I will not implement a GUI with a calendar, month an days.
You can check this [link](https://crontab.guru/) to help you build your cron.

</details>

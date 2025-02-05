# Migration page

## Migrate from 3.0.1 to 4.0.0

To get ride of the file mounted volume computers.txt. computers.txt is now inside the `/app/db` path.

If you see the warning message `Computers migration needed` here are the steps to migrate:

- Go to your docker-compose.yml root path
- Run
```
docker compose down || sudo docker compose down
mkdir -p appdata/db || sudo mkdir -p appdata/db
old_computer_location=$(grep "/app/computers.txt" docker-compose.yml | awk '{print $NF}' | awk -F':' '{print $1}')
[ -f "$old_computer_location" ] && (cp "$old_computer_location" appdata/db/computers.txt || sudo cp "$old_computer_location" appdata/db/computers.txt) && (sed -i 's|-.*:/app/computers.txt|- ./appdata/db:/app/db|' docker-compose.yml || sudo sed -i 's|-.*:/app/computers.txt|- ./appdata/db:/app/db|' docker-compose.yml)
docker compose up -d || sudo docker compose up -d
```
- Your app should start with all your computers on the new volume `./appdata/db`

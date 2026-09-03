# Custom AzerothCore Server

## Architecture

```text
AzerothCore upstream
       |
       +-- official core
       |
       +-- modules/
             |
             +-- mod-custom-server/
                    |
                    +-- our custom server functionality
```

This repository is based on official AzerothCore. The `upstream` remote points
to `https://github.com/azerothcore/azerothcore-wotlk.git`, and the working
branch is `custom-server`. Local Docker settings live in the ignored
`.env` and `docker-compose.override.yml` files.

Future custom C++ should generally go in
`modules/mod-custom-server/src/`, using AzerothCore hooks and module APIs
before considering core changes. Future module SQL belongs in
`modules/mod-custom-server/data/sql/db-auth/`, `db-characters/`, or
`db-world/` as appropriate. Do not edit AzerothCore's immutable
`data/sql/base/`, `data/sql/archive/`, or merged `data/sql/updates/db_*/`
directories.

## Starting the server

```bash
docker compose up -d
```

For a source or module rebuild:

```bash
docker compose up -d --build
```

## Checking status and logs

```bash
docker compose ps
docker compose logs -f ac-worldserver
docker compose logs -f ac-authserver
docker compose logs ac-db-import
```

## Stopping the server

```bash
docker compose down
```

This stops the containers but preserves the persistent database volume. Do
not delete the volume during normal shutdown.

## Worldserver console

Attach with:

```bash
docker attach ac-worldserver
```

Detach without killing worldserver:

```text
Ctrl+P
Ctrl+Q
```

Do not use `Ctrl+C` simply to detach.

## Creating the first administrator account

Attach to the worldserver console and run these commands with your own values;
do not put the password in this repository or insert credentials directly into
the database:

```text
account create <username> <password>
account set gmlevel <username> 3 -1
```

## WoW client connection

Use a separately obtained World of Warcraft 3.3.5a client, build `12340`.
AzerothCore does not provide the copyrighted client. In the client's
locale-specific `Data/<locale>/realmlist.wtf`, set:

```text
set realmlist 127.0.0.1
```

## Important ports

The server is configured for local access only:

```text
3724 - authserver
8085 - worldserver
3306 - local MySQL
7878 - SOAP, internal only and not published to the host
```

## Updating AzerothCore

Fetch upstream deliberately:

```bash
git fetch upstream
```

Review and deliberately merge or rebase `upstream/master` into
`custom-server`; do not rewrite history or force-push automatically. After an
upstream update, rebuild and verify database migrations and server startup:

```bash
docker compose up -d --build
docker compose ps
docker compose logs ac-db-import
docker compose logs ac-authserver
docker compose logs ac-worldserver
```

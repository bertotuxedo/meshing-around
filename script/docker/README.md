# Docker Compose deployment

This is the recommended deployment path. Python and all packages live inside
the image, so the host only needs Docker Engine with the Compose plugin.

## Quick start

1. From the repository root, edit `config.yaml`:

   ```yaml
   interface:
     type: tcp
     hostname: 192.168.1.95:4403
   ```

2. Validate the rendered Compose model and start the service:

   ```sh
   docker compose config --quiet
   docker compose up -d --build
   ```

3. Watch startup and confirm that the container becomes healthy:

   ```sh
   docker compose logs -f meshing-around
   docker compose ps
   ```

The default example targets the Meshtastic TCP API at
`192.168.1.95:4403`. Change it to the address of your node.

## How YAML configuration works

Meshing Around still uses Python's `ConfigParser` internally. At every
container start, `script/docker/render_config.py` performs these steps:

1. Load every default from `config.template`.
2. Overlay sections and keys from `config.yaml`.
3. Apply environment overrides.
4. Validate the primary interface and write a private, ephemeral `config.ini`
   under `/run/meshing-around`.

This keeps the upstream INI code compatible while making a short YAML file the
source of truth. YAML section and key names match their INI counterparts. Lists
are rendered as comma-separated values, and YAML booleans become `True` or
`False`.

Set `MESHING_AROUND_CONFIG_STRICT=true` to reject YAML sections or keys that do
not exist in `config.template`. Strict mode is useful in CI and when checking
for typos.

## Environment overrides

Common shortcuts are available:

| Variable | Target setting |
| --- | --- |
| `MESHTASTIC_TYPE` | `interface.type` |
| `MESHTASTIC_HOST` | host portion of `interface.hostname` |
| `MESHTASTIC_PORT` | port portion of `interface.hostname` |
| `LOG_LEVEL` | `general.sysloglevel` |

Any setting can be overridden using
`MESHING_AROUND__SECTION__KEY`. Environment variables take precedence over
both YAML and template defaults. For example:

```yaml
environment:
  MESHING_AROUND__GENERAL__RESPOND_BY_DM_ONLY: "False"
  MESHING_AROUND__BBS__ENABLED: "True"
```

Do not put passwords, tokens, channel keys, or device private keys in a public
repository. Keep sensitive overrides in an untracked `.env` file or use the
secret-management mechanism provided by your deployment platform.

## Persistent storage and logs

Compose creates two named volumes:

- `meshing-data` stores databases, BBS messages, surveys, and other mutable bot
  data at `/var/lib/meshing-around`.
- `meshing-logs` stores `meshbot.log` and `messages.log` at
  `/var/log/meshing-around`.

Console logs also use Docker's `json-file` driver with rotation. Change
`DOCKER_LOG_MAX_SIZE` and `DOCKER_LOG_MAX_FILES` in `.env` if needed.

Back up both volumes before a major upgrade. One portable approach is to stop
the service and archive each volume with a temporary container:

```sh
docker compose stop meshing-around
docker run --rm -v meshing-around_meshing-data:/source:ro -v "$PWD":/backup alpine tar czf /backup/meshing-data.tgz -C /source .
docker run --rm -v meshing-around_meshing-logs:/source:ro -v "$PWD":/backup alpine tar czf /backup/meshing-logs.tgz -C /source .
docker compose start meshing-around
```

## Legacy `config.ini`

Existing INI files remain supported. Replace the configuration bind mount with:

```yaml
volumes:
  - ./config.ini:/config/config.ini:ro
environment:
  MESHING_AROUND_CONFIG: /config/config.ini
```

The adapter merges the INI file over the current `config.template`, so newly
introduced defaults remain available.

## Serial and Bluetooth nodes

For USB serial, set `interface.type: serial` and the matching `port` in
`config.yaml`, then uncomment the `devices` example in `compose.yaml`. The user
running Docker must have permission to open the host device.

Bluetooth generally requires the host D-Bus socket and additional Linux
capabilities. Those permissions vary by distribution and are intentionally not
enabled by default. TCP is the simplest and most isolated container setup.

## Updating and removing

Rebuild after pulling changes:

```sh
docker compose build --pull
docker compose up -d
```

Stop and remove the container while preserving data:

```sh
docker compose down
```

Only add `--volumes` if you intentionally want to delete persisted bot data and
logs.

## Troubleshooting

- `docker compose config --quiet` catches Compose syntax and interpolation
  errors.
- `docker compose logs meshing-around` shows YAML conversion and startup errors.
- `docker inspect --format '{{json .State.Health}}' meshing-around` shows the
  healthcheck history.
- Confirm that the Docker host can reach the Meshtastic node on TCP port 4403.
- The service runs as non-root UID/GID `10001`. Bind-mounted data directories
  must be writable by that identity; the provided named volumes are initialized
  correctly automatically.

#!/usr/bin/env sh
set -eu

APP_DIR="${MESHING_AROUND_APP_DIR:-/app}"
RUNTIME_DIR="${MESHING_AROUND_RUNTIME_DIR:-/run/meshing-around}"
DATA_DIR="${MESHING_AROUND_DATA_DIR:-/var/lib/meshing-around}"
LOG_DIR="${MESHING_AROUND_LOG_DIR:-/var/log/meshing-around}"
CONFIG_SOURCE="${MESHING_AROUND_CONFIG:-/config/config.yaml}"
CONFIG_TEMPLATE="${MESHING_AROUND_CONFIG_TEMPLATE:-${APP_DIR}/config.template}"
RUNTIME_CONFIG="${RUNTIME_DIR}/config.ini"

if [ ! -f "$CONFIG_SOURCE" ]; then
    if [ -f /config/config.ini ]; then
        CONFIG_SOURCE=/config/config.ini
        printf '%s\n' "Configuration: using legacy /config/config.ini"
    elif [ -f "${APP_DIR}/config.yaml" ]; then
        CONFIG_SOURCE="${APP_DIR}/config.yaml"
        printf '%s\n' "Configuration: /config/config.yaml was not mounted; using image defaults"
    else
        printf '%s\n' "Configuration error: $CONFIG_SOURCE does not exist" >&2
        exit 2
    fi
fi

mkdir -p "$RUNTIME_DIR" "$DATA_DIR" "$LOG_DIR"
cp -R -n "${APP_DIR}/etc/data/." "$DATA_DIR/"

rm -f "${RUNTIME_DIR}/data" "${RUNTIME_DIR}/logs"
ln -s "$DATA_DIR" "${RUNTIME_DIR}/data"
ln -s "$LOG_DIR" "${RUNTIME_DIR}/logs"

python "${APP_DIR}/script/docker/render_config.py" \
    --template "$CONFIG_TEMPLATE" \
    --source "$CONFIG_SOURCE" \
    --output "$RUNTIME_CONFIG"

cd "$RUNTIME_DIR"
exec "$@"

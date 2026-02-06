#!/bin/bash

set -eu

USER_UID=${DEFAULT_UID:-65534}
USER_GID=${DEFAULT_GID:-65534}
USER_NAME=${DEFAULT_USERNAME:-caddy}
USER_HOME=${DEFAULT_HOME_DIR:-/home/$USER_NAME}

echo "Creating unprivileged user matching system user..."
echo "  Name:     $USER_NAME"
echo "  UID:      $USER_UID"
echo "  GID:      $USER_GID"
echo "  Home dir: $USER_HOME"

# create group if it doesn't exist
getent group $USER_GID 2>&1 > /dev/null || addgroup -S -g $USER_GID $USER_NAME

# create user if it doesn't exist
getent passwd $USER_UID 2>&1 > /dev/null || adduser -h $USER_HOME -u $USER_UID -G $USER_NAME -S $USER_NAME

if [[ "${ENABLE_SUDO:-0}" -eq 1 ]]; then
    echo "$USER_NAME ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/$USER_NAME
fi

exec su-exec $USER_NAME:$USER_NAME "$@"

#!/bin/sh
set -e

export PASSWORD_STORE_DIR="${PASSWORD_STORE_DIR:-/home/semaphore/.password-store}"

if [ -f /etc/semaphore/gpg/semaphore-private.key ]; then
    gpg --batch --import /etc/semaphore/gpg/semaphore-private.key
    KEY_ID=$(gpg --list-secret-keys --with-colons 2>/dev/null | awk -F: '/^sec:/ {print $5; exit}')
    if [ -n "$KEY_ID" ]; then
        echo "${KEY_ID}:6:" | gpg --import-ownertrust
    fi
fi

exec /usr/local/bin/server-wrapper

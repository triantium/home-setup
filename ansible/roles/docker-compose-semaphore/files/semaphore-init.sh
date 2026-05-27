#!/bin/sh
set -e

export PASSWORD_STORE_DIR="${PASSWORD_STORE_DIR:-/home/semaphore/.password-store}"

if [ -f /etc/semaphore/gpg/semaphore-private.key ]; then
    gpg --batch --import /etc/semaphore/gpg/semaphore-private.key
    KEY_FPR=$(gpg --list-secret-keys --with-colons 2>/dev/null | awk -F: '/^sec:/ {print $10; exit}')
    if [ -n "$KEY_FPR" ]; then
        echo "${KEY_FPR}:6:" | gpg --import-ownertrust
    fi
fi

exec /usr/local/bin/server-wrapper

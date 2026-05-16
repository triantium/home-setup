#!/usr/bin/env bash

crontab /etc/cron/crontab

# Repo Version 2
restic self-update

autorestic upgrade

crond -f

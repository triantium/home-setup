#!/usr/bin/env bash

crontab /etc/cron/crontab

restic self-update

autorestic upgrade

crond -f

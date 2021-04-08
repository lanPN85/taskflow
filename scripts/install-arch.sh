#!/bin/sh

set -eu

pacman -S --noconfirm python virtualenv

./scripts/build-install.sh \
    && cp ./etc/taskflowd.service /etc/systemd/system/taskflowd.service

systemctl start taskflowd
systemctl enable taskflowd

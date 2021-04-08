#!/bin/sh

set -eu

apt-get update
apt-get install -y \
    software-properties-common \
    systemd

add-apt-repository -y ppa:deadsnakes/ppa
apt-get update
apt-get install -y \
    python3.7-dev \
    virtualenv

./scripts/build-install.sh \
    && cp ./etc/taskflowd.service /etc/systemd/system/taskflowd.service

systemctl start taskflowd
systemctl enable taskflowd

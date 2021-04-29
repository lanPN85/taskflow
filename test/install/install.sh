#!/bin/sh

set -eu

# Detect distro
if [ -f /etc/os-release ]; then
    # freedesktop.org and systemd
    . /etc/os-release
    OS=$NAME
elif type lsb_release >/dev/null 2>&1; then
    # linuxbase.org
    OS="Debian"
elif [ -f /etc/lsb-release ]; then
    # For some versions of Debian/Ubuntu without lsb_release command
    . /etc/lsb-release
    OS="Debian"
else
    echo "Cannot detect distro"
    exit 1
fi

if OS=="Debian"; then
    . /etc/lsb-release
    DISTRO=${DISTRIB_ID}-${DISTRIB_RELEASE}

    dpkg -i dist/ubuntu/*.deb
fi

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

# Install git
if OS=="Debian"; then
    apt-get update
    apt-get install -y git
elif OS=="Arch Linux"; then
    pacman -S --noconfirm git
else
    exit 1
fi

rm -rf /tmp/taskflow || true
git clone https://github.com/lanPN85/taskflow /tmp/taskflow

# Run install script
if OS=="Debian"; then
    echo "Installing for Debian-based distro"
    cd /tmp/taskflow && ./scripts/install-debian.sh
elif OS=="Arch Linux"; then
    echo "Installing for Arch"
    cd /tmp/taskflow && ./scripts/install-arch.sh
else
    exit 1
fi

rm -rf /tmp/taskflow

echo "Successfully installed Taskflow"

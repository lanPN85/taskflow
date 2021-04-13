#!/bin/sh
set -eu

. /etc/lsb-release
DISTRO=${DISTRIB_ID}-${DISTRIB_RELEASE}

make -B build
rm -rf ./dist/${DISTRO} || true

debuild -us -uc

mkdir -p ./dist/${DISTRO}

cp ../taskflow*.deb \
    ../taskflow*.changes \
    ../taskflow*.tar.xz \
    ../taskflow*.dsc \
    ./dist/${DISTRO}

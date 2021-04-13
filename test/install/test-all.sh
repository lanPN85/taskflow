#!/bin/sh

set -eu

declare -a BASE_IMAGES=( \
    "jrei/systemd-ubuntu:18.04" \
    "jrei/systemd-ubuntu:20.04" \
)

for image in ${BASE_IMAGES[@]}; do
    echo $image
    docker run --rm -it \
        -v $(pwd):/workspace \
        $image \
        bash -c 'cd /workspace && ./test/install/install.sh && ./test/install/run-test.sh'
done

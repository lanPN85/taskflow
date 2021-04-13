#!/bin/bash

set -eu

build () {
    docker build -t taskflow-build:$2 \
		-f build/Dockerfile.ubuntu \
        --build-arg BASE_IMAGE=$1 \
		.

	docker run --rm -it \
		-v $(pwd):/workspace/taskflow \
        -w /workspace/taskflow \
		taskflow-build:$2 \
		bash -c "./build/build-ubuntu.sh"
}

build "ubuntu:18.04" "ubuntu-18.04"
build "ubuntu:20.04" "ubuntu-20.04"

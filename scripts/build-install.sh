#!/usr/bin/bash

set -eu

virtualenv -p python3.7 venv

source venv/bin/activate \
    && pip install -r requirements.txt \
    && pip install -r requirements.dev.txt \
    && pyinstaller taskflow.spec \
    && pyinstaller taskflowd.spec \
    && cp dist/taskflow /usr/bin/taskflow \
    && cp dist/taskflowd /usr/bin/taskflowd \
    && chmod a+x /usr/bin/taskflow /usr/bin/taskflowd \
    && mkdir -p /etc/taskflow \
    && test -f "/etc/taskflow/settings.yml" || cp ./etc/default-settings.yml /etc/taskflow/settings.yml \

rm -rf venv/

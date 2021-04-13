These are instructions for building Taskflow from source.

## Prerequisites
- Git
- Python 3.7+
- Make
- binutils

## Building the binaries
It is recommended to use a virtual Python environment (eg. virtualenv or conda) for the build. Inside the environment, run the following commands:

```bash
# Clone the source
git clone https://github.com/lanPN85/taskflow
cd taskflow/

# Install python dependencies
pip install -r requirements.txt
pip install -r requirements.dev.txt

# Run the build
make build
```

A successful build creates 2 files: `dist/taskflow` and `dist/taskflowd`. Copy these files to a directory in your path (typically `/usr/bin` will suffice)

```bash
chmod a+x dist/taskflow dist/taskflowd
sudo cp dist/taskflow /usr/bin/taskflow
sudo cp dist/taskflowd /usr/bin/taskflowd
```

## Setting up the daemon
The daemon `taskflowd` should be run as a system service to enable at startup. This repo contains a `systemd` service file for that purpose. For other init systems, please consult their documentation for instructions on registering services.

To register `taskflowd` with `systemd`, run:

```bash
sudo cp etc/taskflowd.service /etc/systemd/system/taskflowd.service
sudo systemctl enable --now taskflowd.service
```

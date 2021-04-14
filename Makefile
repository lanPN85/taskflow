BINDIR=/usr/bin
DESTDIR=

all: build

build: dist/taskflow dist/taskflowd

dist/taskflow: main.py taskflow/*.py taskflow/**/*.py taskflow.spec
	pyinstaller taskflow.spec

dist/taskflowd: daemon.py taskflow/*.py taskflow/**/*.py taskflowd.spec
	pyinstaller taskflowd.spec

# Install script for Debian and Arch
install:
	mkdir -p ${DESTDIR}${BINDIR}
	cp dist/taskflow ${DESTDIR}${BINDIR}/taskflow
	cp dist/taskflowd ${DESTDIR}${BINDIR}/taskflowd
	chmod a+x ${DESTDIR}${BINDIR}/taskflow ${DESTDIR}${BINDIR}/taskflowd
	mkdir -p ${DESTDIR}/etc/taskflow
	test -f "${DESTDIR}/etc/taskflow/settings.yml" || cp ./etc/default-settings.yml ${DESTDIR}/etc/taskflow/settings.yml

TEST_ARGS=--cov=.
TEST_TARGET=test/
test:
	pytest $(TEST_ARGS) $(TEST_TARGET)

.PHONY: test build all install

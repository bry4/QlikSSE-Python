SHELL=/bin/sh

export COMPOSE_DOCKER_CLI_BUILD=1
export BUILDKIT_PROGRESS=tty
export DOCKER_BUILDKIT=1

qlik-pysse-build:
	docker build \
		-t bvargasc/qlik-pysse:latest \
		--no-cache=false \
		.

qlik-pysse-run:
	docker run \
		--name qlik-pysse \
		-d -p 50053:50053 --rm \
		bvargasc/qlik-pysse:latest

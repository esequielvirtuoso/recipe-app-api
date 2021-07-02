include help.mk

build:
	DOCKER_BUILDKIT=1 \
	docker build --progress=plain \
		--target=security \
		--file=Dockerfile .
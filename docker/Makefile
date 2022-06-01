IMAGE_TAG := mssql-cli:latest

#DOCKER_BUILDKIT := 1
#export DOCKER_BUILDKIT

.PHONY: all
all: publish

.PHONY: image
image:
	docker build --build-arg=http_proxy=${http_proxy} --build-arg=https_proxy=${https_proxy} -t ${IMAGE_TAG} -f ./Dockerfile ..

.PHONY: publish
publish: image
	@echo "TODO: Publish is not yet implemented."

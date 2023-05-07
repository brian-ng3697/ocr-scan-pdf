BINARY=engine
buikd:
deploy-prod:
deploy-dev:
	@echo "Deploy dev process starting now..."
	@echo "Step 1: cd to Downloads and Google Cloud Authentication"
	gcloud auth login --no-launch-browser

build:
	@echo "Docker build"
	docker build -t staging .

docker-run:
	@echo "Docker run"

tag-and-push:
	docker tag <IMAGE_ID> asia-southeast1-docker.pkg.dev/ocr-opencv/apidev/sota4:staging
	docker push asia-southeast1-docker.pkg.dev/ocr-opencv/apidev/sota4:staging

local-setup:
	@echo "Create conda env"
	conda create -n opencv-scan python=3.8
	conda activate opencv-scan

opa-run:
	opa run --server --log-level debug

clean:
	if [ -f ${BINARY} ] ; then rm ${BINARY} ; fi

help:
	@echo ''
	@echo 'Usage: make [TARGET] [EXTRA_ARGUMENTS]'
	@echo 'Targets:'
	@echo 'docker 	Run docker'
	@echo 'dkrb  	Docker Compose run build'
	@echo 'dkr  	Docker Compose Run'
	@echo 'dlog  	Docker log'
	@echo ''
	@echo 'Extra arguments:'
	@echo '..will be update..'
IMAGE_NAME=dice-server-x86:latest

docker build --platform linux/amd64 --pull --rm -f "Dockerfile" -t $IMAGE_NAME "."

ARCH=arm64
IMAGE_NAME=dice-server-m1:latest

docker build --pull --rm -f "Dockerfile" -t dice-server-m1:latest "."

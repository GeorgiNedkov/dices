IMAGE_NAME=dice-server-x86:latest
docker build --no-cache --platform linux/amd64 --pull --rm -f "Dockerfile" -t $IMAGE_NAME "."

IMAGE_NAME=dice-server-m1:latest
docker build --no-cache --platform linux/arm64 --pull --rm -f "Dockerfile" -t $IMAGE_NAME "."

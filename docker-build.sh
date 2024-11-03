ARCH=arm64
docker build --platform linux/amd64 --pull --rm -f "Dockerfile" -t dice-server-x86:latest "."
docker build --pull --rm -f "Dockerfile" -t dice-server-m1:latest "."

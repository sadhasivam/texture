#!/usr/bin/env bash

# docker run --name texture -v .:/texture -it ubuntu:24.04  /bin/sh

# git clone https://github.com/sadhasivam/texture.git

apt-get update
apt-get install -y curl ca-certificates git build-essential

curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"

uv python install 3.14.3 --default
uv python pin 3.14.3

apt-get install -y protobuf-compiler

cd /tmp
curl -LO https://go.dev/dl/go1.26.1.linux-amd64.tar.gz
rm -rf /usr/local/go
tar -C /usr/local -xzf go1.26.1.linux-amd64.tar.gz
echo 'export PATH=/usr/local/go/bin:$PATH' >/etc/profile.d/go.sh

echo 'export PATH="$HOME/go/bin:/usr/local/go/bin:$HOME/.local/bin:$PATH"' >> /root/.bashrc
echo 'export PATH="$HOME/go/bin:/usr/local/go/bin:$HOME/.local/bin:$PATH"' >> /root/.profile



apt-get install -y debian-keyring debian-archive-keyring apt-transport-https curl
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | tee /etc/apt/sources.list.d/caddy-stable.list
chmod o+r /usr/share/keyrings/caddy-stable-archive-keyring.gpg
chmod o+r /etc/apt/sources.list.d/caddy-stable.list
apt-get update
apt-get install -y caddy

source /root/.profile
source /root/.bashrc
hash -r

python3 --version
uv --version
go version

caddy version

go install google.golang.org/protobuf/cmd/protoc-gen-go@latest
go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@latest

# systemctl status caddy --no-pager

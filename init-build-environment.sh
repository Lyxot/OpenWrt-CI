#!/usr/bin/env bash

set -euo pipefail

extra_packages=("$@")
init_script="$(mktemp)"
trap 'rm -f "$init_script"' EXIT

# GitHub-hosted runners use a regional Azure mirror as their first apt source.
# Some runner regions cannot reach that mirror and apt can otherwise wait for
# tens of minutes before trying its fallback. Prefer the Ubuntu HTTPS archive
# directly and bound every repository request.
if [[ -f /etc/apt/apt-mirrors.txt ]]; then
    printf '%s\n' 'https://archive.ubuntu.com/ubuntu' \
        | sudo tee /etc/apt/apt-mirrors.txt >/dev/null
fi
sudo tee /etc/apt/apt.conf.d/99-openwrt-ci-network >/dev/null <<'EOF'
Acquire::Retries "3";
Acquire::http::Timeout "30";
Acquire::https::Timeout "30";
EOF

curl --fail --location --retry 3 --show-error \
    --connect-timeout 15 --max-time 120 \
    --output "$init_script" \
    https://build-scripts.immortalwrt.org/init_build_environment.sh

# A full distribution upgrade is unnecessary on an ephemeral runner and can
# replace preinstalled Actions software. The outer timeout ensures an upstream
# repository outage cannot consume the entire build job.
sed -i \
    -e 's/curl -s "myip.ipip.net"/curl --silent --show-error --connect-timeout 10 --max-time 20 "myip.ipip.net"/' \
    -e '/^[[:space:]]*apt full-upgrade -y /d' \
    "$init_script"
sudo env DEBIAN_FRONTEND=noninteractive \
    timeout --kill-after=2m --signal=TERM 40m bash "$init_script"
sudo env DEBIAN_FRONTEND=noninteractive dpkg --configure -a

if ((${#extra_packages[@]})); then
    sudo env DEBIAN_FRONTEND=noninteractive apt-get install \
        --yes --no-install-recommends "${extra_packages[@]}"
fi
sudo apt-get clean

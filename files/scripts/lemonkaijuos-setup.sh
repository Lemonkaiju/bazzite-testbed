#!/usr/bin/env bash
# LemonKaijuOS — Image build-time setup
# Runs inside the container during image build. Do not run on live system.
set -oue pipefail

echo ">>> LemonKaijuOS: Installing Python dependencies"
# Install packages not available as python3-* RPMs in Fedora repos
pip3 install --prefix=/usr --no-cache-dir \
    passlib \
    flask-cors \
    aiohttp \
    colorlog

echo ">>> LemonKaijuOS: Creating PIN database directory"
mkdir -p /etc/pinlock
chmod 755 /etc/pinlock

echo ">>> LemonKaijuOS: Setting permissions on CLI tools"
chmod +x \
    /usr/bin/pin-auth \
    /usr/bin/security-cli \
    /usr/bin/profile-cli \
    /usr/bin/stfd-cli \
    /usr/bin/lemonkaijuos-pin-validate

echo ">>> LemonKaijuOS: Setting permissions on first-boot wizard"
chmod +x \
    /usr/share/lemonkaijuos/first-boot-wizard/run-wizard.sh \
    /usr/share/lemonkaijuos/first-boot-wizard/wizard.py

echo ">>> LemonKaijuOS: Setup complete"

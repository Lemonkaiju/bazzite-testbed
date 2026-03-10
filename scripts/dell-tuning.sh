#!/usr/bin/env bash
set -oue pipefail

# Dell Latitude 5320 / 7320 - Persistent Tuning
# These changes are baked into the OCI image during build.

echo ">>> Applying Dell Tablet/2-in-1 fixes"

# 1. Screen rotation and sensor support
# iio-sensor-proxy is installed via rpm-ostree module in recipe.yml
# We ensure the service is enabled (though systemd module can do this too)

# 2. Early-load modules for Tablet Mode & Bluetooth stability
# We create the Dracut configuration so it's baked into the initramfs
mkdir -p /etc/dracut.conf.d
cat > /etc/dracut.conf.d/7320-modules.conf << EOF
# Dell Latitude 7XXX/5XXX - Force early loading of tablet mode and Bluetooth modules
force_drivers+=" pinctrl_tigerlake soc_button_array iwlwifi btintel "
EOF

# 3. Kernel Arguments for Power & Stability
# In BlueBuild, you don't run 'rpm-ostree kargs' during the OCI build.
# Instead, these are handled via specific UBlue/Bazzite kargs files or
# applied at install time. However, a common way to include them in the image
# so they are applied to the deployment is via a file in /etc/default/grub.d/
# or similar, but Bazzite has a specific way: /usr/lib/bootc/kargs.d/ (for bootc images)
# or just through the recipe.

echo ">>> Dell tuning script finished"

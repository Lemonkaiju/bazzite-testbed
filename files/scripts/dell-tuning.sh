#!/usr/bin/env bash
set -oue pipefail

# Dell Latitude 5320 / 7320 - Persistent Tuning
# These changes are baked into the OCI image during build.

echo ">>> Applying Dell Tablet/2-in-1 fixes"

# 1. Screen rotation and sensor support
# iio-sensor-proxy is installed via rpm-ostree module in recipe.yml

# 2. Early-load modules for Tablet Mode & Bluetooth stability
# We create the Dracut configuration so it's baked into the initramfs
mkdir -p /etc/dracut.conf.d
cat > /etc/dracut.conf.d/7320-modules.conf << EOF
# Dell Latitude 7XXX/5XXX - Force early loading of tablet mode and Bluetooth modules
force_drivers+=" pinctrl_tigerlake soc_button_array iwlwifi btintel "
EOF

# 3. Kernel Arguments for Power & Stability
# In BlueBuild, we add kargs through the recipe or via files/usr/lib/bootc/kargs.d/
# For simplicity, we can also use the ublue-os/main methodology of appending to /etc/default/grub (if it exists)
# But standard BlueBuild way is the kargs module or a script.

echo ">>> Dell tuning script finished"

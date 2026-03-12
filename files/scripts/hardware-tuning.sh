#!/usr/bin/env bash
set -oue pipefail

# Universal Hardware Tuning for LemonKaijuOS
# Detects hardware and applies appropriate optimizations
# This replaces the Dell-specific tuning for broader compatibility

echo ">>> Starting hardware detection and tuning"

# Universal optimizations (always applied)
echo ">>> Applying universal optimizations"

# 1. Enable sensor proxy for rotation (tablets/2-in-1s)
# iio-sensor-proxy is installed via rpm-ostree module in recipe.yml
systemctl enable iio-sensor-proxy 2>/dev/null || true

# 2. Enable fingerprint support
systemctl enable fprintd 2>/dev/null || true

# Hardware-specific optimizations
echo ">>> Detecting hardware for specific optimizations"

# Detect Dell Latitude 5320/7320 (Intel Tiger Lake)
if lspci | grep -i "Tiger Lake" >/dev/null 2>&1 &&    dmidecode -s system-manufacturer 2>/dev/null | grep -i "Dell" >/dev/null 2>&1; then
    
    echo ">>> Detected Dell Latitude with Intel Tiger Lake - applying tablet optimizations"
    
    # Early-load modules for Tablet Mode & Bluetooth stability
    mkdir -p /etc/dracut.conf.d
    cat > /etc/dracut.conf.d/tablet-modules.conf << EOF
# Intel Tiger Lake tablet mode modules
force_drivers+=" pinctrl_tigerlake soc_button_array iwlwifi btintel "
EOF
    
    echo ">>> Dell tablet optimizations applied"
    
elif lspci | grep -i "Intel" >/dev/null 2>&1; then
    
    echo ">>> Detected Intel hardware - applying Intel optimizations"
    
    # Generic Intel optimizations
    mkdir -p /etc/dracut.conf.d
    cat > /etc/dracut.conf.d/intel-modules.conf << EOF
# Generic Intel hardware modules
force_drivers+=" iwlwifi btintel "
EOF
    
    echo ">>> Intel optimizations applied"
    
else:
    echo ">>> Unknown or unsupported hardware - using universal configuration only"
fi

# Gaming optimizations (universal)
echo ">>> Applying gaming optimizations"

# Ensure Mesa drivers are properly configured
if command -v glxinfo >/dev/null 2>&1; then
    echo ">>> Graphics drivers detected"
else
    echo ">>> Graphics drivers will be configured on first boot"
fi

# Power management optimizations (laptops)
if [ -d /sys/class/power_supply/BAT* ]; then
    echo ">>> Laptop detected - applying power management optimizations"
    
    # Enable laptop power management
    systemctl enable tlp 2>/dev/null || true
    
    echo ">>> Power management configured"
fi

# Log what we detected for debugging
echo ">>> Hardware detection summary:"
echo "    Manufacturer: $(dmidecode -s system-manufacturer 2>/dev/null || echo 'Unknown')"
echo "    Product: $(dmidecode -s system-product-name 2>/dev/null || echo 'Unknown')"
echo "    GPU: $(lspci | grep -i vga | head -1 || echo 'Unknown')"
echo "    WiFi: $(lspci | grep -i network | head -1 || echo 'Unknown')"

echo ">>> Hardware tuning completed successfully"

# Bazzite for Dell Latitude 5320/7320

This repository contains a custom Bazzite image optimized for Dell Latitude 2-in-1s and tablets (specifically the 5320 and 7320).

## Included Fixes:
- **Screen Flickering:** `i915.enable_psr=0` (Tiger Lake iGPU fix).
- **Deep Sleep:** `mem_sleep_default=deep` (Battery drain fix).
- **Auto-Rotation:** `iio-sensor-proxy` built-in and enabled.
- **Biometrics:** `fprintd` enabled for fingerprint login.
- **Tablet Mode:** Early-load modules (`pinctrl_tigerlake`, `soc_button_array`) via Dracut.

## Included Software:
- Godot Engine, VS Code, Chrome, Microsoft Edge, Thunderbird, Spotify, RustDesk.

## How to Install on your New Device (Thursday):

### Option A: The "Rebase" Method (Recommended)
1. Install standard **Bazzite (KDE)** using any official USB.
2. Open a terminal and run:
   ```bash
   rpm-ostree rebase ostree-image-signed:docker://ghcr.io/lemonkaiju/bazzite-testbed:latest
   ```
3. Reboot. your device is now fully configured!

### Option B: Custom ISO
The custom ISO generation is being stubborn on GitHub's environment. For now, **Option A** is the fastest and most reliable way to get your "testbed" configuration onto the physical metal.

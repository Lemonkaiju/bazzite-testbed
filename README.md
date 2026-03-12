# LemonKaijuOS - Easy Gaming & Productivity Build

A custom Bazzite-based Linux distribution that comes pre-loaded with games, creative tools, and productivity apps. Built for families and users who want a "just works" experience with everything ready to go.

## What's Included

### 🎮 Gaming Ready
- Steam pre-configured with Proton
- Godot Engine for game development
- Gaming drivers and optimizations
- Controller support out of the box

### 🛠️ Creative & Productivity Tools
- VS Code with popular extensions
- Chrome and Microsoft Edge browsers
- Thunderbird email client
- Spotify for music streaming
- RustDesk for remote access

### 🖥️ Tablet & 2-in-1 Optimizations
- Screen flickering fixes (i915.enable_psr=0)
- Deep sleep support (mem_sleep_default=deep)
- Auto-rotation for tablets (iio-sensor-proxy)
- Fingerprint login (fprintd)
- Tablet mode with early-load modules

### 🔒 Privacy & Security
- Mullvad Browser pre-configured
- Enhanced privacy settings
- No telemetry or tracking

## Perfect For
- **Family PCs** - Living room, kitchen, bedroom setups
- **Gaming Desktops** - Steam deck alternative
- **Creative Workstations** - Development and content creation
- **2-in-1 Laptops** - Tablet mode with touch support

## Installation

### Option A: Rebase Method (Recommended)
1. Install standard Bazzite (KDE) from official USB
2. Run: `rpm-ostree rebase ostree-image-signed:docker://ghcr.io/lemonkaiju/bazzite-testbed:latest`
3. Reboot and enjoy!

### Option B: Custom ISO
Download the pre-built ISO from GitHub Releases for a fresh installation.

---

Built with ❤️ for families who want privacy without complexity.

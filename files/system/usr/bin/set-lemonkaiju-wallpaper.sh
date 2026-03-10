#!/bin/bash
if [ ! -f ~/.lemonkaiju_wallpaper_set ]; then
  # Wait a few seconds for Plasma to fully initialize
  sleep 5
  plasma-apply-wallpaperimage /usr/share/wallpapers/lemonkaiju_1080p.png
  touch ~/.lemonkaiju_wallpaper_set
fi

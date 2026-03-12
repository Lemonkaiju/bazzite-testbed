#!/bin/bash
set -e

DATE=$(date +%Y%m%d)
TIME=$(date +%H%M%S)
TAG="${DATE}-${TIME}"

echo "=== Chunking ISO ==="
cd ./output

# Split into 1.9GB chunks
split -b 1900M -d LemonKaijuOS-${DATE}.iso LemonKaijuOS-${DATE}.part.

# Create checksum of original ISO
sha256sum LemonKaijuOS-${DATE}.iso > LemonKaijuOS-${DATE}.sha256

echo "Files created:"
ls -lh

echo "=== Creating GitHub Release: $TAG ==="
gh release create "$TAG" \
  --title "LemonKaijuOS $TAG" \
  --notes "LemonKaijuOS ISO split into chunks for download.

Each chunk is under 2GB for GitHub Releases compatibility.
Use the STFD installer app to download and reassemble automatically." \
  --latest

echo "=== Uploading chunks ==="
for file in LemonKaijuOS-${DATE}.part.*; do
  echo "Uploading: $file"
  gh release upload "$TAG" "$file"
done

echo "=== Uploading checksum ==="
gh release upload "$TAG" LemonKaijuOS-${DATE}.sha256

echo "=== Done! Release: $TAG ==="

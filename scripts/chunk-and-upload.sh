#!/bin/bash
set -e

echo "=== Finding ISO file ==="
cd ./output

# Find any LemonKaijuOS ISO file
ISO_FILE=$(ls LemonKaijuOS-*.iso 2>/dev/null | head -1)

if [ -z "$ISO_FILE" ]; then
    echo "❌ No LemonKaijuOS ISO file found in ./output/"
    echo "Contents:"
    ls -la
    exit 1
fi

echo "✅ Found ISO: $ISO_FILE"

# Extract date from filename for consistency
DATE=$(echo "$ISO_FILE" | sed 's/.*LemonKaijuOS-\([0-9]*\)\.iso/\1/')
TIME=$(date +%H%M%S)
TAG="${DATE}-${TIME}"

echo "=== Chunking ISO ==="
# Split into 1.9GB chunks
split -b 1900M -d "$ISO_FILE" "LemonKaijuOS-${DATE}.part."

# Create checksum of original ISO
sha256sum "$ISO_FILE" > "LemonKaijuOS-${DATE}.sha256"

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
gh release upload "$TAG" "LemonKaijuOS-${DATE}.sha256"

echo "=== Done! Release: $TAG ==="

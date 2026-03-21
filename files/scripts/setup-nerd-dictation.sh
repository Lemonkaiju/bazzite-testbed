#!/usr/bin/env bash
set -oue pipefail

echo ">>> Installing Nerd Dictation (offline speech-to-text)"

# 1. Install vosk Python library (speech recognition engine)
pip3 install vosk --quiet

# 2. Download nerd-dictation binary
curl -fsSL \
  "https://raw.githubusercontent.com/ideasman42/nerd-dictation/main/nerd-dictation" \
  -o /usr/local/bin/nerd-dictation
chmod +x /usr/local/bin/nerd-dictation

# 3. Install a first-run helper that downloads the Vosk language model
# The model is ~40MB and lives in the user's home dir, so it's downloaded
# on first use rather than baked into the ISO.
cat > /usr/local/bin/nerd-dictation-setup << 'EOF'
#!/usr/bin/env bash
# Run this once per user to download the English Vosk model
MODEL_DIR="$HOME/.config/nerd-dictation"
MODEL_URL="https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"

if [ -d "$MODEL_DIR/model" ]; then
  echo "Vosk model already installed at $MODEL_DIR/model"
  exit 0
fi

echo "Downloading Vosk English model (~40MB)..."
mkdir -p "$MODEL_DIR"
curl -L "$MODEL_URL" -o /tmp/vosk-model.zip
unzip -q /tmp/vosk-model.zip -d /tmp/
mv /tmp/vosk-model-small-en-us-0.15 "$MODEL_DIR/model"
rm /tmp/vosk-model.zip
echo "Done! Run: nerd-dictation begin --vosk-model-dir $MODEL_DIR/model"
EOF
chmod +x /usr/local/bin/nerd-dictation-setup

echo ">>> Nerd Dictation installed. Users should run 'nerd-dictation-setup' on first login."

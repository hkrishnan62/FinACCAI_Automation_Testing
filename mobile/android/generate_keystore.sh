#!/bin/bash
# Generate a keystore for signing Android releases
# Usage: ./generate_keystore.sh

KEYSTORE_PATH="${FINACCAI_KEYSTORE_PATH:-keystore.jks}"
KEYSTORE_PASSWORD="${FINACCAI_KEYSTORE_PASSWORD:-}"
KEY_ALIAS="${FINACCAI_KEY_ALIAS:-finaccai}"
KEY_PASSWORD="${FINACCAI_KEY_PASSWORD:-}"

if [ -z "$KEYSTORE_PASSWORD" ] || [ -z "$KEY_PASSWORD" ]; then
    echo "Error: FINACCAI_KEYSTORE_PASSWORD and FINACCAI_KEY_PASSWORD must be set."
    echo "Usage:"
    echo "  export FINACCAI_KEYSTORE_PASSWORD='your-secure-password'"
    echo "  export FINACCAI_KEY_PASSWORD='your-secure-password'"
    echo "  ./generate_keystore.sh"
    exit 1
fi

keytool -genkey -v -keystore "$KEYSTORE_PATH" \
    -alias "$KEY_ALIAS" \
    -keyalg RSA \
    -keysize 2048 \
    -validity 36500 \
    -storepass "$KEYSTORE_PASSWORD" \
    -keypass "$KEY_PASSWORD" \
    -dname "CN=FinAccAI,O=FinAccAI,L=San Francisco,ST=California,C=US"

echo "✓ Keystore generated: $KEYSTORE_PATH"
echo "Keep this file safe and set FINACCAI_KEYSTORE_PATH, FINACCAI_KEYSTORE_PASSWORD, FINACCAI_KEY_PASSWORD for builds."

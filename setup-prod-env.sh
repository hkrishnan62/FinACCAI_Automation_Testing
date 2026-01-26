#!/bin/bash
# Setup production secrets and environment
# Usage: source setup-prod-env.sh

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}FinAccAI Production Environment Setup${NC}"
echo ""

# Load .env.prod if it exists
if [ -f ".env.prod" ]; then
    echo "Loading .env.prod..."
    source .env.prod
else
    echo -e "${YELLOW}No .env.prod file found. Create one from .env.prod.example:${NC}"
    echo "  cp .env.prod.example .env.prod"
    echo "  Edit .env.prod with your production values"
    echo "  source setup-prod-env.sh"
    exit 1
fi

echo ""
echo "Production environment variables loaded:"
echo "  Keystore: ${FINACCAI_KEYSTORE_PATH:-(not set)}"
echo "  Backend: ${FINACCAI_BACKEND_URL:-(not set)}"
echo "  Privacy: ${FINACCAI_PRIVACY_POLICY_URL:-(not set)}"
echo ""

# Verify keystore
if [ -z "$FINACCAI_KEYSTORE_PATH" ]; then
    echo -e "${RED}❌ FINACCAI_KEYSTORE_PATH not set${NC}"
    exit 1
fi

if [ ! -f "$FINACCAI_KEYSTORE_PATH" ]; then
    echo -e "${RED}❌ Keystore file not found: $FINACCAI_KEYSTORE_PATH${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Keystore configured: $FINACCAI_KEYSTORE_PATH${NC}"

# Verify passwords
if [ -z "$FINACCAI_KEYSTORE_PASSWORD" ] || [ -z "$FINACCAI_KEY_PASSWORD" ]; then
    echo -e "${RED}❌ Keystore passwords not set${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Keystore passwords set${NC}"

# Verify backend URL
if [ -z "$FINACCAI_BACKEND_URL" ]; then
    echo -e "${YELLOW}⚠ FINACCAI_BACKEND_URL not set, using default${NC}"
else
    if [[ "$FINACCAI_BACKEND_URL" == https://* ]]; then
        echo -e "${GREEN}✓ Backend URL: $FINACCAI_BACKEND_URL${NC}"
    else
        echo -e "${RED}❌ Backend URL must use HTTPS: $FINACCAI_BACKEND_URL${NC}"
        exit 1
    fi
fi

echo ""
echo -e "${GREEN}✅ Production environment ready!${NC}"
echo ""
echo "Now you can:"
echo "  ./mobile/verify-prod.sh    # Verify production settings"
echo "  ./mobile/deploy-prod.sh    # Build and deploy"
echo ""

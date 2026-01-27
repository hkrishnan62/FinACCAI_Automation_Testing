#!/bin/bash
# Create placeholder Play Store assets for FinAccAI Mobile
# Production use: Replace these with professional designs

set -e

ASSETS_DIR="/workspaces/FinACCAI_Automation_Testing/mobile/play_store_assets"
mkdir -p "$ASSETS_DIR"/{icons,screenshots,graphics}

GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${GREEN}📦 Creating Play Store Assets${NC}\n"

# 1. App Icon (512×512)
echo -e "${BLUE}Creating App Icon (512×512)...${NC}"
convert -size 512x512 xc:'#0C4B8F' \
  -font "DejaVu-Sans-Bold" -pointsize 200 \
  -fill '#00D1A0' -gravity center \
  -annotate +0+0 'FA' \
  "$ASSETS_DIR/icons/app_icon_512.png"
echo "✓ $ASSETS_DIR/icons/app_icon_512.png"

# 2. Feature Graphic (1024×500)
echo -e "${BLUE}Creating Feature Graphic (1024×500)...${NC}"
convert -size 1024x500 \
  -background '#0C4B8F' \
  -fill '#00D1A0' -font "DejaVu-Sans-Bold" -pointsize 100 \
  -gravity west -annotate +50+0 'FinAccAI' \
  -fill '#FFFFFF' -font "DejaVu-Sans" -pointsize 50 \
  -gravity southeast -annotate +30+30 'Financial Statement Accessibility' \
  "$ASSETS_DIR/graphics/feature_graphic_1024x500.png"
echo "✓ $ASSETS_DIR/graphics/feature_graphic_1024x500.png"

# 3. Phone Screenshots (1080×1920)
echo -e "${BLUE}Creating Phone Screenshots (1080×1920)...${NC}"

for i in {1..5}; do
  convert -size 1080x1920 xc:'#1A1A2E' \
    -stroke '#00D1A0' -strokewidth 2 -fill none \
    -draw "rectangle 0,0 1080,1920" \
    -fill '#00D1A0' -pointsize 60 -font "DejaVu-Sans-Bold" \
    -gravity north -annotate +0+100 "FinAccAI v1.0" \
    -fill '#FFFFFF' -pointsize 40 -font "DejaVu-Sans" \
    -gravity center -annotate +0+0 "Screenshot $i\n\nLive Accessibility Analysis" \
    "$ASSETS_DIR/screenshots/phone_${i}_1080x1920.png"
  echo "✓ $ASSETS_DIR/screenshots/phone_${i}_1080x1920.png"
done

# 4. Tablet Screenshots (1920×1080)
echo -e "${BLUE}Creating Tablet Screenshots (1920×1080)...${NC}"

for i in {1..2}; do
  convert -size 1920x1080 xc:'#1A1A2E' \
    -stroke '#00D1A0' -strokewidth 3 -fill none \
    -draw "rectangle 0,0 1920,1080" \
    -fill '#00D1A0' -pointsize 80 -font "DejaVu-Sans-Bold" \
    -gravity northwest -annotate +50+50 "FinAccAI" \
    -fill '#FFFFFF' -pointsize 50 -font "DejaVu-Sans" \
    -gravity center -annotate +0+0 "Tablet View $i" \
    "$ASSETS_DIR/screenshots/tablet_${i}_1920x1080.png"
  echo "✓ $ASSETS_DIR/screenshots/tablet_${i}_1920x1080.png"
done

echo -e "\n${GREEN}✅ All Play Store assets created!${NC}\n"

echo "📁 Asset Directory Structure:"
tree "$ASSETS_DIR" 2>/dev/null || find "$ASSETS_DIR" -type f | sed 's|.*/||' | sort

echo -e "\n${BLUE}📝 Next Steps:${NC}"
echo "1. Replace placeholder assets with professional designs:"
echo "   - App Icon: $ASSETS_DIR/icons/app_icon_512.png"
echo "   - Feature Graphic: $ASSETS_DIR/graphics/feature_graphic_1024x500.png"
echo "   - Screenshots: $ASSETS_DIR/screenshots/"
echo ""
echo "2. Upload to Google Play Console:"
echo "   - App → Graphics Assets → Upload new files"
echo ""
echo "3. For professional screenshots, use tools like:"
echo "   - Figma (free tier available)"
echo "   - Canva (templates available)"
echo "   - Adobe XD (for advanced designs)"


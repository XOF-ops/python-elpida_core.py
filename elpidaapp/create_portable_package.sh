#!/bin/bash
# ============================================================
# Create portable Body package for new codespace
# ============================================================
# Packages only the files needed for deployment.
# Excludes all research history, experiments, and archives.
# ============================================================

PACKAGE_NAME="elpida_body_$(date +%Y%m%d_%H%M%S).tar.gz"

echo "Creating portable Body package..."
echo "Package: $PACKAGE_NAME"
echo ""

# Create temp directory
TEMP_DIR=$(mktemp -d)
DEST="$TEMP_DIR/elpida_body"
mkdir -p "$DEST"

# ── Copy elpidaapp package ──
echo "Copying elpidaapp/..."
cp -r elpidaapp "$DEST/"

# ── Copy dependencies ──
echo "Copying dependencies..."
cp llm_client.py "$DEST/"
cp elpida_config.py "$DEST/"
cp elpida_domains.json "$DEST/"

# ── Copy kernel ──
echo "Copying kernel..."
mkdir -p "$DEST/kernel"
cp kernel/kernel.json "$DEST/kernel/"

# ── Copy S3Cloud (optional) ──
if [ -d ElpidaS3Cloud ]; then
    echo "Copying ElpidaS3Cloud..."
    cp -r ElpidaS3Cloud "$DEST/"
fi

# ── Copy .env template (NOT your actual .env!) ──
echo "Including .env.template..."
# Already in elpidaapp/

# ── Create archive ──
echo ""
echo "Creating archive..."
cd "$TEMP_DIR"
tar -czf "/tmp/$PACKAGE_NAME" elpida_body/

# Move to workspace
mv "/tmp/$PACKAGE_NAME" /workspaces/python-elpida_core.py/

# Cleanup
rm -rf "$TEMP_DIR"

echo ""
echo "════════════════════════════════════════════════════════"
echo "✓ Package created: $PACKAGE_NAME"
du -h "/workspaces/python-elpida_core.py/$PACKAGE_NAME"
echo "════════════════════════════════════════════════════════"
echo ""
echo "To deploy:"
echo "  1. Copy $PACKAGE_NAME to new codespace"
echo "  2. Extract: tar -xzf $PACKAGE_NAME"
echo "  3. cd elpida_body/"
echo "  4. Copy your .env file with API keys"
echo "  5. bash elpidaapp/deploy_to_new_space.sh"
echo ""

#!/bin/sh
# Build the slide deck (PPTX) and its PDF export.  Requires: npm install (pptxgenjs, react-icons, react, react-dom, sharp), LibreOffice.
set -e
cd "$(dirname "$0")"
node build_deck.js
PROFILE="${TMPDIR:-/tmp}/stat3013_lo_profile"
FONTCONFIG_FILE="$PROFILE/fonts.conf" /Applications/LibreOffice.app/Contents/MacOS/soffice -env:UserInstallation="file://$PROFILE" \
  --headless --convert-to pdf --outdir out out/ClinicAnalytics_Slides.pptx >/dev/null 2>&1
echo "slides/out/ClinicAnalytics_Slides.pptx + .pdf"

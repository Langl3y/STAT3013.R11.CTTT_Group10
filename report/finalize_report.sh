#!/bin/sh
# Usage: report/finalize_report.sh IN.docx OUT.docx OUT.pdf
set -e
PROFILE="${TMPDIR:-/tmp}/stat3013_lo_profile"
mkdir -p "$PROFILE/user/Scripts/python"
cp "$(dirname "$0")/lo_macro.py" "$PROFILE/user/Scripts/python/lo_macro.py"
# make macOS system fonts (Times New Roman, Courier New) visible to LibreOffice's fontconfig
cat > "$PROFILE/fonts.conf" <<XML
<?xml version="1.0"?><!DOCTYPE fontconfig SYSTEM "fonts.dtd">
<fontconfig><dir>/System/Library/Fonts</dir><dir>/System/Library/Fonts/Supplemental</dir>
<dir>/Library/Fonts</dir><dir>~/Library/Fonts</dir><cachedir>$PROFILE/fccache</cachedir></fontconfig>
XML
export FONTCONFIG_FILE="$PROFILE/fonts.conf"
abs() { python3 -c 'import os,sys;print(os.path.abspath(sys.argv[1]))' "$1"; }
export REPORT_IN="$(abs "$1")" REPORT_OUT_DOCX="$(abs "$2")" REPORT_OUT_PDF="$(abs "$3")"
rm -f "$REPORT_OUT_PDF.log"
/Applications/LibreOffice.app/Contents/MacOS/soffice -env:UserInstallation="file://$PROFILE" --headless --norestore \
  "vnd.sun.star.script:lo_macro.py\$finalize?language=Python&location=user"
cat "$REPORT_OUT_PDF.log" && rm -f "$REPORT_OUT_PDF.log"

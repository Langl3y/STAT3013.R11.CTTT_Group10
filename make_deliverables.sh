#!/bin/sh
# Build every deliverable and copy it into deliverables/ with the course naming convention.
#   ./make_deliverables.sh [VERSION] [YYYYMMDD]      e.g.  ./make_deliverables.sh 1.0 20261128
set -e
cd "$(dirname "$0")"
VER="${1:-1.0}"
DATE="${2:-$(date +%Y%m%d)}"
PREFIX="STAT3013.R11.CTTT.Group10"      # STAT3013.<Rxx>.<GroupYY>  -- edit if your lecturer expects another form
PROJ="ClinicAnalytics"
REPO_URL="https://github.com/Langl3y/STAT3013.R11.CTTT_Group10"
VIDEO_URL="${VIDEO_URL:-<ADD 15-MINUTE DEMO VIDEO LINK>}"
OUT=deliverables
B="${PREFIX}_${PROJ}"

report/build.sh
(cd paper/ieee && tectonic -X compile main.tex >/dev/null)
slides/build.sh
(cd docs/ai_disclosure && tectonic -X compile ai_disclosure.tex >/dev/null)

rm -rf "$OUT" && mkdir -p "$OUT"
cp report/out/FullReport.pdf          "$OUT/${B}_FullReport_v${VER}_${DATE}.pdf"
cp report/out/FullReport_final.docx   "$OUT/${B}_FullReport_v${VER}_${DATE}.docx"
cp paper/ieee/main.pdf                "$OUT/${B}_IEEEpaper_v${VER}_${DATE}.pdf"
cp slides/out/ClinicAnalytics_Slides.pptx "$OUT/${B}_Slides_v${VER}_${DATE}.pptx"
cp slides/out/ClinicAnalytics_Slides.pdf  "$OUT/${B}_Slides_v${VER}_${DATE}.pdf"
cp docs/ai_disclosure/ai_disclosure.pdf   "$OUT/${B}_AI_Explanation_${DATE}.pdf"
zip -qj "$OUT/${B}_Dataset_${DATE}.zip" data/*.csv data/README.md
git archive --format=zip -o "$OUT/${B}_SourceCode_${DATE}.zip" HEAD
cat > "$OUT/${B}_Links_${DATE}.txt" <<TXT
Project: ${PROJ} - STAT3013.R11.CTTT, Group 10 - Ho Van Hieu (19521497)
GitHub repository: ${REPO_URL}
Dataset: ${REPO_URL}/tree/main/data
Demo video (15 min): ${VIDEO_URL}
TXT
echo "Still to add by hand: ${B}_Turnitin_${DATE}.png and ${B}_AIcheck_<ToolName>_${DATE}.png"
ls -1 "$OUT"

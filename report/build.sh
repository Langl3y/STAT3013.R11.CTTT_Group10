#!/bin/sh
# Build the full report: Markdown content -> DOCX (course template) -> refreshed DOCX + PDF.
# Requires the project venv (python-docx) and LibreOffice (brew install --cask libreoffice).
set -e
cd "$(dirname "$0")/.."
.venv/bin/python report/build_report.py
report/finalize_report.sh report/out/FullReport.docx report/out/FullReport_final.docx report/out/FullReport.pdf 2>/dev/null
echo "PDF:  report/out/FullReport.pdf"
echo "DOCX: report/out/FullReport_final.docx (editable, TOC refreshed)"

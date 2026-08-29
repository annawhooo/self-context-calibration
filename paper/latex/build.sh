#!/bin/sh
# Build the INTERCEPT submission PDF. IEEEtran.cls and IEEEtran.bst
# are vendored in this directory, so any TeX Live with pdflatex and
# bibtex suffices. Output: main.pdf (page budget: 4 to 6).
set -e
cd "$(dirname "$0")"
pdflatex -interaction=nonstopmode main.tex >/dev/null || { tail -40 main.log; exit 1; }
bibtex main || true
pdflatex -interaction=nonstopmode main.tex >/dev/null || { tail -40 main.log; exit 1; }
pdflatex -interaction=nonstopmode main.tex >/dev/null || { tail -40 main.log; exit 1; }
grep -E "^Output written" main.log
grep -iE "warning.*(undefined|multiply)" main.log || true

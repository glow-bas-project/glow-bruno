#!/usr/bin/env bash
# One-time repo setup: git clean filter (sanitize on git add) + pre-commit hooks.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

if command -v python3 >/dev/null 2>&1; then
  PY=python3
elif command -v python >/dev/null 2>&1; then
  PY=python
else
  echo "Python 3 is required." >&2
  exit 1
fi

# Quote for git config; works on macOS, Linux, and Git Bash on Windows.
FILTER_CMD="$PY \"$ROOT/.githooks/sanitize-filter.py\""
git config --local filter.sanitize-bruno-yaml.clean "$FILTER_CMD"
git config --local filter.sanitize-bruno-yaml.smudge cat
git config --local filter.sanitize-bruno-yaml.required true

# Re-apply filter to any files already tracked or staged.
git add --renormalize collections/glow 2>/dev/null || true

if command -v pre-commit >/dev/null 2>&1; then
  pre-commit install --install-hooks
else
  echo "Note: install pre-commit for gitleaks (brew install pre-commit / pip install pre-commit)." >&2
fi

echo "Done. Personal data in collection YAML is stripped on git add; your local files stay unchanged."

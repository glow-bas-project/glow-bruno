#!/usr/bin/env bash
# Fail commit if git sanitize filter was not installed after clone.
set -euo pipefail
if git config --local --get filter.sanitize-bruno-yaml.clean >/dev/null 2>&1; then
  exit 0
fi
echo "Git sanitize filter is not installed for this repo." >&2
echo "Run once after clone: ./.githooks/install.sh" >&2
exit 1

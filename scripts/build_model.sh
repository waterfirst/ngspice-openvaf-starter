#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
: "${OPENVAF_BIN:=openvaf}"
mkdir -p "$ROOT/build"
"$OPENVAF_BIN" --output "$ROOT/build/ohmic.osdi" "$ROOT/models/ohmic.va"
test -s "$ROOT/build/ohmic.osdi"
echo "Built: $ROOT/build/ohmic.osdi"

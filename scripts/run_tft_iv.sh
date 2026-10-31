#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
mkdir -p "$ROOT/build" "$ROOT/results"
"${OPENVAF_BIN:-openvaf}" -o "$ROOT/build/tft.osdi" "$ROOT/models/tft.va"
python3 "$ROOT/circuits/tft_iv.py"

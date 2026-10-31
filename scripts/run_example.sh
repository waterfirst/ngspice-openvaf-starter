#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
: "${NGSPICE_BIN:=ngspice}"
bash "$ROOT/scripts/build_model.sh"
mkdir -p "$ROOT/results"
"$NGSPICE_BIN" -b "$ROOT/circuits/ohmic_divider.cir" | tee "$ROOT/results/ohmic_divider.log"
grep -Eq 'v\(out\)[[:space:]]*=[[:space:]]*5\.000000e-01' "$ROOT/results/ohmic_divider.log"
echo "PASS: V(out) = 0.5 V"

#!/usr/bin/env python3
"""Run first-use transfer-curve checks for the bundled PMOS and NMOS cards."""
from pathlib import Path
import json
import os
import subprocess
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results"
CARDS = json.loads((ROOT / "models" / "tft_cards.json").read_text())


def model_line(name, card):
    values = {**card, "W": 20e-6, "L": 4e-6, "COV": 3e-10}
    return ".model %s tft %s" % (name, " ".join(
        f"{key}={value:.8g}" for key, value in values.items() if key != "description"))


def netlist(kind, card):
    # NMOS: source=0 V, Vg 0→4 V. PMOS: source=+5 V, Vg +5→+1 V.
    if kind == "pmos":
        bias = ["Vd d 0 0", "Vs s 0 5", "Vg g 0 5"]
        sweep = "dc Vg 5 1 -0.1"
        current = "i(Vs)"
    else:
        bias = ["Vd d 0 5", "Vg g 0 0"]
        sweep = "dc Vg 0 4 0.1"
        current = "i(Vd)"
    return "\n".join([
        f"* {kind.upper()} TFT transfer curve — bundled educational card",
        model_line(f"{kind}_card", card),
        *bias, f"N1 d g {'s' if kind == 'pmos' else '0'} {kind}_card",
        ".control", "set noaskquit", "pre_osdi build/tft.osdi",
        sweep, "set wr_singlescale", "set wr_vecnames",
        f"wrdata results/{kind}_iv.dat v(g) {current}", ".endc", ".end", ""
    ])


def run(kind, card):
    cir = OUT / f"{kind}_iv.cir"
    cir.write_text(netlist(kind, card))
    proc = subprocess.run([os.environ.get("NGSPICE_BIN", "ngspice"), "-b", str(cir)],
                          cwd=ROOT, capture_output=True, text=True)
    (OUT / f"{kind}_iv.log").write_text(proc.stdout + proc.stderr)
    if proc.returncode:
        print(proc.stdout + proc.stderr, file=sys.stderr)
        raise SystemExit(proc.returncode)
    values = np.loadtxt(OUT / f"{kind}_iv.dat", skiprows=1)
    current = np.abs(values[:, 2])
    return float(current[0]), float(current[-1])


def main():
    OUT.mkdir(exist_ok=True)
    results = {
        "NMOS": run("nmos", CARDS["oxide_nmos_25c"]),
        "PMOS": run("pmos", CARDS["ltps_pmos_25c"]),
    }
    ok = True
    for name, (ioff, ion) in results.items():
        passed = ion > 100 * max(ioff, 1e-15)
        ok &= passed
        print(f"{name}: |Id| at sweep start = {ioff:.3e} A, at sweep end = {ion:.3e} A — {'PASS' if passed else 'FAIL'}")
    if not ok:
        raise SystemExit("FAIL: expected at least 100× on/off current ratio")
    print("PASS: bundled PMOS and NMOS TFT cards passed the first I–V check")


if __name__ == "__main__":
    main()

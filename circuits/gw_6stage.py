#!/usr/bin/env python3
"""Run a six-stage educational oxide-NMOS gate-waveform (GW) chain.

The circuit is inspired by the latch-and-transmission-gate topology in
KR20170071217A Fig. 3.  It is an educational topology exercise; it is not a
copy of the JSID blocking-structure circuit.
"""
from pathlib import Path
import os
import subprocess
import sys
import json
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results"
N = 6
VGH, VGL = 8.0, -8.0
SLOT, PW, EDGE, T0 = 5e-6, 4e-6, 50e-9, 10e-6
SIZES = {"M1": 6, "M2": 24, "M3": 6, "M4": 24, "M5": 120,
         "M6": 60, "M7": 20, "M8": 200, "M9": 1200, "M10": 900}
CARD = json.loads((ROOT / "models" / "tft_cards.json").read_text())["oxide_nmos_25c"]


def pwl(points):
    return "PWL(" + " ".join(f"{t:.9g} {v:g}" for t, v in sorted(points)) + ")"


def slot(k):
    return T0 + k * SLOT + (SLOT - PW) / 2


def model_lines(dvth):
    lines = [f"* synthetic oxide-NMOS card; dVth={dvth:+.3f} V"]
    for name, width in SIZES.items():
        card = {**CARD, "VTH": CARD["VTH"] + dvth, "W": width * 1e-6,
                "L": 4e-6, "COV": 3e-10}
        lines.append(".model t%s tft %s" % (name, " ".join(
            f"{key}={value:.8g}" for key, value in card.items() if key != "description")))
    return lines


def stage_lines():
    return [
        ".subckt gw_stage gpre gpost cka ckb out vgh vgl rst",
        "* Ratioed NMOS latch plus output transmission path",
        "NM1 qb vgh vgh tM1", "NM2 qb q vgl tM2",
        "NM3 q vgh rst tM3", "NM4 q qb vgl tM4",
        "NM5 qb gpre x tM5", "NM6 q gpost x tM6", "NM7 x cka vgl tM7",
        "NM8 out qb ckb tM8", "NM9 ckb q out tM9", "NM10 out qb vgl tM10",
        ".ends gw_stage",
    ]


def build(dvth):
    cka, ckb, vst = [(0, VGL)], [(0, VGL)], [(0, VGL)]
    for k in range(2 * N + 4):
        t = slot(k)
        target = cka if k % 2 == 0 else ckb
        target += [(t, VGL), (t + EDGE, VGH), (t + PW, VGH), (t + PW + EDGE, VGL)]
    t = slot(0)
    vst += [(t, VGL), (t + EDGE, VGH), (t + PW, VGH), (t + PW + EDGE, VGL)]
    td = slot(N + 1)
    dmy = [(0, VGL), (td, VGL), (td + EDGE, VGH), (td + PW, VGH), (td + PW + EDGE, VGL)]
    lines = ["* Six-stage educational GW pulse chain", *model_lines(dvth), *stage_lines(),
             f"Vvgh vgh 0 {VGH}", f"Vvgl vgl 0 {VGL}",
             f"Vcka cka 0 {pwl(cka)}", f"Vckb ckb 0 {pwl(ckb)}",
             f"Vvst vst 0 {pwl(vst)}", f"Vrst rst 0 {VGH}", f"Vdmy dmy 0 {pwl(dmy)}"]
    for i in range(1, N + 1):
        pre = "vst" if i == 1 else f"out{i - 1}"
        post = "dmy" if i == N else f"out{i + 1}"
        clocks = ("cka", "ckb") if i % 2 else ("ckb", "cka")
        lines.append(f"X{i} {pre} {post} {clocks[0]} {clocks[1]} out{i} vgh vgl rst gw_stage")
    lines.append("Cdummy dmy 0 20p")
    ic = " ".join(f"v(x{i}.q)={VGL} v(x{i}.qb)={VGH} v(out{i})={VGL}" for i in range(1, N + 1))
    vectors = " ".join(f"v(out{i})" for i in range(1, N + 1))
    lines += [f".ic {ic}", ".options method=gear reltol=1e-4 abstol=1e-12 vntol=1e-6 gmin=1e-12",
              ".control", "set noaskquit", "pre_osdi build/tft.osdi",
              f"tran 10n {slot(2 * N + 3) + 2e-6:.9g} 0 20n uic",
              "set wr_singlescale", "set wr_vecnames",
              f"wrdata results/gw_6stage.dat v(vst) v(cka) v(ckb) {vectors}", ".endc", ".end"]
    return "\n".join(lines) + "\n"


def pulse_count(time, value):
    mid = 0.0
    rises = np.where((value[:-1] < mid) & (value[1:] >= mid))[0]
    falls = np.where((value[:-1] >= mid) & (value[1:] < mid))[0]
    return [(time[a], time[falls[falls > a][0]]) for a in rises if np.any(falls > a)]


def evaluate(data):
    time = data[:, 0]
    verdict = []
    for i in range(N):
        pulses = pulse_count(time, data[:, 4 + i])
        expected = (T0 + (i + 1) * SLOT, T0 + (i + 2) * SLOT)
        good = [p for p in pulses if p[0] > expected[0] - 0.2 * SLOT and p[1] < expected[1] + 0.5 * SLOT]
        verdict.append(len(good) == 1 and len(pulses) == 1)
    return verdict


def main():
    dvth = float(sys.argv[1]) if len(sys.argv) > 1 else 0.0
    OUT.mkdir(exist_ok=True)
    (OUT / "gw_6stage.cir").write_text(build(dvth))
    command = [os.environ.get("NGSPICE_BIN", "ngspice"), "-b", str(OUT / "gw_6stage.cir")]
    run = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
    (OUT / "gw_6stage.log").write_text(run.stdout + run.stderr)
    if run.returncode:
        print(run.stdout + run.stderr, file=sys.stderr)
        raise SystemExit(run.returncode)
    result = evaluate(np.loadtxt(OUT / "gw_6stage.dat", skiprows=1))
    print("GW slot test:", ["PASS" if x else "FAIL" for x in result])
    if result != [True] * N:
        raise SystemExit("FAIL: expected exactly one pulse in each OUT1..OUT6 slot")
    print("PASS: six one-hot GW pulses reproduced with the synthetic NMOS model")


if __name__ == "__main__":
    main()

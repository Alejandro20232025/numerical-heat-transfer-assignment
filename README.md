# Numerical Methods in Heat Transfer — Problem 5-35 and a Forced-Air-Cooled Adaptation

|||
|-|-|
|Course|INQU 4001|
|Instructor|Prof. Camilo Mora Navarro |
|Students|Adrian Cupeles Belen · Alejandro Fortuno Santiago |
|Submission|\[26/oct/2026] — video link: \[URL]|

## Summary

**Base exercise (textbook Problem 5-35).** An ASME SB-96 copper–silicon plate (30 mm, k = 36 W/m·K) under a stainless steel plate (10 mm, k = 13 W/m·K). A uniform heat flux of 750 W/m² enters the bottom; the top loses heat to 20 °C air and surroundings with h\_comb = 7.76 W/m²·K. Finite differences with Δx = 5 mm (nodes 0–8).

|Result|Original (h\_comb = 7.76)|Adapted (h\_comb = 40)|
|-|-|-|
|Hottest SB-96 temperature T0|117.85 °C — **not compliant** (limit 93 °C, ASME BPVC.IV-2015 HF-300)|39.95 °C — compliant, 53 °C margin|
|Highest allowable heat flux|559.5 W/m²|2744.1 W/m² (+390 %)|
|Cooldown 93 → 40 °C (explicit FD, hottest point)|22,928 s = 6.37 h|4,575 s = 1.27 h (−80.0 %, 5.0× faster)|

**Adaptation.** Fan-forced 20 °C air plus a high-emissivity coating on the steel surface raise h\_comb from 7.76 to 40 W/m²·K. The surface resistance is 98.8 % of the total, so this is the only effective, code-neutral lever (see the sensitivity study in `03\\\_numerical/results/sensitivity.csv`).

## Repository structure

```
heat-transfer-fdm-5-35/
├── README.md
├── 01\\\_original\\\_problem/
│   ├── problem\\\_statement.md        restated problem, data, results
│   
├── 02\\\_adapted\\\_problem/
│   ├── adapted\\\_problem\\\_statement.md
│  
├── 03\\\_numerical/
│   ├── fdm\\\_5\\\_35.py                 finite difference solver (steady + transient)
│   ├── requirements.txt
│   ├── results/                    run\\\_log.txt and CSV tables (generated)
│   └── figures/                    PNG figures used in the report (generated)
├── 04\\\_audit/
│   ├── audit\\\_checklist.md          22 hand checks, initialled by each student
│   └── ai\\\_error\\\_log.md             AI errors found and how they were corrected
├── 05\\\_presentation/
│   └── slide\\\_outline.md            11 slides, speaker notes, timing (13:45)
└── prompts/
    ├── prompt\\\_log.md               index of every prompt and AI output
    ├── templates/                  prompt templates downloaded from the class GitHub
    ├── 01\\\_base\\\_and\\\_adapted\\\_prompt.md
    └── 02\\\_audit\\\_prompt.md          suggested follow-up prompt (run and log it)
```

## How to reproduce the numbers

```bash
pip install -r 03\\\_numerical/requirements.txt
python 03\\\_numerical/fdm\\\_5\\\_35.py
```

The script prints every node temperature, the Thomas-algorithm sweep, residuals, flux and energy checks, and the transient results, and writes `results/run\\\_log.txt`, eight CSV tables and five figures. Runtime is a few seconds.

## Verification summary

* Steady state: numpy solve, Thomas algorithm and the exact resistance network agree to 4 × 10⁻¹² °C; every interval carries 750.000 W/m²; the energy balance closes.
* Transient: explicit FD (Δt = 1 s, stable since τ₁ = 0.448 ≤ 0.5) agrees with Crank–Nicolson and a 2.5-mm grid within 0.02 %, and with lumped capacitance (Bi = 0.012 and 0.064) and the one-term series within 3.4 %.
* Manual audit: see `04\\\_audit/`. Hand-signed report: see the submitted PDF.

## AI workflow

1. Prompt templates downloaded from the class GitHub → `prompts/templates/`.
2. Each prompt and the full AI output are saved as numbered files in `prompts/` and indexed in `prompts/prompt\\\_log.md`.
3. AI output was audited by hand (`04\\\_audit/audit\\\_checklist.md`); every correction is recorded in `04\\\_audit/ai\\\_error\\\_log.md`.
4. The code was run locally and its output compared with the hand calculations before the report was signed.

## Material data sources (transient analysis only)

* C65500 (ASME SB-96): ρ = 8530 kg/m³, c = 377 J/kg·K, k = 36 W/m·K — Wieland Diversified, "Bronze CDA 65500" data sheet.
* 904L stainless steel: ρ = 8000 kg/m³, c = 500 J/kg·K, k = 13.0 W/m·K — Atlas Steels, "Stainless Steel 904L Grade Data Sheet", rev. 27 Apr 2021.


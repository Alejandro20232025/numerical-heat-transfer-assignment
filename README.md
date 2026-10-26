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


* C65500 (ASME SB-96): ρ = 8530 kg/m³, c = 377 J/kg·K, k = 36 W/m·K — Wieland Diversified, "Bronze CDA 65500" data sheet.
* 904L stainless steel: ρ = 8000 kg/m³, c = 500 J/kg·K, k = 13.0 W/m·K — Atlas Steels, "Stainless Steel 904L Grade Data Sheet", rev. 27 Apr 2021.


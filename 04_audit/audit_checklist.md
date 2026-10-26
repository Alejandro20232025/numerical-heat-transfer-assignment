# Manual audit checklist

Recompute each row on paper with a calculator. Initial the row only after your own result matches. Scan the pages into `01_original_problem/hand_calculations/` and `02_adapted_problem/hand_calculations/`.

| # | Item | Value in report | Independent check | Expected | Student 1 | Student 2 |
|---|---|---|---|---|---|---|
| 1 | Grid fits both plates | 6 + 2 intervals | 30/5 and 10/5 | 6 and 2 |ACB|AFS|
| 2 | q0·Δx/k1 | 0.1041667 °C | 750 × 0.005 / 36 | 0.1041667 |ACB|AFS|
| 3 | q0·Δx/k2 | 0.2884615 °C | 750 × 0.005 / 13 | 0.2884615 |ACB|AFS|
| 4 | h·Δx/k2, original | 0.0029846 | 7.76 × 0.005 / 13 | 0.0029846 |ACB|AFS|
| 5 | Interface coefficients | 36, −49, 13 | k1, −(k1 + k2), k2 | 36, −49, 13 |ACB|AFS|
| 6 | T8, original | 116.649 °C | 20 + 750/7.76 | 116.649 |ACB|AFS|
| 7 | T6, original | 117.226 °C | T8 + 750 × 0.01/13 | 117.226 |ACB|AFS|
| 8 | T0, original | 117.851 °C | T6 + 750 × 0.03/36 | 117.851 |ACB|AFS|
| 9 | Interface flux continuity | 750 = 750 W/m² | 36 × 0.104167/0.005 ; 13 × 0.288462/0.005 | 750.0 ; 750.0 |ACB|AFS|
| 10 | Energy balance, original | 750 W/m² | 7.76 × (116.649 − 20) | 750.0 |ACB|AFS|
| 11 | q0,max, original | 559.5 W/m² | 73 / 0.1304685 | 559.5 |ACB|AFS|
| 12 | Minimum h_comb | 10.45 W/m²·K | 1 / (73/750 − 0.0016026) | 10.446 |ACB|AFS|
| 13 | T8 and T0, adapted | 38.750 ; 39.952 °C | 20 + 750/40 ; + 0.577 + 0.625 | 38.750 ; 39.952 |ACB|AFS|
| 14 | q0,max, adapted | 2744.1 W/m² | 73 / (0.025 + 0.0016026) | 2744.1 |ACB|AFS|
| 15 | Biot numbers | 0.0124 ; 0.0641 | 7.76 × 0.0016026 ; 40 × 0.0016026 | 0.0124 ; 0.0641 |ACB|AFS|
| 16 | Wall heat capacity C'' | 136,474 J/m²·K | 8530 × 377 × 0.03 + 8000 × 500 × 0.01 | 136,474 |ACB|AFS|
| 17 | Time constants C''/h | 17,587 s ; 3,412 s | 136,474/7.76 ; 136,474/40 | 17,587 ; 3,412 |ACB|AFS|
| 18 | Mesh Fourier number τ1 | 0.4478 ≤ 0.5 | (36/3,215,810) × 1 / 0.005² | 0.4478 |ACB|AFS|
| 19 | First explicit step, T8 at 1 s | 92.943352 °C | 93 − 0.26 × 0.0029846 × 73 | 92.943352 |ACB|AFS|
| 20 | One-term root, original | λ1 = 0.11129 | 0.11129 × tan(0.11129) | 0.012436 = Bi |ACB|AFS|
| 21 | One-term validity | Fo = 104.7 ; 20.8 | requires Fo > 0.2 | both > 0.2 |ACB|AFS|
| 22 | Cooldown improvement | 80.0 % | (22,927.7 − 4,575.0) / 22,927.7 | 0.8005 |ACB|AFS|


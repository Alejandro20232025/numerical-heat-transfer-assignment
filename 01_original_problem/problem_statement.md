# Problem 5-35 — original (base) exercise

Source: heat transfer textbook, Chapter 5 "Numerical Methods in Heat Conduction", p. 369, as reproduced in the course packet 092126. Paste the screenshot of the original statement and Figure P5-35 here if the instructor requires the verbatim wording.

## Restated problem

A plane wall consists of a 3-cm ASME SB-96 copper–silicon plate (k = 36 W/m·K) at the bottom and a 1-cm stainless steel plate (k = 13 W/m·K) on top. A uniform heat flux of 750 W/m² enters the bottom face (surface 1). The top face (surface 2) loses heat by convection to air at 20 °C and by radiation to surroundings at 20 °C, combined into h_comb = 7.76 W/m²·K. ASME BPVC.IV-2015, HF-300 limits SB-96 equipment to 93 °C. Using finite differences with Δx = 5 mm, find (a) the temperature at each node, (b) whether the SB-96 plate complies with the code, and (c) the highest bottom heat flux that keeps the SB-96 plate below 93 °C.

## Given data

| Quantity | Symbol | Value |
|---|---|---|
| Cu–Si (SB-96) conductivity, thickness | k1, L1 | 36 W/m·K, 0.030 m |
| Stainless steel conductivity, thickness | k2, L2 | 13 W/m·K, 0.010 m |
| Heat flux into surface 1 | q0 | 750 W/m² |
| Air and surroundings | T∞ = Tsurr | 20 °C |
| Combined coefficient | h_comb | 7.76 W/m²·K |
| Code limit for SB-96 | T_allow | 93 °C |
| Nodal spacing; nodes | Δx | 0.005 m; nodes 0–8 (node 6 = interface) |

## Node equations

| Node | Equation |
|---|---|
| 0 | −T0 + T1 = −0.1041667 |
| 1–5 | T(m−1) − 2T(m) + T(m+1) = 0 |
| 6 | 36 T5 − 49 T6 + 13 T7 = 0 |
| 7 | T6 − 2 T7 + T8 = 0 |
| 8 | T7 − 1.0029846 T8 = −0.0596923 |

## Results

| Node | x (mm) | T (°C) |
|---|---|---|
| 0 | 0 | 117.851 |
| 1 | 5 | 117.747 |
| 2 | 10 | 117.643 |
| 3 | 15 | 117.539 |
| 4 | 20 | 117.435 |
| 5 | 25 | 117.331 |
| 6 | 30 | 117.226 |
| 7 | 35 | 116.938 |
| 8 | 40 | 116.649 |

- Hottest SB-96 temperature 117.85 °C > 93 °C → **not compliant**.
- Highest allowable heat flux: q0,max = (93 − 20)/0.1304685 = 559.5 W/m².
- Energy balance: h_comb (T8 − T∞) = 7.76 × 96.6495 = 750.0 W/m² = q0.

Hand calculations: `hand_calculations/` (students: scan your Thomas sweep and checks here).

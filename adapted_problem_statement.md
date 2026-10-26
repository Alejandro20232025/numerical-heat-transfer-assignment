# Problem 5-35A — adapted exercise (forced-air cooling)

## Statement

The wall of Problem 5-35 is unchanged: a 3-cm ASME SB-96 Cu–Si plate (k = 36 W/m·K, ρ = 8530 kg/m³, c = 377 J/kg·K) under a 1-cm stainless steel plate (k = 13 W/m·K, ρ = 8000 kg/m³, c = 500 J/kg·K), heated by 750 W/m² at surface 1. To cool it faster, surface 2 is coated with a high-emissivity paint (ε ≈ 0.9) and cooled by a fan blowing 20 °C air, with surroundings also at 20 °C, giving h_comb = 40 W/m²·K.

(a) Using finite differences with Δx = 5 mm, find the steady temperature at each node, check the 93 °C limit of ASME BPVC.IV-2015 HF-300, and find the highest allowable heat flux.

(b) The heat flux is switched off when the wall is at a uniform 93 °C and surface 1 becomes adiabatic. Using the explicit finite difference method, find the time for the hottest point of the SB-96 plate to reach 40 °C, and compare it with the original design.

## Modified and unchanged parameters

| Parameter | Original | Adapted |
|---|---|---|
| h_comb (W/m²·K) | 7.76 | **40** |
| k1 / k2 (W/m·K), L1 / L2 (mm) | 36 / 13, 30 / 10 | unchanged |
| q0 (W/m²), T∞ = Tsurr (°C) | 750, 20 | unchanged |
| Code limit, Δx | 93 °C, 5 mm | unchanged |

## Why this change (design reasoning)

- Surface resistance 1/h_comb = 0.1289 of 0.1305 m²·K/W (98.8 %) → it controls both the temperature level and the cooling time.
- Doubling k1 or k2 changes T0 by less than 0.32 °C; halving plate thickness speeds cooling but conflicts with pressure design.
- Forced convection of gases is typically 25–250 W/m²·K; a high-ε coating alone adds 5.7–7.4 W/m²·K of radiation between 40 and 93 °C.
- Bi = h_comb (L1/k1 + L2/k2) = 0.064 < 0.1 → the wall still cools almost uniformly.

## Results

| Node | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|---|
| T (°C) | 39.952 | 39.848 | 39.744 | 39.639 | 39.535 | 39.431 | 39.327 | 39.038 | 38.750 |

- Compliant: 39.95 °C ≤ 93 °C (53.05 °C margin). Highest allowable heat flux 2744.1 W/m².
- Cooldown 93 → 40 °C (explicit FD, Δt = 1 s): 4,575 s = 1.27 h, versus 22,928 s = 6.37 h originally → 80.0 % less time.
- Checks: Crank–Nicolson 4,575.6 s; 2.5-mm grid 4,575.5 s; lumped 4,417 s; one-term 4,548 s.



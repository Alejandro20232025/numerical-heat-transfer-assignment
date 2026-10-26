# AI error log

Every error found in AI output, how it was detected, and the correction. Rows 1–5 were found and fixed while the AI (Claude) drafted the solution and cross-checked it; add your own rows for anything you find during the manual audit or in other AI tools.

| # | Date | Tool | Where | What the AI produced | Why it was wrong | How it was detected | Correction |
|---|---|---|---|---|---|---|---|
| 1 | 2026-10-26 | Claude | Code, sensitivity study | Explicit run with Δt = 1 s for k1 = 72 W/m·K | Doubling k1 doubles α1, so the stable limit drops to 0.558 s | The code's stability check raised an error | Δt = min(1 s, 0.9 Δt_crit) for each case |
| 2 | 2026-10-26 | Claude | Report §9.4 | β given in m²·K/W | β = 2Δt / [(ρ1c1 + ρ2c2) Δx²] has units m·K/W so that βk is dimensionless | Unit check | Units corrected |
| 3 | 2026-10-26 | Claude | Report §9.4 | "Halving Δt (Crank–Nicolson)" | The Crank–Nicolson check used a larger step (10 s) | Compared text with the code | Reworded to the checks actually run |
| 4 | 2026-10-26 | Claude | Report §12 | Conduction-limited cooldown of 2.3 min (one-term series, equivalent homogeneous wall) | At Bi → ∞ the layer arrangement matters | Re-ran the composite FD with h = 10⁵ W/m²·K | Replaced by 2.7 min |
| 5 | 2026-10-26 | Claude | Report §7.3 | Rounding example quoted as T8 = 116.05 °C | Depends on whether the right-hand side is rounded too | Recomputed both ways | Stated as 116.05–116.15 °C |
| 6 | | | | | | | |
| 7 | | | | | | | |

## Traps to check in any AI output (Fourier numbers, Heisler charts, lumped capacitance)

- Characteristic length: only one face is cooled, so L_c = V/A_s = L = 40 mm, not L/2.
- Biot number of a composite wall: Bi = h (L1/k1 + L2/k2), not h L / k of one material.
- Lumped capacitance is valid when Bi < 0.1 — check it; "it is metal" is not a reason.
- Heisler charts assume a homogeneous wall; they cannot be read accurately at 1/Bi ≈ 80.
- The one-term series needs Fo = αt/L² > 0.2.
- The mesh Fourier number τ = αΔt/Δx² is a stability parameter, not the physical Fourier number.
- Explicit stability: interior τ ≤ 0.5, convection node τ(1 + hΔx/k) ≤ 0.5, interface node β(k1 + k2) ≤ 1.
- "Reaches equilibrium faster because the final temperature is lower" is not a valid speed comparison; compare the time between the same two temperatures.

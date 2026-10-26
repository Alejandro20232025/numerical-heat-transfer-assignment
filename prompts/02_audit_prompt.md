# Prompt 02 — independent audit (suggested; run it, then save the output as 02_output.md)

Use a fresh chat, ideally a different tool (for example Gemini) so the audit is independent. Paste Sections 6, 7, 9 and 13 of our report after the prompt.

---

Act as a strict heat-transfer teaching assistant grading a finite difference solution. Do not trust any number in the attached work: recompute everything yourself and show each substitution.

Problem: two-layer plane wall, ASME SB-96 Cu–Si plate (k1 = 36 W/m·K, L1 = 30 mm) under stainless steel (k2 = 13 W/m·K, L2 = 10 mm). Uniform heat flux 750 W/m² into the bottom face; top face combined convection–radiation h_comb to 20 °C. Δx = 5 mm, nodes 0–8, node 6 at the interface. Original h_comb = 7.76 W/m²·K; adapted h_comb = 40 W/m²·K.

Tasks:
1. Derive the energy-balance equation of every node (heat-flux node, interior nodes, interface node, convection node) and compare with ours.
2. Solve the nine equations for both designs with the Thomas algorithm, showing c′ and d′ at every step, and compare with ours to 0.001 °C.
3. Check interface flux continuity, the overall energy balance, and the units of every coefficient.
4. Recompute the highest allowable heat flux for a 93 °C limit and the minimum h_comb for compliance at 750 W/m².
5. For the cooldown test (uniform 93 °C, heat flux off, bottom adiabatic, target 40 °C; ρ1 = 8530 kg/m³, c1 = 377 J/kg·K, ρ2 = 8000 kg/m³, c2 = 500 J/kg·K): compute the Biot number with the correct characteristic length, state whether lumped capacitance is valid, check the explicit stability limit for every node type with Δt = 1 s, compute the first two explicit time steps, and estimate the cooldown time by lumped capacitance and by the one-term series (check Fo > 0.2).
6. List every disagreement with our work as: location, our value, your value, which one is right and why. Flag any use of Heisler charts, Fourier numbers or lumped capacitance outside their validity limits.

Report numbers with units and at least four significant figures.

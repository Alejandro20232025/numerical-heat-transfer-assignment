# Prompt 03 — adapted exercise from scratch (suggested; run it, then save the output as 03_output.md)

Run this without showing the AI our answers, then compare its results with Section 9 of the report and log any difference in 04_audit/ai_error_log.md.

---

Act as an entry-level thermal engineer. Solve the following problem completely, showing every equation and substitution, in SI units.

A plane wall consists of a 3-cm ASME SB-96 copper–silicon plate (k = 36 W/m·K, ρ = 8530 kg/m³, c = 377 J/kg·K) at the bottom and a 1-cm stainless steel plate (k = 13 W/m·K, ρ = 8000 kg/m³, c = 500 J/kg·K) on top. A uniform heat flux of 750 W/m² enters the bottom surface. The top surface is coated with a high-emissivity paint and cooled by a fan blowing 20 °C air, with surroundings at 20 °C; the combined convection–radiation coefficient is 40 W/m²·K. ASME BPVC.IV-2015, HF-300 limits SB-96 equipment to 93 °C.

(a) Using the finite difference energy-balance method with Δx = 5 mm (nodes 0–8, node 6 at the interface), write every node equation, solve the system, and give the temperature at each node.
(b) Check interface flux continuity and the overall energy balance.
(c) State whether the SB-96 plate complies with the code, and find the highest heat flux for which it stays at or below 93 °C.
(d) The heat flux is switched off when the wall is at a uniform 93 °C, and the bottom becomes adiabatic. Compute the Biot number (state the characteristic length you use and why), decide whether lumped capacitance is valid, and find the time for the hottest point of the SB-96 plate to reach 40 °C using the explicit finite difference method. State the stability limit you used for each node type.
(e) Repeat (d) with h = 7.76 W/m²·K and report the percentage reduction in cooling time.

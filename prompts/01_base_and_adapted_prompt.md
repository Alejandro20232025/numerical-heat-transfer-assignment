# Prompt 01 — base exercise and adapted version (as sent to Claude, 2026-10-26)

Attached with this prompt: three screenshots of the assignment overview, rubric, and Heat Conduction Bank (pp. 368–369). Save them in this folder as 01_attachments_*.png.

---

Act as an expert in Numerical Methods in Heat Transfer, Heat Conduction, Finite Difference Methods, and Engineering Problem Solving. I am an engineering student working on a project titled “Numerical Methods in Heat Transfer.”

I have attached screenshots containing the professor’s assignment instructions, grading rubric, and the Heat Conduction Bank from a heat transfer textbook. Carefully read ALL the attached images before starting. Use the assignment instructions and grading rubric as the primary requirements.

1. Main objective

Select ONE appropriate base exercise from the attached Heat Conduction Bank and solve it completely. Then create a creatively adapted version of the same exercise that produces significantly faster heating or faster cooling while maintaining physically realistic conditions.

The assignment requires:

* A base heat transfer exercise.
* A creatively adapted version of the base exercise.
* Two exercises per group, including the original and the adapted version.
* Detailed prompts for solving both exercises.
* Numerical calculations and verification.
* A final technical report signed by both students.
* A video presentation of no more than 15 minutes.

Choose a problem that is suitable for a detailed numerical solution using the finite difference method. Prefer an exercise that is sufficiently challenging to demonstrate engineering knowledge but manageable enough to verify every calculation manually.

Potential exercises visible in the screenshots include Problems 5-33, 5-34, 5-35, 5-36, and other problems in the Heat Conduction Bank. Read the problem statements carefully and select the best option. Do not assume that these are the only available choices.

2. Base exercise solution

First, reproduce the complete original problem statement accurately from the attached images. If any numerical value, unit, or sentence is unreadable, explicitly identify the uncertainty rather than guessing.

Then solve the selected problem in English using the following structure:

1. Problem statement.
2. Given data, including all material properties, thermal conductivities, thicknesses, boundary conditions, heat fluxes, convection coefficients, ambient temperatures, and applicable temperature limits.
3. Required quantities.
4. Engineering assumptions.
5. Physical model and coordinate system.
6. Governing differential equation.
7. Derivation of the finite difference equations from the governing equation.
8. Interior-node equations.
9. Boundary-node equations, including convection, radiation, heat flux, or thermal contact resistance whenever applicable.
10. Interface equations for composite materials, if applicable.
11. Application of the boundary conditions.
12. Construction of the complete system of algebraic equations.
13. Numerical solution with every calculation shown.
14. Temperature at each node.
15. Temperature distribution through the material thickness.
16. Heat transfer rate or heat flux, as required.
17. Verification of energy conservation and numerical accuracy.
18. Engineering interpretation of the results.

Use consistent SI units unless the original problem specifically requires otherwise. Clearly identify every variable and its units.

Do not skip mathematical derivations or present unexplained final answers.

3. Create a creative thermal adaptation

After solving the original exercise, design a modified version that achieves significantly faster heating or cooling.

The modification must be physically meaningful, realistic, and supported by heat transfer theory. Consider changing one or more of the following parameters:

* Thermal conductivity.
* Material thickness.
* Convection heat transfer coefficient.
* Coolant or heating-fluid temperature.
* Heat flux.
* Surface emissivity, if radiation is relevant.
* Material arrangement or thermal resistance.

Choose the changes that best demonstrate a substantial improvement in heating or cooling performance.

Clearly explain:

* What was changed from the original problem.
* Why the change improves heat transfer.
* Which physical mechanism is responsible for the improvement.
* Why the modified conditions are realistic.
* Which parameters remain unchanged.
* How the adaptation affects the temperature distribution and heat transfer rate.

Do not change parameters arbitrarily or violate physical constraints, material properties, or the assumptions of the selected model.

4. Solve the adapted problem

Solve the modified exercise independently using the same level of detail as the original exercise.

Show:

* The modified problem statement.
* The complete list of modified and unchanged parameters.
* The governing equation and finite difference formulation.
* All node equations and boundary conditions.
* All numerical calculations.
* The temperature at every node.
* The resulting temperature distribution.
* The heat transfer rate or flux.
* The verification of energy conservation and numerical accuracy.

If the original problem is steady-state, do not claim that the system reaches equilibrium faster merely because its final temperature is different. Instead, compare appropriate steady-state performance measures, such as heat transfer rate and thermal resistance. If transient heating or cooling speed is the intended objective, establish an appropriate transient model and compare the time required to reach the same specified target temperature.

Clearly distinguish between steady-state and transient analysis.

5. Quantitative comparison

Create a comparison table containing:

* Original parameter values.
* Adapted parameter values.
* Original temperature results.
* Adapted temperature results.
* Original heat transfer rate or heat flux.
* Adapted heat transfer rate or heat flux.
* Percentage improvement in the selected performance metric.
* Any relevant material or operating temperature constraints.

Use the following formula when applicable:

Percentage improvement = [(Adapted performance − Original performance) / Original performance] × 100%.

Define the performance metric carefully. If a lower value represents better performance, such as cooling time, use a formula appropriate for that metric.

Explain the results in engineering terms and support the conclusions with calculated values.

6. Manual mathematical audit

The assignment requires a manual audit of all AI-generated calculations.

Therefore:

* Verify every equation and numerical substitution.
* Recalculate every node temperature independently where practical.
* Check units and significant figures.
* Verify boundary conditions.
* Check interface heat flux continuity when applicable.
* Check energy conservation.
* Identify common mistakes and possible numerical errors.
* Never invent textbook answers or claim that a calculation has been manually verified if it has not actually been checked.

Provide a separate audit section with the original calculations, independent verification, and corrected values, if necessary.

7. Engineering tools and reproducibility

Provide a detailed explanation of how to reproduce the work using GitHub and an AI tool such as Claude.

Include:

* Suggested GitHub repository structure.
* A README.md outline.
* A folder for the original problem and its calculations.
* A folder for the adapted problem.
* A folder for numerical calculations, tables, and graphs.
* A folder for audit documentation.
* A folder for presentation materials.

If a Python calculation is useful, provide complete, executable Python code that solves the finite difference equations, prints the temperature at every node, checks the residuals, and generates a temperature-versus-position graph. Explain the code and independently verify its numerical results.

Do not substitute code output for the required mathematical derivation and manual audit.

8. Final technical report

Prepare a professional engineering report in English with the following sections:

1. Title page with placeholders for both students’ names, course, instructor, and submission date.
2. Abstract.
3. Introduction.
4. Objectives.
5. Original problem statement.
6. Physical model and assumptions.
7. Governing equations.
8. Finite difference derivation.
9. Original problem solution.
10. Creative thermal adaptation.
11. Adapted problem solution.
12. Results and comparison tables.
13. Temperature distribution graphs.
14. Engineering discussion.
15. Manual mathematical audit.
16. Conclusions.
17. References.

Use clear technical English, properly formatted mathematical equations, and consistent units. Cite the textbook only when its title, edition, and other bibliographic information can be established from the provided material. Do not fabricate references.

Include a signature section for both students confirming that they reviewed and manually verified the calculations.

9. Presentation and video script

Prepare a presentation outline with approximately 10–12 slides that can be presented in no more than 15 minutes.

For each slide, provide:

* Slide title.
* Exact bullet points to display.
* Equations, tables, or graphs to include.
* Speaker notes.
* An estimated presentation duration.

Divide the speaking time fairly between both students.

The presentation must demonstrate the engineering workflow, the use of GitHub and AI tools, the original solution, the adapted solution, the numerical results, and the manual verification process.

Finish with a concise conclusion that explains the quantitative improvement achieved through the thermal adaptation.

10. Final quality requirements

Before presenting the final deliverables, check the work against the assignment rubric:

* Prompt engineering and thermal adaptation: 50%.
* Video presentation: 30%.
* Manual audit and hand-signed certification: 20%.

Prioritize a technically correct and well-verified solution over a superficially polished report.

Do not invent missing textbook data, calculations, citations, GitHub activity, signatures, or verification results. Clearly distinguish completed work from tasks that the students must perform themselves.

Start by identifying the selected textbook problem, explaining why it is the best choice, and listing its original data. Then proceed through the solution in the order specified above.
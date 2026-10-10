# Project TeX — Initial Skill Plan

Status: plan-only idea; not a skill, route, or active capability.

Current scope: design the problem-statement mode only. Learning-resource and
research-report modes remain pending separate review.

## Reference pattern

Primary reference:
`/Users/billabobz/phd/HO_purification/Non-unitary_Control_Qubit_HO.tex`

Learn the reference's scientific progression and equation/prose relationship.
Do not copy its project-specific physics, numerical values, macros, typos, or
notation collisions.

## Problem-statement mode

### Purpose

Produce a compact, mathematically precise statement of a research problem.
The document should contain enough prose to explain the physical meaning and
logic of the equations, but it should not become a tutorial, literature
review, or progress report.

The aim is carried by the title and opening sentence. The document then builds
the actual problem progressively rather than replacing it with an abstract
generic optimization template.

### Scientific progression

1. **Achievement and physical system**
   - State the desired achievement in the title and opening sentence.
   - Introduce the concrete physical system immediately.

2. **Governing dynamics and control**
   - Give the project-native Hamiltonian, equation of motion, or other
     governing dynamics.
   - Explain which terms describe the subsystems, interaction, drift, and
     control.
   - Identify what is fixed, controllable, uncertain, or derived.

3. **Initial states and resources**
   - Define the complete initial state.
   - Explain its components separately.
   - Define the parameters and the physical meaning of important limiting
     cases.
   - List alternative resource-state families when they are part of the
     problem.

4. **Target transformation**
   - State plainly what state, operation, observable, or physical effect is
     sought.
   - Express the target in the notation of the actual project.

5. **Success and resource costs**
   - Derive the target cost from the stated target.
   - Explain what exact success and nonzero error mean.
   - Introduce secondary costs only after the primary target cost.
   - Explain the physical tradeoff rather than hiding it inside an unexplained
     generic functional.
   - Keep objectives, penalties, constraints, and diagnostics distinct.

6. **Central research questions**
   - Ask direct questions that follow from the formulation: exact
     reachability, best achievable fidelity, required time, best control,
     resource dependence, and robustness when relevant.
   - Define qualitative terms such as "good" or "best" through the preceding
     metrics and constraints.

7. **Working mathematical route**
   - If an agreed method exists, give its operative chain and project
     equations, not only its name.
   - For an iterative control method, this may include the initial control,
     forward state, backward co-state, control update, and convergence test.
   - If an equation is said to follow from PMP, GRAPE, variational calculus,
     or another formulation, either show the compact derivation needed here or
     identify it as imported and point to the learning resource containing the
     derivation.

8. **Derived extensions when needed**
   - Keep extensions outside the canonical core problem.
   - Begin from the physical assumption that changes.
   - Derive the corresponding change in the state, dynamics, target, or cost.
   - State the new research question only after the modified mathematics is
     defined.

The reusable flow is:

\[
\begin{aligned}
&\text{achievement and physical system}\\
&\rightarrow\text{governing dynamics and control}\\
&\rightarrow\text{initial states and resources}\\
&\rightarrow\text{target transformation}\\
&\rightarrow\text{target and resource costs}\\
&\rightarrow\text{research questions}\\
&\rightarrow\text{working mathematical route}\\
&\rightarrow\text{derived extensions when needed}.
\end{aligned}
\]

### Equation and prose contract

- Let equations carry the scientific definition of the problem.
- Use short prose around them to explain physical meaning, assumptions, and
  logical connections.
- Define symbols locally before or beside their first use.
- Use project-native notation rather than forcing generic symbols.
- Derive any non-obvious relation required to make the formulation
  self-contained and unambiguous.
- Move long pedagogical derivations to the learning resource.
- Detect symbol collisions, inconsistent assumptions, and mismatches between
  the target and cost instead of reproducing them.
- Do not force a fixed number of headings; preserve the scientific progression
  even when the project needs a different visible section layout.

### Extension and Scout boundary

Scout findings may be proposed as candidate extensions, but they do not enter
the canonical problem merely because they are topically related. Before an
extension is admitted, map:

- the baseline equation;
- the changed equation;
- every changed symbol and assumption;
- the control, target, resource, or bath difference;
- the source or derivation supporting the change;
- its status as candidate, derived, source-supported, or verified.

### Document boundary

The problem statement should not contain:

- tutorial-level background;
- a broad literature review;
- research-progress results;
- unsupported numerical parameter choices;
- long derivations better suited to the learning resource;
- claims of applicability based only on topic similarity.

### Editing boundary

Treat an approved problem statement as a stable project authority. Inspect and
present a proposed change first. Edit only after explicit approval, preserve
unrelated content and preamble choices, and verify the resulting LaTeX before
claiming completion.

## Deferred work

Do not yet design or implement:

- the live skill folder or `SKILL.md`;
- registry or activation entries;
- Codex or Claude adapters;
- templates or scripts;
- learning-resource mode;
- research-report mode.

Those steps begin only after the user explicitly promotes this plan or approves
the next document-mode design.

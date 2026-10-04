# Productivity And Research Skills To Look Into

Status: idea-only backlog. This is not an active skill, has no `SKILL.md`, and is not registered with the orchestrator.

## Purpose

Collect skill ideas that could increase productivity for research, writing, coding, and daily context recovery. The emphasis is on workflows that preserve evidence, reduce repeated explanation, and make unfinished research easier to resume.

## Strong Candidates

1. Research trail and framing skill
   - Record assumptions, alternate framings, evidence gaps, belief updates, and rejected routes.
   - Best fit for early theoretical research where the reasoning path matters as much as the conclusion.

2. Paper evidence matrix skill
   - Convert paper notes into claim, source span, equation or method, confidence, and next-check rows.
   - Should avoid unsupported literature-review prose until local paper evidence is reviewed.

3. Experiment and notebook run ledger skill
   - Summarize objective, parameters, environment, result, artifact paths, failure mode, and next run.
   - Useful for BVP/PMP experiments, optimizer runs, notebooks, and generated plots.

4. Weekly research digest skill
   - Summarize what changed across chats, files, papers, equations, scripts, and unresolved questions.
   - Output should be short enough to actually read and explicit enough to restart work.

5. Citation and Zotero hygiene skill
   - Check citation keys, BibTeX entries, local PDFs, paper notes, and whether claims cite the right source.
   - Strong fit when moving from notes into article text.

6. File and artifact organizer skill
   - Rename and place PDFs, screenshots, notes, generated figures, and run outputs into stable folders.
   - Should create or update a manifest rather than silently moving important research material.

7. Learning and recall skill
   - Turn slow math notes into derivation checkpoints, active-recall cards, and "can I reproduce this?" prompts.
   - Best used for long-term retention, not immediate paper production.

## Lower Priority

- Calendar, email, and generic task automation.
- Broad deep-research skill without a strict source/evidence boundary.
- Large all-in-one "personal AI" skill that mixes retrieval, writing, scheduling, and coding.

## Design Notes

- Keep each skill small and independently triggerable.
- Prefer plan and review modes before write modes.
- Keep local-first and free-first options when possible.
- Separate candidate evidence from verified claims.
- Use deterministic scripts for repeated fragile work such as file manifests, run ledgers, citation checks, and paper-unit validation.
- Preserve manual activation for exploratory research skills so ordinary questions are not hijacked.

## Best First Build

Start with the experiment and notebook run ledger skill or the paper evidence matrix skill. Both have narrow inputs, obvious outputs, and immediate value for current research work.

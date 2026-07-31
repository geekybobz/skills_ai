---
title: Personalized Interaction Protocol Plan
type: todo-plan
status: proposed
topic: interaction-protocol
tags:
  - todo
  - interaction
  - personalization
  - protocol
  - token-efficiency
  - obsidian
depends_on:
  - "[[00_SKILLS_HUB]]"
  - "[[registry/compression]]"
  - "[[03_COMBO_MAP]]"
  - "[[04_RISK_MAP]]"
  - "[[05_COLOR_LAYERS]]"
---

# Personalized Interaction Protocol Plan

Back to [[README]] and [[00_SKILLS_HUB]].

## 1. Aim

Replace the current Caveman-centered interaction model with a personal,
professional, modular interaction protocol that:

1. reuses the reliable engineering already present in Caveman;
2. removes the Caveman name, character voice, and one-mode-for-everything model;
3. expresses the user's stable communication and research preferences once;
4. selects only the operation and domain guidance needed for the current task;
5. supports rigorous research, software, learning, writing, and design workflows;
6. preserves explicit review and write boundaries;
7. reduces total context and output tokens without removing necessary reasoning;
8. works consistently across Claude, Codex, Gemini, OpenCode, and OpenClaw;
9. remains understandable and navigable as an Obsidian graph; and
10. remains replaceable, testable, and maintainable as new needs are added.

The intended composition is:

```text
response
  = personal profile
  + task operation
  + domain overlay
  + permission and evidence policies
  + explicit user override
```

This is not a proposal for another persistent personality skill. It is a
protocol family whose components are selected just in time.

## 2. Scope And Non-Goals

### In scope

- Personal response contract and profile.
- Generic operations such as explain, derive, investigate, design, implement,
  review, and write.
- Specialized overlays for mathematics, quantum control, software, research
  notes, learning, career communication, web work, and AI-system design.
- Runtime state, routing, context selection, adapters, commands, and telemetry.
- Migration of useful Caveman behavior and utilities.
- Obsidian routing, backlinks, graph layers, and future extension rules.
- Evaluation of both token use and answer quality.

### Not in scope for the first implementation

- Building a general memory platform.
- Automatically writing durable user preferences from conversations.
- Rewriting unrelated skill families.
- Modifying research, code, Web_space, or AI-project repositories.
- Preserving Caveman branding as the final user-facing identity.
- Claiming a fixed percentage of token savings before measurement.

## 3. Inspection Method And Evidence Levels

This plan combines two evidence sources.

### A. Live repository evidence

Current files were inspected directly in:

- `/Users/billabobz/skills_ai`
- `/Users/billabobz/phd/CODES`
- `/Users/billabobz/phd/rob_unversal_article`
- `/Users/billabobz/OPTIMIZER_v3`
- `/Users/billabobz/Web_space`
- `/Users/billabobz/research_papers`
- `/Users/billabobz/TODO/ai_project`

Live files are authoritative for current structure and behavior.

### B. Memory and rollout evidence

The Codex memory registry and representative rollout summaries were inspected
for recurring preferences, successful workflows, failures, and corrections.
Memory is historical evidence, not proof of current filesystem state.

### Drift rule

When memory and the live repository disagree:

1. report the disagreement;
2. use the live repository for current-state claims;
3. use memory only to explain historical intent or user preference; and
4. never silently reconstruct missing artifacts from memory.

Observed example: memory records a substantial `paper_extract` design and
sample-unit workflow, but the live `/Users/billabobz/research_papers` currently
contains no `paper_extract/` directory or paper-unit folders. Its `README.md`
still links to those absent nodes. This confirms that current-state verification
must remain part of the protocol.

## 4. Summarized Scan Results

### 4.1 User interaction needs

The repeated requirement is not simply "use fewer words." It is:

- use compact, proper, professional language;
- remove canned praise, filler, restatement, and AI-like transitions;
- avoid em-dash-heavy prose and unnecessary storytelling;
- answer the direct question before background;
- preserve technical vocabulary, symbols, code, paths, and exact errors;
- use equations to carry mathematical reasoning;
- define symbols locally and derive results step by step;
- start from the generic formulation and specialize last;
- distinguish facts, derivations, choices, assumptions, and claims;
- state the problem, admissible family, solver, evidence, and claim boundary;
- investigate before recommending changes;
- treat "do not edit" and "show for review" as hard permission boundaries;
- provide connected, human-readable, RAG-addressable notes;
- show a small useful result before building large infrastructure;
- keep machine-facing output structured and compact where appropriate; and
- use domain-specific response structures instead of one universal template.

### 4.2 PhD and mathematical research

Representative authorities:

- `rob_unversal_article/README.md`
- `BVP_problem/BVP_PROBLEM_HUB.md`
- `BVP_problem/BVP_CLAIM_RULES.md`
- `BVP_problem/state_transfer/notes/methods_and_optimality_guide.md`

Extracted requirements:

- Organize knowledge through root, topic, method, result, and authority nodes.
- Keep state-transfer and gate claims separate.
- Identify a method by problem + admissible family + solver.
- Separate feasibility, stationarity, local optimality, and global optimality.
- Keep metric provenance and normalization explicit.
- Use a claim ladder and state the highest supported level.
- Derive from formulation rather than introducing an unexplained ansatz.
- Preserve protected theory and review gates even if validation later succeeds.

### 4.3 Code and optimizer work

Representative authorities:

- `phd/CODES/AGENTS.md`
- `phd/CODES/README.md`
- `OPTIMIZER_v3/README.md`
- `OPTIMIZER_v3/optimizer/system_olgs/SYSTEM_OLGS_HUB.md`

Extracted requirements:

- Read project-local authority files before acting.
- Respect environment, template, source-of-truth, and compatibility contracts.
- Keep physics/system responsibility separate from optimizer responsibility.
- Prefer compact structured discovery with optional human formatting.
- Preserve public APIs and propagate shared-contract changes deliberately.
- Verify implementation against theory and with small smoke tests first.
- Report exact commands, outputs, artifacts, and remaining uncertainty.
- Avoid wrappers and abstractions unless they solve a demonstrated need.

### 4.4 Web, design, and professional communication

Representative authorities:

- `Web_space/SITE_CONTEXT.md`
- `Web_space/wiki/00 Home.md`
- `Web_space/wiki/08 Change Preview Protocol.md`

Extracted requirements:

- Read the project hub and source-of-truth map first.
- Never edit generated files directly.
- Use a short design gate for substantial changes.
- Make previews functional, not decorative screenshots.
- Verify desktop, interaction, routes, and relevant mobile behavior.
- Return the exact command matching the real final state.
- For career communication, distinguish verified facts, transferable fit,
  platform-specific gaps, and cautious administrative claims.
- Use formal but natural language, not generic AI motivation prose.

### 4.5 Research notes and learning

Memory records a review-gated paper-extraction workflow and Markdown learning
work. The live paper-extraction implementation is currently absent, so only the
interaction lessons are reused:

- one pedagogical main artifact before infrastructure;
- detail notes only when they add real value;
- compact initial review, then one file or decision at a time;
- reciprocal links and typed relationships;
- syntax checks do not establish pedagogical quality;
- explanations should be paired with rendered or clickable artifacts; and
- workflows should use `flowchart LR` when showing a pipeline.

### 4.6 Personal AI architecture

Representative authorities:

- `TODO/ai_project/docs/00-INDEX.md`
- `TODO/ai_project/docs/03-architecture.md`
- `TODO/ai_project/docs/05-agent-contract.md`
- `TODO/ai_project/decisions/ADR-002-protocols-over-frameworks.md`

Extracted requirements:

- Protocols over frameworks.
- Code controls sequencing; the model fills bounded judgement slots.
- Stable profile and state must live outside any one model or adapter.
- Components need explicit contracts and must remain replaceable.
- Bounded specialists are preferable to one giant autonomous agent.
- Evals are required before registration or default activation.
- Writes are proposed or permission-gated.
- Provenance, versioning, and auditability are structural requirements.

## 5. Current Caveman Audit

### Useful engineering to preserve

| Existing component | Reuse decision | Target role |
|---|---|---|
| symlink-safe atomic flag read/write | adapt | versioned JSON state storage |
| config precedence | adapt | profile and session defaults |
| JSONC settings reader/writer | keep | safe adapter installation |
| hook validation and idempotent install | keep | neutral hook management |
| provider detection matrix | keep | cross-platform installation |
| dry-run and uninstall paths | keep | reversible deployment |
| canonical-to-packaged mirror checks | adapt | generated package verification |
| compressor backup and validation | keep separately | `text-compress` utility |
| bounded investigator/builder/reviewer roles | adapt | delegation operation |
| snapshot evaluation harness | extend | token and quality evaluation |
| repository verification runner | adapt | manifests, state, graph, adapter parity |

### Behavior to personalize

| Existing idea | Personalized form |
|---|---|
| remove filler | compact professional voice |
| preserve technical terms | universal invariant |
| formula-first math | `derive` operation + math overlay |
| short code review findings | `review` operation |
| concise commit messages | `write` + commit format |
| compact subagent receipts | bounded delegation contracts |
| auto-clarity for risk | permission and safety policy |

### Behavior to replace or retire

- Caveman name and character identity.
- Broken grammar as a default style.
- Mechanical article deletion.
- Always-on `full` mode.
- One scalar state mixing voice, task, and reasoning.
- Hard-coded Caveman prompts in hooks and platform rules.
- Duplicated routing logic in Claude and OpenCode adapters.
- Fixed `65%` or `75%` savings assumptions.
- Token savings measured without fidelity or reasoning checks.
- Wenyan modes in the default product. They may be archived separately if wanted.
- Caveman-specific package, command, status-line, asset, and marketplace names
  after the compatibility period.

## 6. Target Protocol Model

### 6.1 Independent dimensions

```json
{
  "schema": 1,
  "profile": {
    "voice": "compact-professional",
    "no_em_dash": true,
    "no_canned_praise": true,
    "math_rendering": "latex"
  },
  "session": {
    "depth": "standard",
    "explicit_overrides": []
  },
  "turn": {
    "operation": "derive",
    "domain": "quantum-control",
    "permission": "read-only",
    "evidence": "analytic",
    "format": "equation-led"
  }
}
```

- `profile` contains stable, reviewed personal preferences.
- `session` contains explicit temporary changes.
- `turn` is recomputed for each request.
- Permission is never inferred downward. `read-only` cannot become `write`.
- Durable profile changes require explicit user approval.

### 6.2 Precedence

```text
explicit current instruction
  > explicit session override
  > project-local authority
  > reviewed personal profile
  > generic protocol default
```

For current facts:

```text
live verified source > dated memory > general recollection
```

### 6.3 Runtime flow

```mermaid
flowchart LR
  A["Session start"] --> B["Load compact profile"]
  B --> C["Receive request"]
  C --> D["Parse explicit command and permission"]
  D --> E["Select one operation"]
  E --> F["Select zero or one domain overlay"]
  F --> G["Load required policy"]
  G --> H["Render compact instruction"]
  H --> I["Respond and verify"]
  I --> J["Record non-sensitive telemetry"]
```

The router should use exact commands and high-confidence rules first. It should
not spend a separate LLM call merely to classify ordinary requests. When no
specialization is needed, it should apply only the personal core.

## 7. Protocol Components

### 7.1 Personal core

The default response contract should require:

- direct answer first;
- proper, compact sentences;
- no canned praise or unnecessary acknowledgement;
- no repeated restatement of the request;
- no story or analogy unless useful or requested;
- no removal of necessary technical explanation;
- exact preservation of identifiers, paths, commands, and errors;
- explicit assumptions when ambiguity matters;
- facts, inferences, decisions, and uncertainty kept distinct; and
- a clear next step only when one is useful.

### 7.2 Generic operations

| Operation | Default response order |
|---|---|
| discuss | answer -> reason -> implication |
| explain | answer -> mechanism -> example or consequence |
| derive | conclusion -> setup -> equations -> derivation -> insight -> check -> boundary |
| investigate | scope -> evidence -> findings -> unknowns -> plan |
| design | aim -> requirements -> alternatives -> architecture -> migration -> tests |
| implement | preflight -> edits -> verification -> result -> residual risk |
| review | severity-ordered findings -> evidence -> fix -> test gaps |
| write | audience -> facts and claims -> structure -> draft -> factual check |

### 7.3 Domain overlays

#### Mathematics

- Render equations in LaTeX.
- Define every symbol locally.
- Show one justified transformation per step.
- Start with the general formulation and specialize last.
- Prefer analytic verification before code.
- State exact, approximate, restricted, or heuristic status.

#### Quantum control research

- State physical model, objective, hard constraints, residual convention,
  admissible family, solver, and claim level.
- Separate terminal penalty, feasibility, constrained energy, KKT, PMP,
  second-order evidence, and globality.
- Keep state-transfer and gate conventions separate.
- Report native and reconstructed metrics without substitution.

#### Software engineering

- Inspect current code and repository authority first.
- Preserve established contracts and responsibility boundaries.
- Keep changes scoped; no unrelated refactors.
- Verify with tests proportional to blast radius.
- Report commands and important output, not narration of every action.

#### Research notes and Obsidian

- Maintain clear authority and reader routes.
- Require useful inbound and outbound links.
- Keep routing metadata separate from duplicated content.
- Distinguish mechanical validation from pedagogical review.
- Prefer one useful artifact before general infrastructure.

#### Web and design

- Identify source files and generated outputs.
- Use a design gate for substantial changes.
- Build functional previews and test actual interaction.
- Return the correct project-specific preview route and command.

#### Career and professional writing

- Verify volatile facts.
- Separate demonstrated skills, transferable fit, and real gaps.
- Avoid unsupported legal, administrative, or experience claims.
- Use formal, natural language without generic AI motivation phrases.

#### Learning

- Explain the core concept before broad context.
- Pair syntax with a copyable example.
- Explain unfamiliar lines and symbols individually.
- Add a small verification, artifact, or exercise when useful.

#### AI-system design

- Preserve user ownership and replaceability.
- Use typed boundaries and deterministic orchestration.
- Keep memory external and provenance-aware.
- Require evals before activation.
- Treat agents as bounded components, not autonomous authorities.

## 8. Proposed Repository Structure

No new top-level `Skills/` wrapper is needed.

```text
interaction-protocol/
├── 00_INTERACTION_HUB.md
├── PROFILE.md
├── core/
│   ├── response-contract.md
│   ├── routing.md
│   └── voice.md
├── operations/
│   ├── discuss/SKILL.md
│   ├── explain/SKILL.md
│   ├── derive/SKILL.md
│   ├── investigate/SKILL.md
│   ├── design/SKILL.md
│   ├── implement/SKILL.md
│   ├── review/SKILL.md
│   └── write/SKILL.md
├── references/
│   ├── domains/
│   │   ├── mathematics.md
│   │   ├── quantum-control.md
│   │   ├── software.md
│   │   ├── research-notes.md
│   │   ├── web-design.md
│   │   ├── career.md
│   │   ├── learning.md
│   │   └── ai-systems.md
│   └── policies/
│       ├── permissions.md
│       ├── evidence.md
│       ├── verification.md
│       ├── memory.md
│       └── context-budget.md
├── runtime/
│   ├── state.js
│   ├── schema.js
│   ├── router.js
│   ├── selector.js
│   ├── renderer.js
│   └── telemetry.js
├── adapters/
│   ├── claude/
│   ├── codex/
│   ├── gemini/
│   ├── opencode/
│   └── openclaw/
├── utilities/
│   ├── text-compress/
│   └── tool-schema-compress/
├── evals/
│   ├── prompts/
│   ├── rubrics/
│   ├── fixtures/
│   └── snapshots/
└── legacy/
    └── aliases.json
```

## 9. Obsidian Integration

Agent route:

```text
SKILLS.md
  -> 00_SKILLS_HUB.md
  -> registry/interaction.md
  -> interaction-protocol/00_INTERACTION_HUB.md
  -> one operation SKILL.md
  -> optional domain or policy reference
```

Rules:

1. Add `registry/interaction.md` as the L2 family route.
2. Keep operation cards or protocol overview nodes in L3 only if they improve
   human graph navigation; do not add them to the agent critical path.
3. Operation skills are L4.
4. Runtime, adapters, utilities, tests, and references are L5.
5. Reuse the existing layer colours; do not assign a colour per operation.
6. Every operation links back to the interaction hub and to the domain/policy
   references it may load.
7. Registry files contain routing metadata, not duplicated protocol content.

## 10. Existing-To-New Component Map

| Current path or family | Target |
|---|---|
| `skills/caveman/SKILL.md` | `core/voice.md` and `core/response-contract.md` after full rewrite |
| `skills/caveman-math/` | `operations/derive/` plus math references |
| `skills/caveman-review/` | `operations/review/` |
| `skills/caveman-commit/` | commit specialization under `operations/write/` |
| `skills/cavecrew/` and `agents/` | bounded delegation reference and neutral agents |
| `skills/caveman-compress/` | `utilities/text-compress/` |
| `skills/caveman-help/` | interaction hub and generated command reference |
| `skills/caveman-stats/` | `runtime/telemetry.js` plus reporting command |
| `src/hooks/caveman-config.js` | `runtime/state.js` and `runtime/schema.js` |
| `src/hooks/caveman-activate.js` | Claude session-start adapter |
| `src/hooks/caveman-mode-tracker.js` | shared router plus Claude prompt adapter |
| `src/plugins/opencode/plugin.js` | thin OpenCode adapter |
| `bin/lib/settings.js` | neutral installer settings library |
| `bin/install.js` | neutral protocol installer |
| `evals/` | multi-domain token and quality evaluation suite |
| `tests/verify_repo.py` | repository, mirror, graph, and adapter verifier |

## 11. Detailed Implementation Phases

### Phase 0: Preserve and classify the current state

Tasks:

- Review the current staged worktree separately from this new plan.
- Create a clean checkpoint before protocol implementation.
- Record canonical sources, generated mirrors, packages, hooks, and installers.
- Mark every Caveman file: keep, adapt, split, generate, archive, or delete.

Acceptance:

- Exact checkpoint hash recorded.
- No unrelated staged work is mixed into migration commits.
- Canonical and generated files are unambiguous.

Stop gate: review the inventory before moving files.

### Phase 1: Approve the protocol specification

Tasks:

- Draft `PROFILE.md`, core response contract, routing dimensions, permission
  precedence, and context budgets.
- Create representative before/after examples from real user task types.
- Decide the final neutral product and command name.
- Decide whether Wenyan remains an optional archive or is removed completely.

Acceptance:

- Profile contains only stable preferences.
- No domain procedure is duplicated in the profile.
- User approves the voice and examples.

Stop gate: no runtime implementation before profile approval.

### Phase 2: Build protocol content

Tasks:

- Build the eight operation skills.
- Build domain and policy references.
- Migrate useful math, review, commit, delegation, and compression rules.
- Add hubs, backlinks, frontmatter, and registry routing.
- Validate links, layers, and maximum loading path.

Acceptance:

- One operation is enough for a generic task.
- A specialized task needs at most one domain reference.
- No duplicated Caveman prose remains in the new canonical content.
- Obsidian graph has no new orphan protocol nodes.

Stop gate: inspect protocol outputs manually before adding persistence.

### Phase 3: Build the neutral runtime beside Caveman

Tasks:

- Implement versioned state schema and validation.
- Generalize secure state read/write without weakening symlink protections.
- Implement explicit command parsing and permission detection.
- Implement operation/domain selection and compact context rendering.
- Add migration from old scalar state without deleting it yet.
- Add non-sensitive telemetry.

Acceptance:

- Malformed state fails closed to safe defaults.
- `read-only` cannot transition to write without explicit user instruction.
- Session start loads only profile/core.
- Per-turn reinforcement stays within the approved budget.

Stop gate: old and new runtimes remain independently reversible.

### Phase 4: Build thin adapters

Order:

1. Claude, because the current hooks are most complete.
2. OpenCode, replacing duplicated routing.
3. Codex.
4. Gemini.
5. OpenClaw.

Tasks:

- Keep platform lifecycle translation in adapters.
- Keep state, routing, selection, and rendering in shared runtime code.
- Preserve foreign settings and status-line configuration.
- Verify fresh install, reinstall, upgrade, and uninstall.

Acceptance:

- Identical input and profile produce equivalent selected state on all adapters.
- Installation is idempotent.
- Uninstall removes only managed entries.
- GUI launchers work with minimal `PATH` environments.

### Phase 5: Separate utilities

Tasks:

- Move file compression under a neutral utility identity.
- Preserve file detection, backup collision checks, protected-region checks,
  validation, repair attempts, and rollback.
- Evaluate MCP/tool-schema compression independently.
- Remove interaction-style assumptions from utility prompts.

Acceptance:

- File compression cannot target secrets, code, config, or existing backups.
- Original bytes are recoverable after every failed validation path.
- Tool-schema compression preserves machine semantics.

### Phase 6: Build evaluation before cutover

Evaluation categories:

| Category | Critical properties |
|---|---|
| simple question | direct, natural, no forced template |
| mathematical explanation | LaTeX, local symbols, complete derivation |
| quantum-control claim | problem/family/solver/claim boundary |
| read-only audit | no edits, evidence and plan only |
| code implementation | scoped edit, tests, exact report |
| code review | findings first, severity and locations |
| Obsidian design | authority, links, small visible workflow |
| Web_space change | source-only edit and correct preview command |
| career writing | verified facts and honest fit/gap |
| learning request | concept, example, line-level explanation |
| ambiguous request | explicit assumption or one useful question |
| destructive request | clear warning and confirmation boundary |

Comparison arms:

```text
baseline model
compact instruction only
current Caveman
new personal core
new core + operation
new core + operation + domain
```

Metrics:

- input tokens added by protocol;
- output tokens;
- total tokens;
- factual and mathematical fidelity;
- required-step coverage;
- permission compliance;
- claim-boundary compliance;
- style compliance;
- adapter parity;
- latency where measurable; and
- human preference review.

Critical safety, permission, and claim-boundary tests must pass completely.
Token reduction cannot compensate for a failed critical property.

### Phase 7: Compatibility and cutover

Tasks:

- Introduce the neutral command and package identity.
- Map old commands temporarily, for example:
  - `/caveman math` -> derive + mathematics;
  - `/caveman review` -> review;
  - `/caveman ultra` -> compact voice override.
- Emit one concise migration notice, not a notice every turn.
- Make the new protocol opt-in first, then default after evaluation.
- Keep rollback instructions and old package backup for one migration phase.

Acceptance:

- Existing users do not lose access during the transition.
- The new protocol can be disabled without uninstalling utilities.
- Cutover requires passing evals and explicit user approval.

### Phase 8: Remove Caveman identity and old implementation

Tasks:

- Remove old always-on hooks and scalar flags.
- Remove duplicated router implementations.
- Remove Caveman package, marketplace, command, status-line, documentation,
  asset, and plugin names.
- Remove temporary aliases after the agreed compatibility period.
- Regenerate packaged mirrors from canonical sources.
- Re-run full repository, installer, adapter, link, and eval verification.

Acceptance:

- No user-facing Caveman identity remains.
- No stale Caveman hook remains in supported platform settings.
- Neutral utilities and protocol components work independently.
- Documentation describes the final system rather than migration history.

## 12. Proposed Context Budgets

These are initial design limits to validate, not final performance claims.

| Layer | Proposed maximum |
|---|---:|
| always-loaded metadata/profile | 250 tokens |
| per-turn state reinforcement | 100 tokens |
| one operation skill | 450 tokens |
| one domain reference | 500 tokens |
| normal specialized total | 1,000 tokens |

Long examples, rubrics, and reference material remain on-demand. Scripts should
execute without being loaded into model context when possible.

## 13. Main Risks And Controls

| Risk | Control |
|---|---|
| new system becomes another large monolith | independent dimensions and one-operation loading |
| personalization becomes stale | reviewed profile and explicit durable updates only |
| routing chooses the wrong specialization | explicit override, high-confidence rules, safe generic fallback |
| brevity removes reasoning | fidelity rubric and required-step tests |
| adapters drift | shared runtime and parity fixtures |
| old and new settings conflict | versioned migration and idempotent managed markers |
| utility rename breaks safeguards | migrate tests before moving implementation |
| Obsidian graph becomes decorative | critical-path budget plus reciprocal links |
| memory is treated as current truth | live-source precedence and drift reporting |
| migration mixes with current staged work | Phase 0 checkpoint and separate commits |

## 14. Decisions Required Before Implementation

- [ ] Approve or replace the working name `interaction-protocol`.
- [ ] Approve the personal core voice contract.
- [ ] Approve the eight generic operations.
- [ ] Approve the initial domain overlays.
- [ ] Decide whether Wenyan is archived or deleted.
- [ ] Decide the neutral slash-command prefix.
- [ ] Approve the proposed token budgets.
- [ ] Approve the compatibility period for old commands.
- [ ] Decide whether telemetry is local-only and what fields it may record.
- [ ] Review the current staged repository checkpoint before migration begins.

## 15. Definition Of Done

The project is complete only when:

- the personal voice feels professional, natural, rigorous, and recognizably
  suited to the user without becoming a character;
- simple questions remain simple;
- mathematical and research questions receive complete equation-led reasoning;
- code and repository tasks respect live contracts and permission boundaries;
- domain modules load only when relevant;
- all supported adapters use the same state and routing engine;
- utilities work independently of response style;
- critical evals pass and token reductions are measured honestly;
- the Obsidian graph is connected and the agent read path remains bounded;
- old Caveman branding, hooks, commands, and duplicated logic are removed; and
- installation, upgrade, rollback, and uninstall are documented and verified.

## 16. Immediate Next Review

Review this document in this order:

1. Aim and non-goals.
2. Summarized scan results.
3. Personal core and operation list.
4. Existing-to-new component map.
5. Implementation phases and stop gates.
6. Open decisions.

After approval, the next action should be Phase 0 only: checkpoint and classify
the current implementation. No protocol files should be built in that same step.


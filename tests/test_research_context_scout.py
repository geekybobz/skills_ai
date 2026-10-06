#!/usr/bin/env python3

from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "research-context-scout"
sys.path.insert(0, str(ROOT / "scripts"))

from registry_runtime import build_manifest  # noqa: E402


class ResearchContextScoutTests(unittest.TestCase):
    def read(self, relative: str) -> str:
        return (PACKAGE / relative).read_text(encoding="utf-8")

    def test_package_entry_is_manual_and_alias_modes_are_declared(self) -> None:
        manifest = build_manifest(ROOT)
        route = next(item for item in manifest["routes"] if item["id"] == "research-context-scout")
        self.assertEqual("manual", route["state"])
        self.assertEqual("research-context-scout/SKILL.md", route["path"])
        self.assertEqual(
            [
                ("#> scout", "initial"),
                ("#> scout-again", "deepen"),
            ],
            [
                (item["command"], item["mode"])
                for item in manifest["command_aliases"]
                if item["skill_id"] == "research-context-scout"
            ],
        )

    def test_runtime_entry_excludes_the_long_human_guide(self) -> None:
        entry = " ".join(self.read("SKILL.md").split())
        self.assertIn("Do not read `README.md` during task", entry)
        self.assertIn("shared/SKILL.md", entry)
        self.assertIn("codex/SKILL.md", entry)
        self.assertIn("claude/CLAUDE.md", entry)

    def test_initial_phase_questions_and_pauses_before_deep_research(self) -> None:
        phase = self.read("shared/phases/initial-scout.md")
        self.assertLess(phase.index("## Cycle A"), phase.index("## Cycle B"))
        self.assertIn("Ask one to three questions", phase)
        self.assertIn("tell the user where to", self.read("shared/SKILL.md"))
        self.assertIn("stop", phase.lower())
        self.assertIn("Do not conduct the deep", phase)

    def test_record_template_protects_user_answers(self) -> None:
        template = self.read("shared/templates/research-orientation.md")
        self.assertGreaterEqual(template.count("USER RESPONSES START"), 1)
        self.assertEqual(
            template.count("USER RESPONSES START"),
            template.count("USER RESPONSES END"),
        )
        self.assertIn("### Agent interpretation", template)
        self.assertIn("## Superseded conclusions", template)
        self.assertIn(
            "one more than the highest existing cycle number",
            " ".join(template.split()),
        )
        self.assertIn("never overwrite", self.read("codex/CODEX.md").lower())

    def test_claude_wrapper_preserves_record_and_directive_boundaries(self) -> None:
        wrapper = self.read("claude/CLAUDE.md")
        self.assertIn("late state-recovery", wrapper)
        self.assertIn("Never read `../README.md`", wrapper)
        self.assertIn("`#> scout-again` is `deepen`", " ".join(wrapper.split()))
        self.assertIn("mode-resolution.md", wrapper)
        self.assertNotIn("inject", wrapper.lower())

    # Evidence policy is host-neutral and lives in the shared rule. A wrapper may
    # only name its host's tools. Keeping policy in one wrapper is what left
    # Claude without the empty-response guard that Codex had.
    SHARED_POLICY_PHRASES = (
        "A control probe is the only thing that establishes health",
        "backend health is **unverified**",
        "reclassify that call as pass 2",
        "Never infer that a host approval setting will prompt",
        "only normal acquisition trigger",
    )
    HOST_TOOLS = (
        "extract_key_findings",
        "smart_extract_paper",
        "download_and_read_paper",
        "zotero_get_item_fulltext",
        "list_library_papers",
        "zotero_search_items",
    )

    def test_evidence_policy_is_shared_and_wrappers_only_name_tools(self) -> None:
        rule = " ".join(self.read("shared/rules/literature-corpus.md").split())
        wrappers = {
            name: " ".join(self.read(name).split())
            for name in ("codex/SKILL.md", "claude/CLAUDE.md")
        }
        for phrase in self.SHARED_POLICY_PHRASES:
            flat = " ".join(phrase.split())
            with self.subTest(phrase=phrase):
                self.assertIn(flat, rule, "policy must live in the shared rule")
                for name, text in wrappers.items():
                    self.assertNotIn(flat, text, f"{name} restates shared policy")
        # Both hosts must name every tool the shared guards require.
        for name, text in wrappers.items():
            for tool in self.HOST_TOOLS:
                with self.subTest(wrapper=name, tool=tool):
                    self.assertIn(tool, text)
            with self.subTest(wrapper=name):
                self.assertIn("literature-corpus.md", text)
        self.assertNotIn("list_library_papers", self.read("codex/CODEX.md"))

    def test_corpus_stop_condition_has_one_predicate(self) -> None:
        # gates.md, the checkpoint rule and the corpus rule previously disagreed
        # about an unreachable backend: one said stop, two said continue.
        gates = " ".join(self.read("shared/gates.md").split())
        checkpoints = " ".join(self.read("shared/rules/alignment-checkpoints.md").split())
        rule = " ".join(self.read("shared/rules/literature-corpus.md").split())
        self.assertIn("corpus readiness is `pending`", gates)
        self.assertIn("Stop while corpus readiness is `pending`", checkpoints)
        self.assertIn("Corpus readiness is `pending` whenever", rule)
        # Only the corpus rule may enumerate which states hold it pending.
        for other in (gates, checkpoints):
            self.assertNotIn("lacks locally available full text", other)
        # An unfinished check is never an exclusion and never an absence.
        self.assertIn("`missing`, `unknown` and `failed` all hold it pending", rule)
        self.assertIn("neither be excluded nor counted as absent", rule)

    def test_local_state_enum_covers_every_mandated_value(self) -> None:
        rule = self.read("shared/rules/literature-corpus.md")
        enum_line = next(l for l in rule.splitlines() if l.startswith("local state:"))
        values = {v.strip() for v in enum_line.split(":", 1)[1].split("|")}
        # Every state the rule tells the agent to record must be in the enum.
        for mandated in ("missing", "failed", "unknown", "available"):
            with self.subTest(value=mandated):
                self.assertIn(mandated, values)

    def test_scout_runtime_does_not_depend_on_zotero_semantic_search(self) -> None:
        for path in sorted(PACKAGE.rglob("*")):
            if not path.is_file() or path.suffix not in {".md", ".yaml", ".json"}:
                continue
            with self.subTest(path=path.relative_to(PACKAGE)):
                self.assertNotIn(
                    "zotero_semantic_search",
                    path.read_text(encoding="utf-8"),
                )

    def test_codex_always_on_path_stays_bounded(self) -> None:
        self.assert_path_under(
            "Codex always-on",
            10000,
            "SKILL.md",
            "shared/SKILL.md",
            "codex/SKILL.md",
        )

    def test_record_and_brief_contract_has_one_home(self) -> None:
        contract = self.read("shared/rules/record-and-brief.md")
        self.assertIn("USER RESPONSES", contract)
        self.assertIn("only writable", contract)
        self.assertIn("research-orientation.md", contract)
        self.assertIn("brief leads with a bounded current orientation", " ".join(contract.split()))
        # No wrapper may restate the shared contract; that duplication is what
        # let the Claude wrapper drift out of sync with the shared workflow.
        for relative in ("claude/CLAUDE.md", "codex/SKILL.md", "codex/CODEX.md"):
            wrapper = " ".join(self.read(relative).split())
            with self.subTest(relative=relative):
                self.assertNotIn("brief leads with a bounded current orientation", wrapper)
                self.assertNotIn("only writable", wrapper)
                self.assertNotIn("physics_objective", wrapper)

    def test_mode_resolution_covers_aliases_and_bare_requests(self) -> None:
        fallback = " ".join(self.read("shared/rules/mode-resolution.md").split())
        entry = " ".join(self.read("SKILL.md").split())
        for form in ("#> scout ...", "#> scout-again ..."):
            with self.subTest(form=form):
                self.assertIn(form, fallback)
        self.assertIn("no existing record means `initial`", fallback)
        self.assertIn("For any other invocation, read", entry)
        # Aliases fix the mode; the rule file is only for other invocations.
        self.assertIn("Read only when the invocation is not `#> scout` or `#> scout-again`", fallback)
        self.assertNotIn("inject", (fallback + entry).lower())

    def test_answered_intake_without_a_map_completes_initial_cycle_b(self) -> None:
        entry = " ".join(self.read("shared/SKILL.md").split())
        initial = " ".join(self.read("shared/phases/initial-scout.md").split())
        deepen = self.read("shared/phases/deepen-scout.md")
        self.assertIn("answered intake with an empty Existing understanding ledger", entry)
        self.assertIn("physics objective, existing-work verdict, relation class", entry)
        self.assertIn("skip Cycle A and run Cycle B", entry)
        self.assertIn("skip Cycle A and run Cycle B", initial)
        self.assertIn("run initial Cycle B first", deepen)

    def test_deepen_phase_preserves_focus_and_cycle_structure(self) -> None:
        phase = self.read("shared/phases/deepen-scout.md")
        self.assertIn("Apply any supplied focus", phase)
        self.assertIn("## Interaction cycle N", phase)
        self.assertIn("fresh user-response", phase)

    def test_record_path_and_repository_guard_are_shared(self) -> None:
        entry = " ".join(self.read("SKILL.md").split())
        shared = self.read("shared/SKILL.md")
        claude = self.read("claude/CLAUDE.md")
        self.assertIn("resolve its parent as the project root", entry)
        self.assertIn("inside the Skills AI repository", shared)
        self.assertNotIn("inside the Skills AI repository", claude)

    def test_recommendations_have_formal_evidence_and_application_contracts(self) -> None:
        rule = self.read("shared/rules/evidence-gate.md")
        self.assertIn("\\mathcal D=(C,M,A,E,T,F,U,P)", rule)
        self.assertIn("\\mathcal A=", rule)
        self.assertIn("\\mathcal P=(Q,C,N,E,G,A,F)", rule)
        for level in ("E0", "E1", "E2", "E3", "E4"):
            self.assertIn(level, rule)
        self.assertIn("Mathematical claim", rule)
        self.assertIn("Numerical claim", rule)
        self.assertIn("Physical claim", rule)

    def test_physics_objective_gates_separate_existing_from_new(self) -> None:
        shared = self.read("shared/SKILL.md")
        initial = self.read("shared/phases/initial-scout.md")
        template = self.read("shared/templates/research-orientation.md")
        anti = self.read("shared/rules/anti-hallucination.md")
        relation = self.read("shared/rules/relation-taxonomy.md")
        journal = self.read("shared/rules/journal-thresholds.md")
        lens = self.read("shared/phases/math-method-lens.md")
        gates = self.read("shared/gates.md")

        self.assertIn("G1 physics objective", gates)
        self.assertIn("G6 existing vs new ledger", gates)
        self.assertNotIn("G1 physics objective", shared)
        self.assertIn("Lock the physics objective before method explanation", initial)
        self.assertIn("## Existing understanding ledger", template)
        self.assertIn("## New direction ledger", template)
        self.assertIn("A source result cannot enter the new direction ledger", anti)
        self.assertIn("same-physics-different-math", relation)
        self.assertIn("different-physics-same-math", relation)
        self.assertIn("Start at J1", journal)
        self.assertIn("novelty, journal level", lens)

    def test_deepen_phase_is_delta_based(self) -> None:
        phase = self.read("shared/phases/deepen-scout.md")
        self.assertIn("S_{k+1}=\\operatorname{revise}(S_k,\\Delta_k)", phase)
        self.assertIn("Do not rerun the complete initial scan", phase)
        self.assertIn("counterevidence", phase)

    # `research-orientation.md` is the record Scout writes in the user's project,
    # not a file inside this package, so it never resolves here.
    EXTERNAL_REFERENCES = frozenset({"research-orientation.md"})

    def test_every_internal_reference_resolves(self) -> None:
        # A reference resolves either against the shared root (`rules/x.md` cited
        # from a phase) or against the citing file's own directory (`../shared/x.md`
        # from a wrapper). Anything else is a dead link.
        shared_root = PACKAGE / "shared"
        broken: list[str] = []
        for path in sorted(PACKAGE.rglob("*.md")):
            if path.name == "README.md":
                continue
            text = path.read_text(encoding="utf-8")
            for reference in re.findall(r"`([^`\s]+\.md)`", text):
                if reference in self.EXTERNAL_REFERENCES or ":" in reference:
                    continue
                candidates = (path.parent / reference, shared_root / reference)
                if not any(candidate.exists() for candidate in candidates):
                    broken.append(f"{path.relative_to(PACKAGE)} -> {reference}")
        self.assertEqual([], broken, f"unresolvable references: {broken}")

    # Phrases that must have exactly one home. Duplication here is what let the
    # earlier drafts drift: the same constraint restated in two files means one
    # of them silently goes stale. Template rows are excluded on purpose — the
    # template is the user's record, not prompt text.
    CANONICAL_PHRASES = (
        "successfully extracted",
        "Corpus readiness is `pending`",
        "lowers the status",
        "Scout never acquires silently",
        "caps at `source-read`",
        "does not permit automatic downloads",
    )

    def test_canonical_phrases_have_one_home(self) -> None:
        runtime = [
            path
            for path in sorted(PACKAGE.rglob("*.md"))
            if path.name != "README.md" and "templates" not in path.parts
        ]
        for phrase in self.CANONICAL_PHRASES:
            homes = [
                str(path.relative_to(PACKAGE))
                for path in runtime
                if phrase in " ".join(path.read_text(encoding="utf-8").split())
            ]
            with self.subTest(phrase=phrase):
                self.assertEqual(1, len(homes), f"{phrase!r} lives in {homes}")

    def test_load_graph_matches_files(self) -> None:
        import json

        graph = json.loads((PACKAGE / "load-graph.json").read_text(encoding="utf-8"))
        listed: set[str] = set()
        for key in ("always_on", "record_contract"):
            listed.update(graph[key])
        listed.update(graph["phases"].values())
        listed.update(graph["gate_rules"].values())
        listed.update(graph["conditional"].values())
        listed.add(graph["gate_index"])
        for relative in sorted(listed):
            with self.subTest(relative=relative):
                self.assertTrue((PACKAGE / relative).exists(), f"ghost entry: {relative}")
        # Every shared runtime file must appear somewhere in the graph.
        on_disk = {
            str(path.relative_to(PACKAGE))
            for path in (PACKAGE / "shared").rglob("*.md")
        }
        self.assertEqual(set(), on_disk - listed, "shared files missing from load-graph.json")
        for name, path_list in graph["paths"].items():
            for relative in path_list:
                with self.subTest(path=name, relative=relative):
                    self.assertIn(relative, listed)

    def test_runtime_files_remain_bounded(self) -> None:
        limits = {
            "SKILL.md": 5000,
            "shared/SKILL.md": 3000,
            "shared/gates.md": 5000,
            "shared/phases/initial-scout.md": 8000,
            "shared/phases/deepen-scout.md": 8000,
            "shared/phases/math-method-lens.md": 5000,
            "shared/rules/alignment-checkpoints.md": 3000,
            "shared/rules/anti-hallucination.md": 6000,
            "shared/rules/collective-synthesis.md": 4000,
            "shared/rules/evidence-gate.md": 8000,
            "shared/rules/journal-thresholds.md": 2000,
            "shared/rules/journal-level-up.md": 2000,
            "shared/rules/literature-corpus.md": 8000,
            "shared/rules/relation-taxonomy.md": 6000,
            "shared/rules/record-and-brief.md": 4000,
            "shared/rules/source-status.md": 3000,
            "shared/rules/mode-resolution.md": 2500,
            "codex/SKILL.md": 4000,
            "codex/CODEX.md": 4000,
            "claude/CLAUDE.md": 3200,
        }
        for relative, limit in limits.items():
            with self.subTest(relative=relative):
                self.assertLess((PACKAGE / relative).stat().st_size, limit)

    def test_packet_keys_have_one_home(self) -> None:
        contract = self.read("shared/rules/record-and-brief.md")
        keys = contract.split("```text")[1].split("```")[0].split()
        self.assertIn("physics_objective", keys)
        self.assertIn("gap_predicate", keys)
        self.assertIn("journal_threshold", keys)
        self.assertIn("alignment_state", keys)
        self.assertIn("acquisition_manifest", keys)
        self.assertIn("corpus_coverage", keys)
        self.assertIn("collective_synthesis", keys)
        self.assertIn("project_translations", keys)
        self.assertIn("beginner_report", keys)
        self.assertEqual(21, len(keys))
        # Every other runtime file must reference the contract, not repeat it.
        for relative in (
            "SKILL.md",
            "shared/SKILL.md",
            "shared/phases/initial-scout.md",
            "shared/phases/deepen-scout.md",
        ):
            with self.subTest(relative=relative):
                self.assertNotIn("existing_understanding_ledger", self.read(relative))
        self.assertIn("record-and-brief.md", self.read("shared/SKILL.md"))

    def test_source_status_vocabulary_is_single_valued(self) -> None:
        rule = self.read("shared/rules/source-status.md")
        template = self.read("shared/templates/research-orientation.md")
        gate = self.read("shared/rules/evidence-gate.md")
        for token in (
            "search-candidate",
            "abstract-only",
            "source-read",
            "equation-checked",
            "result-verified",
        ):
            with self.subTest(token=token):
                self.assertIn(token, rule)
                self.assertIn(token, template)
        # The gate points at the rule instead of restating the ladder.
        self.assertIn("source-status.md", gate)
        self.assertNotIn("equation-checked", gate)
        self.assertIn("source-status.md", self.read("shared/rules/anti-hallucination.md"))
        for relative in (
            "shared/phases/initial-scout.md",
            "shared/rules/anti-hallucination.md",
            "shared/templates/research-orientation.md",
            "codex/SKILL.md",
            "claude/CLAUDE.md",
        ):
            with self.subTest(relative=relative):
                self.assertNotIn("candidate-only", self.read(relative))

    def test_search_effort_is_capped_by_tier_and_fails_closed(self) -> None:
        initial = " ".join(self.read("shared/phases/initial-scout.md").split())
        gates = self.read("shared/gates.md")
        self.assertIn("smallest pilot query", initial)
        self.assertIn("pilot query and preview fit inside the tier budget", initial)
        self.assertIn("## Tier budget", self.read("shared/phases/initial-scout.md"))
        for tier in ("T1", "T2", "T3"):
            with self.subTest(tier=tier):
                self.assertIn(tier, initial)
        self.assertIn("An exhausted budget is a search state, never a gap", initial)
        self.assertIn("Stop if", gates)
        self.assertIn("G5 relation map", gates)
        self.assertIn("preview groups only the dimensions its funded lanes", initial)
        self.assertIn(
            "same-physics-same-math",
            self.read("shared/rules/record-and-brief.md"),
        )
        template = self.read("shared/templates/research-orientation.md")
        self.assertIn("Tier and search budget", template)
        self.assertIn("Lanes searched / not searched", template)

    def test_template_enumerates_every_relation_label(self) -> None:
        taxonomy = self.read("shared/rules/relation-taxonomy.md")
        template = self.read("shared/templates/research-orientation.md")
        labels = set(re.findall(r"`([a-z]+(?:-[a-z]+)+)`", taxonomy))
        self.assertIn("no-go-or-bound", labels)
        for label in labels:
            with self.subTest(label=label):
                self.assertIn(label, template)

    def test_absence_of_results_cannot_establish_a_gap(self) -> None:
        anti = " ".join(self.read("shared/rules/anti-hallucination.md").split())
        initial = " ".join(self.read("shared/phases/initial-scout.md").split())
        self.assertIn("Absence of results is a search state, never a gap", anti)
        self.assertIn("require at least one source at `source-read` or stronger", anti)
        self.assertIn("requires at least one `source-read` comparison", initial)

    def test_gate_ids_are_wired_into_the_phases_and_record(self) -> None:
        shared = self.read("shared/gates.md")
        initial = self.read("shared/phases/initial-scout.md")
        template = self.read("shared/templates/research-orientation.md")
        for gate in ("G0", "G1", "G2", "G3", "G4", "G5", "G6", "G7", "G8", "G9"):
            with self.subTest(gate=gate):
                self.assertIn(gate, shared)
                self.assertIn(gate, initial)
        # G10 closes every cycle, so both phases must reach it.
        self.assertIn("G10", self.read("shared/phases/deepen-scout.md"))
        self.assertIn("(G10)", self.read("shared/phases/initial-scout.md"))
        self.assertIn("Highest gate reached", template)

    def test_alignment_checkpoints_interrupt_the_right_boundaries(self) -> None:
        shared = self.read("shared/gates.md")
        initial = self.read("shared/phases/initial-scout.md")
        rule = self.read("shared/rules/alignment-checkpoints.md")
        template = self.read("shared/templates/research-orientation.md")

        for gate in ("G2A", "G3A", "G6A"):
            with self.subTest(gate=gate):
                self.assertIn(gate, shared)
                self.assertIn(gate, initial)
        self.assertLess(initial.index("G2)."), initial.index("G2A context mirror"))
        self.assertLess(initial.index("G2A context mirror"), initial.index("G3 landscape"))
        self.assertIn("Stop while its state is `pending`", rule)
        for action in ("CONFIRM", "CORRECT", "ADD", "REMOVE", "PRIORITIZE", "DEFER"):
            with self.subTest(action=action):
                self.assertIn(action, rule)
                self.assertIn(action, template)
        for state in (
            "Context alignment",
            "Search alignment",
            "Corpus readiness",
            "Interpretation alignment",
        ):
            with self.subTest(state=state):
                self.assertIn(state, template)

    def test_search_policy_is_recent_bounded_and_user_aligned(self) -> None:
        rule = self.read("shared/rules/literature-corpus.md")
        initial = self.read("shared/phases/initial-scout.md")
        for phrase in (
            "newest credible review",
            "primary results published after that review's search cutoff",
            "seminal source",
            "Age alone never proves",
            "backward/forward citation closure",
            "unsearched regions",
            "stopping condition",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, rule)
        self.assertIn("landscape preview", initial)
        self.assertIn("aligned the search lanes", initial)
        self.assertIn("Scout cannot claim all papers globally", rule)

    def test_acquisition_requires_user_handoff_and_complete_extraction(self) -> None:
        rule = " ".join(self.read("shared/rules/literature-corpus.md").split())
        source = " ".join(self.read("shared/rules/source-status.md").split())
        template = self.read("shared/templates/research-orientation.md")
        initial = " ".join(self.read("shared/phases/initial-scout.md").split())

        # Acquisition is library-first with one manifest-wide confirmation. The
        # no-silent-download guarantee survives; the per-paper handoff does not.
        self.assertIn("locally available** when the host's configured reference", rule)
        self.assertIn("Check availability with the library's own read tools", rule)
        self.assertIn("does not permit automatic downloads", rule)
        self.assertIn("One confirmation covers the whole manifest", rule)
        # Absence requires a healthy backend and an exact negative identity lookup.
        self.assertIn("A control probe is the only thing that establishes health", rule)
        self.assertIn("exact canonical-identity lookup explicitly reports", rule)
        self.assertIn("empty library search is never evidence of absence", rule)
        # An unreachable library is an infrastructure failure, never a missing paper.
        self.assertIn("unreachable** — the backend did not answer", rule)
        self.assertIn("another healthy backend or a user-supplied local file", rule)
        self.assertIn("Every paper incorporated into the collective synthesis", rule)
        self.assertIn("locally available as full text", rule)
        self.assertIn("successfully extracted", rule)
        self.assertIn("Corpus readiness is `pending` whenever", rule)
        self.assertIn("confirm exclusion", rule)
        self.assertIn("source-read` alone does not waive", source)
        self.assertIn("## Paper acquisition and corpus coverage", template)
        self.assertIn("stop until every paper selected for synthesis", initial.lower())

    def test_two_pass_reading_keeps_paper_cards_out_of_main_report(self) -> None:
        corpus = " ".join(self.read("shared/rules/literature-corpus.md").split())
        source = " ".join(self.read("shared/rules/source-status.md").split())
        synthesis = " ".join(self.read("shared/rules/collective-synthesis.md").split())
        brief = " ".join(self.read("shared/rules/record-and-brief.md").split())
        self.assertIn("Coverage extraction", corpus)
        self.assertIn("Decisive deep reading", corpus)
        self.assertIn("do not dump one card per paper into the main report", corpus)
        # Pass 1 must be cheap: no full text, and capped below equation-level status.
        self.assertIn("applies to every incorporated paper and must not load its full text", corpus)
        self.assertIn("cannot reach `equation-checked` or `result-verified`", corpus)
        self.assertIn("A pass-1 mechanical extraction caps at `source-read`", source)
        # Extractions are written once and reused across cycles.
        self.assertIn("Write each extraction once and reuse it", corpus)
        self.assertIn("does not render a paper-by-paper catalogue", synthesis)
        self.assertIn("rather than one visible card per paper", brief)

    def test_collective_synthesis_maps_ideas_into_project_notation(self) -> None:
        rule = self.read("shared/rules/collective-synthesis.md")
        template = self.read("shared/templates/research-orientation.md")
        taxonomy = self.read("shared/rules/relation-taxonomy.md")
        for object_name in ("Achievement", "Model", "Mechanism"):
            with self.subTest(object_name=object_name):
                self.assertIn(f"\\text{{{object_name}}}", rule)
        self.assertIn("Group the extracted corpus", rule)
        self.assertIn("Translate into project notation", rule)
        self.assertIn("candidate project reformulation", rule)
        self.assertIn("candidate re-derivation -> testable insight", rule)
        self.assertIn("## Collective mathematical ideas", template)
        self.assertIn("## Project-notation translations", template)
        self.assertIn("equivalent-under-transformation", taxonomy)
        self.assertIn("unknown-relation", taxonomy)

    def test_beginner_report_is_bounded_and_not_an_expert_verdict(self) -> None:
        synthesis = self.read("shared/rules/collective-synthesis.md")
        brief = self.read("shared/rules/record-and-brief.md")
        template = self.read("shared/templates/research-orientation.md")
        entry = " ".join(self.read("SKILL.md").split())

        self.assertIn("not an authoritative expert verdict", synthesis)
        self.assertIn("does not pretend to replace", entry)
        self.assertIn("the user retains the final research judgment", brief.lower())
        for heading in (
            "Our current problem",
            "What the extracted literature collectively suggests",
            "Translation into our notation",
            "Supported, derived, proposed and unknown",
            "User decision",
        ):
            with self.subTest(heading=heading):
                self.assertIn(heading, template)
        for provenance in (
            "source-established",
            "mapped",
            "scout-derived",
            "independently-verified",
            "proposed-inspiration",
            "unknown",
        ):
            with self.subTest(provenance=provenance):
                self.assertIn(provenance, synthesis)

    def test_deepen_reopens_only_affected_alignment_and_synthesis(self) -> None:
        phase = self.read("shared/phases/deepen-scout.md")
        for delta in (
            "context correction",
            "search direction",
            "acquired corpus",
            "terminology mapping",
        ):
            with self.subTest(delta=delta):
                self.assertIn(delta, phase)
        self.assertIn("cannot affect the orientation until its full text is extracted", phase)
        self.assertIn("Rebuild only the affected collective idea", phase)
        self.assertIn("correction never silently preserves", phase)

    def path_bytes(self, *relatives: str) -> int:
        return sum((PACKAGE / relative).stat().st_size for relative in relatives)

    def assert_path_under(self, name: str, limit: int, *relatives: str) -> None:
        total = self.path_bytes(*relatives)
        self.assertLess(
            total,
            limit,
            f"{name} load path is {total} B, over the {limit} B budget "
            f"({total - limit:+d} B). Files: {', '.join(relatives)}",
        )

    ALWAYS_ON = ("SKILL.md", "claude/CLAUDE.md", "shared/SKILL.md")
    # Read once at the start of Cycle B or a deepen cycle, never on Cycle A.
    GATE_INDEX = "shared/gates.md"
    GATE_RULES = (
        "shared/rules/record-and-brief.md",
        "shared/rules/alignment-checkpoints.md",
        "shared/rules/anti-hallucination.md",
        "shared/rules/collective-synthesis.md",
        "shared/rules/literature-corpus.md",
        "shared/rules/relation-taxonomy.md",
        "shared/rules/source-status.md",
        "shared/rules/evidence-gate.md",
        "shared/rules/journal-thresholds.md",
        "shared/rules/journal-level-up.md",
    )

    # Budgets are set from measurement with ~7% headroom, so they catch a
    # regression rather than describing an aspiration. Baseline before the
    # gate-sized refactor: always-on 12910, Cycle A 20519, Cycle B 30998,
    # Deepen 27027, and no early-stop path existed.
    #
    # After deferring the gate index into gates.md, binding the corpus rule to
    # two-pass reading, and moving evidence policy out of the wrappers into the
    # shared rule: always-on 8675, Cycle A 24198, Cycle B 53077,
    # Deepen 45022, early stop 47233. Deferral pays only on paths that
    # never reach a gate -- Cycle A and ambiguity bounces. A path that does reach
    # a gate still loads gates.md, so it is close to a wash there, and the
    # evidence rules deliberately spend bytes here to save far more paper tokens
    # at run time.

    def test_always_on_load_path_stays_bounded(self) -> None:
        # Read on every single run before any research happens.
        self.assert_path_under("Always-on", 9300, *self.ALWAYS_ON)

    def test_cycle_a_load_path_stays_bounded(self) -> None:
        # Reconstruct, ask, stop: no gate rule beyond the record contract.
        self.assert_path_under(
            "Cycle A",
            25900,
            *self.ALWAYS_ON,
            "shared/phases/initial-scout.md",
            "shared/rules/record-and-brief.md",
            "shared/templates/research-orientation.md",
        )

    def test_cycle_b_load_path_stays_bounded(self) -> None:
        # Worst case: every gate rule plus the template in one initial cycle.
        self.assert_path_under(
            "Cycle B",
            56800,
            *self.ALWAYS_ON,
            self.GATE_INDEX,
            "shared/phases/initial-scout.md",
            *self.GATE_RULES,
            "shared/templates/research-orientation.md",
        )

    def test_deepen_load_path_stays_bounded(self) -> None:
        self.assert_path_under(
            "Deepen",
            48200,
            *self.ALWAYS_ON,
            self.GATE_INDEX,
            "shared/phases/deepen-scout.md",
            *self.GATE_RULES,
        )

    def test_early_stop_load_path_stays_bounded(self) -> None:
        # A run that settles at G3-G6 must not pay for the G7-G9 rules. This
        # path is the whole point of splitting rules along gate lines.
        early = (
            *self.ALWAYS_ON,
            self.GATE_INDEX,
            "shared/phases/initial-scout.md",
            "shared/rules/record-and-brief.md",
            "shared/rules/alignment-checkpoints.md",
            "shared/rules/literature-corpus.md",
            "shared/rules/relation-taxonomy.md",
            "shared/rules/source-status.md",
            "shared/rules/anti-hallucination.md",
            "shared/rules/collective-synthesis.md",
            "shared/templates/research-orientation.md",
        )
        self.assert_path_under("Early stop", 50500, *early)
        full = self.path_bytes(
            *self.ALWAYS_ON,
            self.GATE_INDEX,
            "shared/phases/initial-scout.md",
            *self.GATE_RULES,
            "shared/templates/research-orientation.md",
        )
        self.assertLess(
            self.path_bytes(*early),
            full - 4000,
            "stopping early must save at least 4000 B over the full gate run",
        )

    def test_registry_description_matches_the_current_workflow(self) -> None:
        registry = (ROOT / "registry" / "research.md").read_text(encoding="utf-8")
        for term in (
            "physics objective",
            "user-aligned",
            "extracted-corpus synthesis",
            "project-notation translation",
        ):
            with self.subTest(term=term):
                self.assertIn(term, registry)

    def test_human_guide_explains_the_new_public_contract(self) -> None:
        guide = self.read("README.md")
        for phrase in (
            "Context mirror plus pilot directions",
            "User aligns search lanes",
            "Extract every incorporated paper",
            "Build A Collective Mathematical Synthesis",
            "project notation",
            "bounded orientation, not an authoritative expert verdict",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, guide)

    def test_human_guide_links_to_live_skill_files_and_hub(self) -> None:
        guide = self.read("README.md")
        required = (
            "docs/00_SKILLS_HUB",
            "research-context-scout/SKILL",
            "research-context-scout/shared/SKILL",
            "research-context-scout/codex/SKILL",
            "research-context-scout/claude/CLAUDE",
        )
        for target in required:
            self.assertIn(target, guide)


if __name__ == "__main__":
    unittest.main()

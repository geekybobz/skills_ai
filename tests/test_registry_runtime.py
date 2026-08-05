#!/usr/bin/env python3

from __future__ import annotations

import json
import copy
import os
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from registry_runtime import (  # noqa: E402
    DESIGN_ROUTED_FAMILIES,
    build_manifest,
    compact_context,
    load_manifest,
    registry_summary,
    route_request,
)
from install_runtime_adapter import check_adapter, install_adapter  # noqa: E402
from compile_registry import atomic_write as atomic_write_manifest  # noqa: E402
from toggle_registry import toggle  # noqa: E402


class RegistryRuntimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = load_manifest()

    def test_compiled_manifest_matches_sources(self) -> None:
        self.assertEqual(build_manifest(), self.manifest)

    def test_ordinary_question_uses_normal_fallback(self) -> None:
        decision = route_request("What is the capital of France?", self.manifest)
        self.assertEqual("NORMAL", decision["result"])
        self.assertEqual("NO_SKILL_MATCH", decision["reason_code"])

    def test_registry_discovery_returns_live_metadata_without_skill_body(self) -> None:
        decision = route_request("What skills are saved in memory?", self.manifest)
        self.assertEqual("NORMAL", decision["result"])
        self.assertEqual("REGISTRY_STATUS", decision["reason_code"])
        self.assertNotIn("skill", decision)
        self.assertEqual(self.manifest["source_hash"], decision["registry"]["source_hash"])
        self.assertEqual(43, decision["registry"]["route_counts"]["active"])
        self.assertEqual(1, decision["registry"]["route_counts"]["manual"])
        self.assertEqual(["quantum-job-collector"], decision["registry"]["routes"]["off"])
        self.assertEqual(
            ["/scout", "/scout-again"],
            [item["command"] for item in decision["registry"]["command_aliases"]],
        )
        self.assertNotIn("hidden", decision["registry"]["routes"])

    def test_research_command_aliases_select_one_manual_skill_and_mode(self) -> None:
        cases = {
            "/scout /tmp/new-project theory": ("/scout", "initial"),
            "/scout-again /tmp/new-project result.md": ("/scout-again", "deepen"),
        }
        for query, (command, mode) in cases.items():
            with self.subTest(query=query):
                decision = route_request(query, self.manifest)
                self.assertEqual("MATCH", decision["result"])
                self.assertEqual("research-context-scout", decision["skill"]["id"])
                self.assertEqual("manual", decision["skill"]["state"])
                self.assertEqual("explicit-command-alias", decision["routing"]["fit_reason"])
                self.assertEqual(command, decision["context"]["skill_invocation"]["command"])
                self.assertEqual(mode, decision["context"]["skill_invocation"]["mode"])
                self.assertNotIn("/tmp/new-project", json.dumps(decision))
                compact = compact_context(decision)
                self.assertIn(f"command={command}", compact)
                self.assertIn(f"mode={mode}", compact)

    def test_research_command_aliases_are_exact_and_leading_only(self) -> None:
        prompts = (
            "Explain the literal /scout /tmp/project",
            "`/scout /tmp/project`",
            "We are scouting this research project",
            "/scoutish /tmp/project",
            "Read this example:\n```text\n/scout /tmp/project\n```",
        )
        for query in prompts:
            with self.subTest(query=query):
                decision = route_request(query, self.manifest)
                self.assertNotEqual("research-context-scout", decision.get("skill", {}).get("id"))

    def test_skill_normal_and_sudo_precede_research_aliases(self) -> None:
        normal = route_request("/scout /tmp/project /skill normal", self.manifest)
        sudo = route_request("/sudo /scout /tmp/project", self.manifest)
        self.assertEqual("USER_NORMAL", normal["reason_code"])
        self.assertEqual("USER_SUDO", sudo["reason_code"])

    def test_canonical_research_skill_request_remains_available(self) -> None:
        decision = route_request(
            "/skill research-context-scout initial /tmp/project",
            self.manifest,
        )
        self.assertEqual("research-context-scout", decision["skill"]["id"])
        self.assertEqual("explicit-skill", decision["routing"]["fit_reason"])
        self.assertNotIn("skill_invocation", decision["context"])

    def test_manual_research_route_does_not_activate_from_ordinary_prose(self) -> None:
        decision = route_request(
            "Give this new research project an initial supervisor assessment",
            self.manifest,
        )
        self.assertNotEqual("research-context-scout", decision.get("skill", {}).get("id"))

    def test_registry_summary_can_include_hidden_only_for_maintenance(self) -> None:
        normal = registry_summary(self.manifest)
        maintenance = registry_summary(self.manifest, include_hidden=True)
        self.assertNotIn("hidden", normal["routes"])
        self.assertIn("hidden", maintenance["routes"])

    def test_skills_ai_write_request_gets_external_change_boundary(self) -> None:
        decision = route_request("Edit the Skills AI router", self.manifest)
        self.assertEqual("SKILLS_AI_MAINTENANCE", decision["reason_code"])
        boundary = decision["context"]["skills_ai_change_boundary"]
        self.assertEqual("request-only-outside-maintenance-workspace", boundary["mode"])

    def test_skills_ai_maintenance_bypasses_task_skill_scoring(self) -> None:
        prompts = (
            "Audit the local skill registry node consistency",
            "Implement the Skills AI maintenance protocol with no external install.",
            "Inspect the Skills AI graph and skill handling rules",
            "Delete a route from the Skills AI registry",
        )
        for query in prompts:
            with self.subTest(query=query):
                decision = route_request(query, self.manifest)
                self.assertEqual("NORMAL", decision["result"])
                self.assertEqual("SKILLS_AI_MAINTENANCE", decision["reason_code"])
                self.assertNotIn("skill", decision)

    def test_negated_install_is_not_positive_write_or_setup_intent(self) -> None:
        decision = route_request(
            "No external install. Inspect the Skills AI change protocol.",
            self.manifest,
        )
        self.assertEqual("SKILLS_AI_MAINTENANCE", decision["reason_code"])
        self.assertEqual("read-only", decision["context"]["requested_access"])

    def test_extended_prohibitions_are_not_positive_routes_or_access(self) -> None:
        prompts = (
            "Explain why we should not deploy this project to Vercel",
            "Explain why we must not deploy this project to Vercel",
            "Avoid installing anything externally. Explain the setup.",
            "Review the protocol instead of installing Node.",
        )
        for query in prompts:
            with self.subTest(query=query):
                decision = route_request(query, self.manifest)
                self.assertEqual("NORMAL", decision["result"])
                self.assertEqual("read-only", decision["context"]["requested_access"])

    def test_maintenance_implementation_remains_write_requested_after_negation_filter(self) -> None:
        decision = route_request(
            "Implement the Skills AI maintenance protocol with no external install.",
            self.manifest,
        )
        self.assertEqual("SKILLS_AI_MAINTENANCE", decision["reason_code"])
        self.assertEqual("write-requested", decision["context"]["requested_access"])

    def test_positive_node_install_still_routes_to_setup_guide(self) -> None:
        decision = route_request("Install Node for my first project", self.manifest)
        self.assertEqual("MATCH", decision["result"])
        self.assertEqual("setup-guide", decision["skill"]["id"])

    def test_leading_implementation_intent_wins_over_later_inspection_words(self) -> None:
        decision = route_request(
            "Implement the Skills AI scanner, then inspect its report",
            self.manifest,
        )
        self.assertEqual("implement", decision["context"]["operation"])

    def test_math_is_a_response_overlay_not_a_task_skill(self) -> None:
        decision = route_request("Derive the Euler-Lagrange equation", self.manifest)
        self.assertEqual("NORMAL", decision["result"])
        self.assertNotIn("skill", decision)
        self.assertEqual("math", decision["context"]["interaction"]["mode"])
        self.assertEqual("mathematics", decision["context"]["domain"])
        self.assertIn("equations", decision["context"]["output"]["shape"])

    def test_general_protocol_handles_commit_response_without_extra_skill(self) -> None:
        decision = route_request("Write a commit message for the staged change", self.manifest)
        self.assertEqual("NORMAL", decision["result"])
        self.assertEqual("general", decision["context"]["interaction"]["mode"])
        self.assertEqual("write", decision["context"]["operation"])
        self.assertEqual("read-only", decision["context"]["requested_access"])

    def test_disabled_skill_falls_back(self) -> None:
        decision = route_request("/skill quantum-job-collector Run the exhaustive collector", self.manifest)
        self.assertEqual("NORMAL", decision["result"])
        self.assertEqual("DISABLED_SKILL", decision["reason_code"])

    def test_natural_and_canonical_skill_opt_outs(self) -> None:
        prompts = (
            "Don't use any skill. Explain this code without jargon.",
            "Do not use any local skill. Explain this code without jargon.",
            "/skill normal Explain this code without jargon.",
            "skillhub normal Explain this code without jargon.",
        )
        for query in prompts:
            with self.subTest(query=query):
                decision = route_request(query, self.manifest)
                self.assertEqual("USER_NORMAL", decision["reason_code"])
                self.assertEqual(0, decision["routing"]["fit"])

    def test_explicit_skill_control_has_high_fit(self) -> None:
        decision = route_request("/skill code-explainer Explain this code", self.manifest)
        self.assertEqual("code-explainer", decision["skill"]["id"])
        self.assertEqual(3, decision["routing"]["fit"])

    def test_bare_skill_identifier_is_not_an_explicit_invocation(self) -> None:
        decision = route_request("Discuss code-explainer routing metadata", self.manifest)
        self.assertNotEqual("explicit-skill", decision["routing"]["fit_reason"])

    def test_manual_task_skill_requires_explicit_exact_request(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        route = next(item for item in manifest["routes"] if item["id"] == "dark-mode-specialist")
        route["state"] = "manual"
        automatic = route_request("Design a dark mode theme switch", manifest)
        explicit = route_request("Use the dark-mode-specialist skill for this theme", manifest)
        self.assertEqual("NORMAL", automatic["result"])
        self.assertEqual("dark-mode-specialist", explicit["skill"]["id"])
        self.assertEqual("manual", explicit["skill"]["state"])

    def test_unknown_explicit_skill_fails_open(self) -> None:
        decision = route_request("/skill does-not-exist Explain this", self.manifest)
        self.assertEqual("NORMAL", decision["result"])
        self.assertEqual("UNKNOWN_SKILL_REQUEST", decision["reason_code"])

    def test_maintenance_boundary_precedes_unknown_skill_control(self) -> None:
        decision = route_request("/skill does-not-exist Edit the Skills AI router", self.manifest)
        self.assertEqual("SKILLS_AI_MAINTENANCE", decision["reason_code"])
        self.assertIn("skills_ai_change_boundary", decision["context"])

    def test_maintenance_boundary_precedes_skill_opt_out(self) -> None:
        decision = route_request("/skill normal Edit the Skills AI router", self.manifest)
        self.assertEqual("SKILLS_AI_MAINTENANCE", decision["reason_code"])
        self.assertIn("skills_ai_change_boundary", decision["context"])

    def test_ambiguity_returns_bounded_candidates_and_fit_one(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        first = next(item for item in manifest["routes"] if item["id"] == "code-explainer")
        second = copy.deepcopy(first)
        second["id"] = "alternate-code-explainer"
        manifest["routes"].append(second)
        decision = route_request("Explain this code without jargon", manifest)
        self.assertEqual("AMBIGUOUS_SKILL_MATCH", decision["reason_code"])
        self.assertEqual(1, decision["routing"]["fit"])
        self.assertEqual(
            ["alternate-code-explainer", "code-explainer", "normal"],
            decision["routing"]["clarification"]["choices"],
        )
        self.assertNotIn("path", decision["routing"]["candidates"][0])

    def test_output_receipt_depth_and_format_controls(self) -> None:
        decision = route_request(
            "/receipt on /depth brief /format mermaid+summary Explain this code",
            self.manifest,
        )
        self.assertEqual("on", decision["context"]["receipt"])
        self.assertEqual("brief", decision["context"]["output"]["depth"])
        self.assertEqual(["mermaid", "summary"], decision["context"]["output"]["format"])
        self.assertIn("depth=brief", compact_context(decision))

    def test_control_like_text_inside_code_is_inert(self) -> None:
        prompts = (
            "Explain this literal: `/skill code-explainer`",
            "Inspect this sample:\n```text\nUse the dark-mode-specialist skill\n```",
            "Explain this literal: `/receipt on /format mermaid`",
        )
        for query in prompts:
            with self.subTest(query=query):
                decision = route_request(query, self.manifest)
                self.assertNotEqual("explicit-skill", decision["routing"]["fit_reason"])
                self.assertEqual("auto", decision["context"]["receipt"])
                self.assertEqual(["auto"], decision["context"]["output"]["format"])

    def test_pdf_reading_does_not_route_to_design(self) -> None:
        decision = route_request("Summarize this PDF document", self.manifest)
        self.assertEqual("NORMAL", decision["result"])

    def test_design_families_require_explicit_design_intent(self) -> None:
        ordinary_prompts = (
            "Search recent papers about quantum control",
            "What does search_index.py do?",
            "Explain input_tensor_shape.py",
            "Summarize structure_factor.py",
            "Create a plot of a sine function",
            "Create an A0 poster",
            "Analyze design_matrix.py and its table coefficients",
            "Design the quantum-control derivation",
            "Search for design system examples",
            "Explain the design system used by this app",
            "Inspect the design tokens in this repository",
            "What is UI design?",
            "Fix why the design router mistakes color-code prompts",
            "Design an API that returns a data table",
            "Design the software architecture for a dashboard service",
        )
        for query in ordinary_prompts:
            with self.subTest(query=query):
                decision = route_request(query, self.manifest)
                self.assertNotIn(
                    decision.get("skill", {}).get("family"),
                    DESIGN_ROUTED_FAMILIES,
                )

    def test_all_design_route_terms_are_inert_without_a_design_request(self) -> None:
        design_routes = [
            route for route in self.manifest["routes"]
            if route["family"] in DESIGN_ROUTED_FAMILIES
        ]
        for route in design_routes:
            terms = (route["id"], *route["triggers"])
            for term in terms:
                prompts = (
                    f"Search source code for {term}",
                    f"Explain `{term}` without editing anything",
                    f"Inspect src/{route['id']}.py for this token: {term}",
                )
                for query in prompts:
                    with self.subTest(route=route["id"], term=term, query=query):
                        decision = route_request(query, self.manifest)
                        self.assertNotIn(
                            decision.get("skill", {}).get("family"),
                            DESIGN_ROUTED_FAMILIES,
                        )

    def test_explicit_design_intent_routes_relevant_design_tasks(self) -> None:
        cases = {
            "Design a search interface with autocomplete": "search-specialist",
            "Design a dark mode theme switch": "dark-mode-specialist",
            "Design a scientific figure for these results": "data-visualization-specialist",
            "Design an A0 research poster": "poster-lead",
            "Design a data table with sorting": "table-designer",
            "Design a login flow with passkey": "auth-security-ux-specialist",
            "For this app, please design a dashboard with KPI cards": "dashboard-designer",
            "Can you redesign the login flow with passkey?": "auth-security-ux-specialist",
            "Help me design a sidebar with breadcrumbs": "navigation-specialist",
            "Create a design for a dark mode theme": "dark-mode-specialist",
        }
        for query, skill_id in cases.items():
            with self.subTest(query=query):
                decision = route_request(query, self.manifest)
                self.assertEqual("MATCH", decision["result"])
                self.assertEqual(skill_id, decision["skill"]["id"])

    def test_non_design_families_keep_their_existing_routes(self) -> None:
        cases = {
            "Explain this code without jargon": "code-explainer",
            "Diagnose this broken build and stack trace": "debug-helper",
            "Plan a LaTeX theory chapter": "theory-reference",
        }
        for query, skill_id in cases.items():
            with self.subTest(query=query):
                decision = route_request(query, self.manifest)
                self.assertEqual(skill_id, decision["skill"]["id"])

    def test_math_overlay_composes_with_task_skill(self) -> None:
        decision = route_request(
            "Plan a LaTeX theory chapter and derive the main Hamiltonian equation",
            self.manifest,
        )
        self.assertEqual("theory-reference", decision["skill"]["id"])
        self.assertEqual("math", decision["context"]["interaction"]["mode"])
        self.assertEqual("theory", decision["context"]["domain"])

    def test_math_intent_ignores_artifact_mentions(self) -> None:
        prompts = (
            "Review equation_parser.py for a bug",
            "Search for the word formula in the repository",
            "Fix the LaTeX equation rendering code",
            "The formula field in settings.json is wrong",
        )
        for query in prompts:
            with self.subTest(query=query):
                decision = route_request(query, self.manifest)
                self.assertEqual("general", decision["context"]["interaction"]["mode"])

    def test_manual_math_requires_explicit_control(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        manifest["components"]["interaction.math"]["state"] = "manual"
        automatic = route_request("Solve x^2 - 5x + 6 = 0", manifest)
        explicit = route_request("/interaction math solve x^2 - 5x + 6 = 0", manifest)
        self.assertEqual("general", automatic["context"]["interaction"]["mode"])
        self.assertEqual("math", explicit["context"]["interaction"]["mode"])

    def test_explicit_general_overrides_automatic_math(self) -> None:
        decision = route_request(
            "/interaction general derive the Euler-Lagrange equation",
            self.manifest,
        )
        self.assertEqual("general", decision["context"]["interaction"]["mode"])

    def test_context_has_polished_response_contract(self) -> None:
        decision = route_request("Explain this code", self.manifest)
        context = decision["context"]
        self.assertEqual("compact-professional", context["output"]["voice"])
        self.assertTrue(context["response_contract"])
        self.assertIn("polished complete sentences", compact_context(decision))

    def test_toggle_dry_run_does_not_write(self) -> None:
        source = ROOT / "registry" / "activation.md"
        with tempfile.TemporaryDirectory() as directory:
            register = Path(directory) / "activation.md"
            register.write_bytes(source.read_bytes())
            before = register.read_bytes()
            changed = toggle(register, "interaction.math", "manual", write=False)
            self.assertTrue(changed)
            self.assertEqual(before, register.read_bytes())

    def test_codex_adapter_installer_is_atomic_and_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            config_dir = Path(directory)
            dry_run = install_adapter("codex", config_dir, dry_run=True)
            self.assertEqual("would-update", dry_run["entry"])
            self.assertFalse((config_dir / "skills").exists())
            self.assertEqual("updated", install_adapter("codex", config_dir)["entry"])
            self.assertTrue(check_adapter("codex", config_dir))
            self.assertEqual("unchanged", install_adapter("codex", config_dir)["entry"])

    def test_claude_adapter_installs_without_replacing_foreign_settings(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            config_dir = Path(directory)
            settings = {"model": "custom", "hooks": {"SessionStart": [{"hooks": []}]}}
            (config_dir / "settings.json").write_text(json.dumps(settings), encoding="utf-8")
            results = install_adapter("claude", config_dir)
            self.assertEqual("absent", results["entry"])
            self.assertEqual("updated", results["hook"])
            self.assertEqual("updated", results["settings"])
            installed = json.loads((config_dir / "settings.json").read_text(encoding="utf-8"))
            self.assertEqual("custom", installed["model"])
            self.assertTrue(installed["hooks"]["SessionStart"])
            self.assertTrue(check_adapter("claude", config_dir))
            self.assertTrue((config_dir / "settings.json.skills-ai.bak").exists())

    def test_claude_adapter_preserves_foreign_hook_and_settings(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            config_dir = Path(directory)
            hook = config_dir / "hooks" / "skills-ai-router.js"
            hook.parent.mkdir(parents=True)
            hook.write_text("// user-owned hook\n", encoding="utf-8")
            settings = config_dir / "settings.json"
            original_settings = b'{"model":"custom"}\n'
            settings.write_bytes(original_settings)
            results = install_adapter("claude", config_dir)
            self.assertEqual("preserved-foreign", results["hook"])
            self.assertEqual("not-attempted", results["entry"])
            self.assertEqual("preserved", results["settings"])
            self.assertEqual("// user-owned hook\n", hook.read_text(encoding="utf-8"))
            self.assertEqual(original_settings, settings.read_bytes())
            self.assertFalse((config_dir / "settings.json.skills-ai.bak").exists())

    def test_claude_settings_backups_preserve_first_and_latest_states(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            config_dir = Path(directory)
            settings = config_dir / "settings.json"
            original = b'{"model":"first"}\n'
            settings.write_bytes(original)
            install_adapter("claude", config_dir)
            first_backup = config_dir / "settings.json.skills-ai.bak"
            self.assertEqual(original, first_backup.read_bytes())
            changed = json.loads(settings.read_text(encoding="utf-8"))
            changed["manual_after_install"] = True
            changed_bytes = (json.dumps(changed) + "\n").encode()
            settings.write_bytes(changed_bytes)
            install_adapter("claude", config_dir)
            self.assertEqual(original, first_backup.read_bytes())
            self.assertEqual(
                changed_bytes,
                (config_dir / "settings.json.skills-ai.previous").read_bytes(),
            )

    @unittest.skipIf(os.name == "nt", "POSIX mode bits are not portable")
    def test_compiled_manifest_write_is_world_readable(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "manifest.json"
            atomic_write_manifest(target, "{}\n")
            self.assertEqual(0o644, stat.S_IMODE(target.stat().st_mode))

    def test_claude_adapter_removes_only_managed_bootstrap(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            config_dir = Path(directory)
            skill_target = config_dir / "skills" / "skills-ai-registry" / "SKILL.md"
            skill_target.parent.mkdir(parents=True)
            skill_target.write_bytes((ROOT / "runtime" / "SKILL.md").read_bytes())
            self.assertEqual("would-remove", install_adapter("claude", config_dir, dry_run=True)["entry"])
            self.assertTrue(skill_target.exists())
            self.assertEqual("removed", install_adapter("claude", config_dir)["entry"])
            self.assertFalse(skill_target.exists())
            self.assertTrue(check_adapter("claude", config_dir))

    def test_claude_adapter_preserves_foreign_bootstrap(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            config_dir = Path(directory)
            skill_target = config_dir / "skills" / "skills-ai-registry" / "SKILL.md"
            skill_target.parent.mkdir(parents=True)
            skill_target.write_text("user-authored\n", encoding="utf-8")
            self.assertEqual("preserved-foreign", install_adapter("claude", config_dir)["entry"])
            self.assertEqual("user-authored\n", skill_target.read_text(encoding="utf-8"))
            self.assertTrue(check_adapter("claude", config_dir))

    def test_claude_hook_uses_shared_router(self) -> None:
        completed = subprocess.run(
            ["node", str(ROOT / "adapters" / "claude" / "skills-ai-router.js"), "--root", str(ROOT)],
            input=json.dumps({"prompt": "/depth brief Explain this code without jargon"}),
            text=True,
            capture_output=True,
            check=True,
        )
        payload = json.loads(completed.stdout)
        context = payload["hookSpecificOutput"]["additionalContext"]
        self.assertIn("Selected local skill: code-explainer", context)
        self.assertIn("voice=compact-professional", context)
        self.assertIn("depth=brief", context)

    def test_claude_hook_renders_registry_discovery_without_skill_body(self) -> None:
        completed = subprocess.run(
            ["node", str(ROOT / "adapters" / "claude" / "skills-ai-router.js"), "--root", str(ROOT)],
            input=json.dumps({"prompt": "What skills are saved in memory?"}),
            text=True,
            capture_output=True,
            check=True,
        )
        payload = json.loads(completed.stdout)
        context = payload["hookSpecificOutput"]["additionalContext"]
        self.assertIn("Live Skills AI registry source", context)
        self.assertIn("active skills (43)", context)
        self.assertIn("manual skills (1): research-context-scout", context)
        self.assertIn("off skills (1): quantum-job-collector", context)
        self.assertNotIn("Selected local skill", context)

    def test_benchmark_fixture_expectations(self) -> None:
        cases = json.loads((ROOT / "tests" / "router_cases.json").read_text(encoding="utf-8"))
        for case in cases:
            with self.subTest(case=case["name"]):
                decision = route_request(case["query"], self.manifest)
                self.assertEqual(case["result"], decision["result"])
                self.assertEqual(case.get("skill"), decision.get("skill", {}).get("id"))
                if "interaction" in case:
                    self.assertEqual(case["interaction"], decision["context"]["interaction"]["mode"])

    def test_interaction_prompt_corpus(self) -> None:
        cases = json.loads((ROOT / "tests" / "interaction_cases.json").read_text(encoding="utf-8"))
        for case in cases:
            with self.subTest(query=case["query"]):
                decision = route_request(case["query"], self.manifest)
                self.assertEqual(case["mode"], decision["context"]["interaction"]["mode"])


if __name__ == "__main__":
    unittest.main()

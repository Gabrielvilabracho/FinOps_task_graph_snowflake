from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class RepositoryContractTests(unittest.TestCase):
    def read(self, relative_path: str) -> str:
        path = ROOT / relative_path
        self.assertTrue(path.is_file(), f"Missing required file: {relative_path}")
        return path.read_text(encoding="utf-8")

    def test_responsibility_based_layout_exists(self) -> None:
        required = (
            "README.md",
            "docs/architecture.md",
            "docs/official-snowflake-evidence.md",
            "docs/operations/runbook.md",
            "sql/00_setup/01_finops_objects.sql",
            "sql/00_setup/02_finops_grants.sql",
            "sql/10_core/10_finops_cost_policy.sql",
            "sql/20_procedures/20_finops_run_lifecycle.sql",
            "sql/20_procedures/21_finops_check_cost.sql",
            "sql/20_procedures/22_finops_check_errors.sql",
            "sql/20_procedures/23_finops_check_warehouse.sql",
            "sql/20_procedures/24_finops_check_queries.sql",
            "sql/20_procedures/25_finops_check_ai.sql",
            "sql/20_procedures/26_finops_check_other_costs.sql",
            "sql/20_procedures/27_finops_report.sql",
            "sql/20_procedures/28_finops_alert.sql",
            "sql/20_procedures/29_finops_finalizer.sql",
            "sql/30_tasks/30_finops_task_graph.sql",
            "sql/30_tasks/31_resume_finops_task_graph.sql",
            "sql/30_tasks/32_suspend_finops_task_graph.sql",
            "sql/90_validation/90_validate_deployment.sql",
        )

        for relative_path in required:
            with self.subTest(relative_path=relative_path):
                self.assertTrue((ROOT / relative_path).is_file(), relative_path)

    def test_cost_policy_has_only_confirmed_thresholds(self) -> None:
        sql = self.read("sql/10_core/10_finops_cost_policy.sql")
        self.assertRegex(
            sql,
            r"(?i)FINOPS_CLASSIFY_COST\(CURRENT_CREDITS, PREVIOUS_CREDITS, 25, 0\.30\)",
        )
        self.assertIn("DAILY_CREDIT_THRESHOLD", sql)
        self.assertIn("GROWTH_RATIO_THRESHOLD", sql)
        self.assertIn("NORMAL", sql)
        self.assertIn("ATTENTION", sql)

    def test_non_cost_modules_do_not_hardcode_alert_thresholds(self) -> None:
        for name in (
            "22_finops_check_errors.sql",
            "23_finops_check_warehouse.sql",
            "24_finops_check_queries.sql",
            "25_finops_check_ai.sql",
            "26_finops_check_other_costs.sql",
        ):
            with self.subTest(module=name):
                sql = self.read(f"sql/20_procedures/{name}")
                self.assertIn("SP_FINOPS_RECORD_RULE_GAP", sql)
                self.assertNotRegex(sql, r"(?i)(threshold|limit)\s*[:=]\s*[0-9]")

    def test_task_graph_is_serverless_daily_and_acyclic_by_contract(self) -> None:
        sql = self.read("sql/30_tasks/30_finops_task_graph.sql")
        self.assertIn("USING CRON 0 10 * * * UTC", sql)
        self.assertIn("OVERLAP_POLICY = NO_OVERLAP", sql)
        self.assertNotRegex(sql, r"(?im)^\s*WAREHOUSE\s*=")

        root_children = (
            "FINOPS_CHECK_COST",
            "FINOPS_CHECK_ERRORS",
            "FINOPS_CHECK_WAREHOUSE",
            "FINOPS_CHECK_QUERIES",
            "FINOPS_CHECK_AI",
            "FINOPS_CHECK_OTHER_COSTS",
        )
        for task_name in root_children:
            pattern = rf"(?is)CREATE OR REPLACE TASK\s+{task_name}.*?AFTER\s+FINOPS_ROOT_TASK"
            self.assertRegex(sql, pattern)

        self.assertRegex(
            sql,
            r"(?is)CREATE OR REPLACE TASK\s+FINOPS_FINALIZER.*?FINALIZE\s*=\s*FINOPS_ROOT_TASK",
        )

        task_blocks = re.findall(
            r"(?is)CREATE OR REPLACE TASK\s+(\w+)\s+(.*?)(?=CREATE OR REPLACE TASK|\Z)",
            sql,
        )
        dependencies: dict[str, set[str]] = {}
        for task_name, body in task_blocks:
            after_match = re.search(r"(?is)\bAFTER\s+(.+?)\s+AS\b", body)
            dependencies[task_name] = (
                set(re.findall(r"\bFINOPS_[A-Z_]+\b", after_match.group(1)))
                if after_match
                else set()
            )

        self.assertEqual(
            dependencies["FINOPS_REPORT_TASK"],
            set(root_children),
        )
        self.assertEqual(
            dependencies["FINOPS_ALERT_TASK"],
            {"FINOPS_REPORT_TASK"},
        )

        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(task_name: str) -> None:
            self.assertNotIn(task_name, visiting, f"Task cycle detected at {task_name}")
            if task_name in visited:
                return
            visiting.add(task_name)
            for predecessor in dependencies.get(task_name, set()):
                visit(predecessor)
            visiting.remove(task_name)
            visited.add(task_name)

        for task_name in dependencies:
            visit(task_name)

    def test_runtime_contains_no_external_orchestrator(self) -> None:
        sql_text = "\n".join(
            path.read_text(encoding="utf-8")
            for path in (ROOT / "sql").rglob("*.sql")
        )
        self.assertNotRegex(sql_text, r"(?i)\b(airflow|dbt)\b")

    def test_documentation_marks_event_driven_as_future(self) -> None:
        architecture = self.read("docs/architecture.md")
        self.assertRegex(architecture, r"(?i)streams.*(future|proposed)")
        self.assertRegex(architecture, r"(?i)triggered tasks.*(future|proposed)")

    def test_operational_statuses_separate_anomalies_from_failures(self) -> None:
        lifecycle = self.read("sql/20_procedures/20_finops_run_lifecycle.sql")
        finalizer = self.read("sql/20_procedures/29_finops_finalizer.sql")
        combined = lifecycle + finalizer
        for status in (
            "NORMAL",
            "ATTENTION",
            "RULE_NOT_CONFIGURED",
            "FAILED",
            "ATTENTION_REQUIRED",
        ):
            self.assertIn(status, combined)

        self.assertIn("SP_FINOPS_BUILD_REPORT", finalizer)
        self.assertIn("SP_FINOPS_SEND_ALERT", finalizer)

    def test_snowflake_scripting_delimiters_are_balanced(self) -> None:
        for path in (ROOT / "sql").rglob("*.sql"):
            with self.subTest(path=path.relative_to(ROOT)):
                text = path.read_text(encoding="utf-8")
                self.assertEqual(text.count("$$") % 2, 0, "Unbalanced $$ delimiter")


if __name__ == "__main__":
    unittest.main()

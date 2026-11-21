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
            "sql/10_core/11_finops_status_precedence.sql",
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
            "tests/sql/02_metric_contract_test.sql",
            "tests/sql/03_status_precedence_test.sql",
            "tests/sql/04_metric_completeness_invariant_test.sql",
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
        runtime_directories = ("10_core", "20_procedures", "30_tasks")
        sql_text = "\n".join(
            path.read_text(encoding="utf-8")
            for directory in runtime_directories
            for path in (ROOT / "sql" / directory).rglob("*.sql")
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
            "DATA_INCOMPLETE",
        ):
            self.assertIn(status, combined)

        self.assertIn("SP_FINOPS_BUILD_REPORT", finalizer)
        self.assertIn("SP_FINOPS_SEND_ALERT", finalizer)

    def test_metric_contract_is_typed_complete_and_idempotent(self) -> None:
        objects = self.read("sql/00_setup/01_finops_objects.sql")
        lifecycle = self.read("sql/20_procedures/20_finops_run_lifecycle.sql")

        self.assertRegex(
            objects,
            r"(?is)CREATE TABLE IF NOT EXISTS FINOPS_METRIC\s*\(.*?"
            r"PRIMARY KEY\s*\(RUN_ID, MODULE_NAME, METRIC_KEY\)",
        )
        for column in (
            "CURRENT_VALUE",
            "PREVIOUS_VALUE",
            "BASELINE_7D_VALUE",
            "BASELINE_30D_VALUE",
            "DELTA_ABSOLUTE",
            "DELTA_PERCENT",
            "THRESHOLD_VALUE",
            "CONTRIBUTORS",
            "EXPLANATION",
            "RECOMMENDED_ACTION",
            "SOURCE_NAME",
            "SOURCE_WINDOW_START",
            "SOURCE_WINDOW_END",
            "SOURCE_ROW_COUNT",
            "SOURCE_WATERMARK",
            "COLLECTED_AT",
            "EXPECTED_COMPLETE_AT",
            "IS_COMPLETE",
            "COMPLETENESS_REASON",
            "CREATED_AT",
            "UPDATED_AT",
        ):
            self.assertIn(column, objects)

        self.assertRegex(
            lifecycle,
            r"(?is)MERGE INTO FINOPS_METRIC.*?ON\s+target\.RUN_ID\s*=\s*source\.RUN_ID"
            r"\s+AND\s+target\.MODULE_NAME\s*=\s*source\.MODULE_NAME"
            r"\s+AND\s+target\.METRIC_KEY\s*=\s*source\.METRIC_KEY",
        )

    def test_metric_api_enforces_incomplete_status_precedence(self) -> None:
        lifecycle = self.read("sql/20_procedures/20_finops_run_lifecycle.sql")
        record_metric = re.search(
            r"(?is)CREATE OR REPLACE PROCEDURE SP_FINOPS_RECORD_METRIC\(.*?\n\$\$;",
            lifecycle,
        )
        self.assertIsNotNone(record_metric)
        procedure = record_metric.group(0)

        self.assertIn("V_EFFECTIVE_STATUS", procedure)
        self.assertRegex(
            procedure,
            r"(?is)NOT\s+P_IS_COMPLETE.*?FINOPS_STATUS_PRECEDENCE\(P_STATUS\).*?"
            r"FINOPS_STATUS_PRECEDENCE\('DATA_INCOMPLETE'\).*?"
            r"V_EFFECTIVE_STATUS\s*:=\s*'DATA_INCOMPLETE'",
        )
        self.assertRegex(procedure, r"(?i)'status',\s*V_EFFECTIVE_STATUS")

    def test_missing_data_is_not_coerced_to_zero_or_normal(self) -> None:
        for name in ("21_finops_check_cost.sql", "23_finops_check_warehouse.sql"):
            with self.subTest(module=name):
                sql = self.read(f"sql/20_procedures/{name}")
                self.assertIn("EXPECTED_COMPLETE_AT", sql)
                self.assertIn("SOURCE_WATERMARK", sql)
                self.assertIn("IS_COMPLETE", sql)
                self.assertIn("DATA_INCOMPLETE", sql)
                self.assertRegex(sql, r"(?i)WHEN\s+.*IS_COMPLETE.*THEN\s+COALESCE")

    def test_partial_source_publication_remains_incomplete(self) -> None:
        for name in ("21_finops_check_cost.sql", "23_finops_check_warehouse.sql"):
            with self.subTest(module=name):
                sql = self.read(f"sql/20_procedures/{name}")
                self.assertRegex(
                    sql,
                    r"(?is)V_IS_COMPLETE\s*:=\s*CURRENT_TIMESTAMP\(\)\s*"
                    r">=\s*V_EXPECTED_COMPLETE_AT\s+AND\s+"
                    r"V_SOURCE_WATERMARK\s*>=\s*V_WINDOW_END",
                )
                self.assertNotRegex(
                    sql,
                    r"(?is)V_IS_COMPLETE\s*:=.*?V_SOURCE_ROW_COUNT\s*>\s*0\s+OR",
                )

    def test_status_precedence_is_shared_by_metric_module_and_run_folding(self) -> None:
        precedence = self.read("sql/10_core/11_finops_status_precedence.sql")
        lifecycle = self.read("sql/20_procedures/20_finops_run_lifecycle.sql")
        report = self.read("sql/20_procedures/27_finops_report.sql")
        alert = self.read("sql/20_procedures/28_finops_alert.sql")
        finalizer = self.read("sql/20_procedures/29_finops_finalizer.sql")

        expected_order = (
            "FAILED",
            "DATA_INCOMPLETE",
            "ATTENTION",
            "REVIEW_REQUIRED",
            "NORMAL",
        )
        ranks = [
            int(re.search(rf"(?is)WHEN\s+'{status}'.*?THEN\s+(\d+)", precedence).group(1))
            for status in expected_order
        ]
        self.assertEqual(ranks, sorted(ranks, reverse=True))
        for sql in (lifecycle, report):
            self.assertIn("FINOPS_STATUS_PRECEDENCE", sql)
        self.assertIn("ATTENTION_REQUIRED", report)
        for sql in (report, alert, finalizer):
            self.assertIn("DATA_INCOMPLETE", sql)

    def test_slice_one_preserves_cost_policy_and_warehouse_scope(self) -> None:
        cost = self.read("sql/20_procedures/21_finops_check_cost.sql")
        warehouse = self.read("sql/20_procedures/23_finops_check_warehouse.sql")

        self.assertIn("SUM(CREDITS_USED)", cost)
        self.assertNotIn("CREDITS_USED_CLOUD_SERVICES", cost)
        self.assertIn("FINOPS_CLASSIFY_COST", cost)
        self.assertIn("REVIEW_REQUIRED", warehouse)
        self.assertNotRegex(warehouse, r"(?i)(threshold|limit)\s*[:=]\s*[0-9]")

    def test_shared_report_finalizer_and_alert_idempotency_is_preserved(self) -> None:
        report = self.read("sql/20_procedures/27_finops_report.sql")
        alert = self.read("sql/20_procedures/28_finops_alert.sql")
        finalizer = self.read("sql/20_procedures/29_finops_finalizer.sql")

        self.assertRegex(
            report,
            r"(?is)MERGE INTO FINOPS_DAILY_REPORT.*?ON target\.RUN_ID = source\.RUN_ID",
        )
        self.assertRegex(
            alert,
            r"(?is)MERGE INTO FINOPS_ALERT_DELIVERY.*?"
            r"ON target\.RUN_ID = source\.RUN_ID AND target\.CHANNEL = source\.CHANNEL",
        )
        self.assertIn("ALREADY_DELIVERED", alert)
        self.assertRegex(
            finalizer,
            r"(?is)AND NOT EXISTS\s*\(.*?FINDING_TYPE = 'TECHNICAL_FAILURE'",
        )

    def test_slice_one_docs_define_live_validation_boundary(self) -> None:
        combined = "\n".join(
            self.read(path)
            for path in (
                "README.md",
                "docs/architecture.md",
                "docs/operations/runbook.md",
                "docs/operations/finops-analytics-expansion-plan.md",
            )
        )
        for phrase in (
            "FINOPS_METRIC",
            "DATA_INCOMPLETE",
            "Snowflake compilation",
            "Account Usage freshness",
        ):
            self.assertIn(phrase, combined)

    def test_cortex_tooling_is_delivered_without_credentials(self) -> None:
        for path in (
            ".cortex/tooling.lock.json",
            "scripts/prepare_cortex_tooling.sh",
            "docs/operations/cortex-tooling.md",
        ):
            with self.subTest(path=path):
                self.assertTrue((ROOT / path).is_file(), path)

    def test_warehouse_documentation_matches_review_status(self) -> None:
        plan = self.read("docs/operations/finops-analytics-expansion-plan.md")
        warehouse = self.read("sql/20_procedures/23_finops_check_warehouse.sql")

        self.assertIn("'REVIEW_REQUIRED'", warehouse)
        self.assertNotIn(
            "Errors, Warehouse, Queries, AI Services, and Other Costs collect "
            "metrics but return `RULE_NOT_CONFIGURED`.",
            plan,
        )

    def test_snowflake_scripting_delimiters_are_balanced(self) -> None:
        for path in (ROOT / "sql").rglob("*.sql"):
            with self.subTest(path=path.relative_to(ROOT)):
                text = path.read_text(encoding="utf-8")
                self.assertEqual(text.count("$$") % 2, 0, "Unbalanced $$ delimiter")


if __name__ == "__main__":
    unittest.main()

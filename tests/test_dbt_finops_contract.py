from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class DbtFinOpsContractTests(unittest.TestCase):
    def read(self, relative_path: str) -> str:
        path = ROOT / relative_path
        self.assertTrue(path.is_file(), relative_path)
        return path.read_text(encoding="utf-8")

    def test_cost_foundation_is_complete_and_credential_free(self) -> None:
        for path in (
            "dbt/finops_analytics/dbt_project.yml",
            "dbt/finops_analytics/dbt_projects_profiles.yml",
            "dbt/finops_analytics/models/intermediate/int_finops_date_spine.sql",
            "dbt/finops_analytics/models/marts/finops_daily_cost.sql",
            "dbt/finops_analytics/models/marts/marts.yml",
            "docs/operations/dbt-finops-analytics.md",
        ):
            with self.subTest(path=path):
                self.assertTrue((ROOT / path).is_file(), path)

        profile = self.read("dbt/finops_analytics/dbt_projects_profiles.yml")
        self.assertIn("env_var('FINOPS_DBT_WAREHOUSE')", profile)
        self.assertIn("env_var('FINOPS_DBT_DATABASE', 'FINOPS_DEV')", profile)
        self.assertIn("env_var('FINOPS_DBT_SCHEMA', 'FINOPS')", profile)
        self.assertNotRegex(profile, r"(?i)(password|private_key|token)\s*:")

    def test_cost_mart_preserves_policy_and_completeness_boundaries(self) -> None:
        cost = self.read("dbt/finops_analytics/models/marts/finops_daily_cost.sql")

        self.assertIn("ref('int_finops_date_spine')", cost)
        self.assertIn("source_latest_usage_date > analysis_date", cost)
        self.assertNotIn("source_latest_usage_date >= analysis_date", cost)
        self.assertIn("ref('stg_account_usage__metering_daily_history')", cost)
        self.assertNotRegex(cost, r"(?i)(attention|threshold|0\.30|\b25\b)")

    def test_operational_task_graph_remains_unchanged_by_dbt(self) -> None:
        graph = self.read("sql/30_tasks/30_finops_task_graph.sql")
        self.assertNotRegex(graph, r"(?i)\bdbt\b")
        self.assertIn("serverless", graph.lower())

    def test_warehouse_extension_preserves_attribution_and_freshness(self) -> None:
        warehouse = self.read(
            "dbt/finops_analytics/models/marts/finops_warehouse_daily.sql"
        )

        self.assertIn("ref('stg_account_usage__warehouse_metering_history')", warehouse)
        self.assertRegex(warehouse, r"(?i)dateadd\(hour,\s*8,")
        self.assertIn("count(credits_attributed_compute_queries) = count(*)", warehouse)
        self.assertNotRegex(warehouse, r"(?i)(attention|threshold|0\.30|\b25\b)")

    def test_udtf_assessment_documents_both_proposed_contracts(self) -> None:
        guide = self.read("docs/operations/dbt-finops-analytics.md")

        for heading in (
            "### Proposed UDTF_FINOPS_COST_METRICS contract",
            "### Proposed UDTF_FINOPS_WAREHOUSE_METRICS contract",
        ):
            self.assertIn(heading, guide)

        for field in ("Inputs:", "Output columns:", "Freshness:", "Privileges:", "Example:"):
            self.assertEqual(guide.count(field), 2, field)


if __name__ == "__main__":
    unittest.main()

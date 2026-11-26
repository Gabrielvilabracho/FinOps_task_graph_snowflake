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
        for variable in (
            "DBT_SNOWFLAKE_ACCOUNT",
            "DBT_SNOWFLAKE_USER",
            "DBT_FINOPS_DBT_ROLE",
            "DBT_FINOPS_DBT_WAREHOUSE",
        ):
            with self.subTest(variable=variable):
                self.assertIn(f"env_var('{variable}')", profile)

        self.assertIn("env_var('DBT_FINOPS_DBT_DATABASE', 'FINOPS_DEV')", profile)
        self.assertIn("env_var('DBT_FINOPS_DBT_SCHEMA', 'FINOPS')", profile)
        self.assertNotRegex(profile, r"(?i)(password|private_key|token)\s*:")

    def test_native_dbt_bootstrap_is_cost_bounded_and_does_not_resume_tasks(self) -> None:
        bootstrap = self.read("sql/00_setup/04_finops_dbt_bootstrap.sql")

        for contract in (
            "WAREHOUSE_SIZE = 'XSMALL'",
            "AUTO_SUSPEND = 60",
            "AUTO_RESUME = TRUE",
            "CREATE ROLE IF NOT EXISTS FINOPS_DBT_ROLE",
            "GRANT CREATE DBT PROJECT ON SCHEMA FINOPS_DEV.FINOPS",
            "GRANT DATABASE ROLE SNOWFLAKE.USAGE_VIEWER",
            "GRANT DATABASE ROLE SNOWFLAKE.GOVERNANCE_VIEWER",
        ):
            with self.subTest(contract=contract):
                self.assertIn(contract, bootstrap)

        self.assertNotRegex(bootstrap, r"(?i)\bALTER\s+TASK\b|\bRESUME\b")

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

    def test_query_and_warehouse_sources_have_explicit_staging_contracts(self) -> None:
        sources = self.read(
            "dbt/finops_analytics/models/sources/account_usage.yml"
        )
        staging = self.read("dbt/finops_analytics/models/staging/staging.yml")

        models = {
            "query_history": "stg_account_usage__query_history.sql",
            "query_attribution_history": (
                "stg_account_usage__query_attribution_history.sql"
            ),
            "warehouse_load_history": (
                "stg_account_usage__warehouse_load_history.sql"
            ),
            "warehouse_events_history": (
                "stg_account_usage__warehouse_events_history.sql"
            ),
        }

        for source_name, filename in models.items():
            with self.subTest(source=source_name):
                self.assertIn(f"- name: {source_name}", sources)
                model_name = filename.removesuffix(".sql")
                self.assertIn(f"- name: {model_name}", staging)
                sql = self.read(
                    f"dbt/finops_analytics/models/staging/{filename}"
                )
                self.assertIn(
                    f"source('snowflake_account_usage', '{source_name}')",
                    sql,
                )

        query_history = self.read(
            "dbt/finops_analytics/models/staging/"
            "stg_account_usage__query_history.sql"
        )
        self.assertNotIn("query_text", query_history.lower())
        self.assertNotIn("bind_values", query_history.lower())

    def test_durable_query_base_reprocesses_late_attribution_safely(self) -> None:
        model = self.read(
            "dbt/finops_analytics/models/intermediate/"
            "int_finops_query_history.sql"
        )
        intermediate = self.read(
            "dbt/finops_analytics/models/intermediate/intermediate.yml"
        )

        for contract in (
            "materialized='incremental'",
            "unique_key='query_id'",
            "incremental_strategy='merge'",
            "ref('stg_account_usage__query_history')",
            "ref('stg_account_usage__query_attribution_history')",
            "dateadd(day, -2",
            "dateadd(hour, 8",
            "attribution_state",
            "is_query_history_complete",
            "is_attribution_window_complete",
        ):
            with self.subTest(contract=contract):
                self.assertIn(contract, model)

        self.assertIn("- name: int_finops_query_history", intermediate)
        self.assertNotIn("query_text", model.lower())
        self.assertNotIn("bind_values", model.lower())

    def test_daily_query_performance_uses_raw_queries_for_buckets_and_percentiles(self) -> None:
        model = self.read(
            "dbt/finops_analytics/models/marts/"
            "finops_query_performance_daily.sql"
        )
        marts = self.read("dbt/finops_analytics/models/marts/marts.yml")

        for percentile in ("0.50", "0.90", "0.99"):
            with self.subTest(percentile=percentile):
                self.assertIn(f"percentile_cont({percentile})", model)
        self.assertEqual(model.count("as number(38, 0)"), 3)

        for bucket in (
            "queries_le_1_second",
            "queries_1_to_5_seconds",
            "queries_5_to_30_seconds",
            "queries_30_to_60_seconds",
            "queries_1_to_5_minutes",
            "queries_gt_5_minutes",
        ):
            with self.subTest(bucket=bucket):
                self.assertIn(bucket, model)

        self.assertIn("ref('int_finops_query_history')", model)
        self.assertIn("- name: finops_query_performance_daily", marts)
        self.assertIn(
            "daily_query_grain_survives_warehouse_rename_and_lowercase_status",
            marts,
        )
        self.assertIn("max_by(warehouse_name, end_time)", model)
        self.assertIn("upper(execution_status)", model)
        self.assertNotIn("avg(p", model.lower())

    def test_warehouse_utilization_requires_event_and_load_evidence_for_idle_time(self) -> None:
        intervals = self.read(
            "dbt/finops_analytics/models/intermediate/"
            "int_finops_warehouse_state_intervals.sql"
        )
        utilization = self.read(
            "dbt/finops_analytics/models/marts/"
            "finops_warehouse_utilization_daily.sql"
        )
        marts = self.read("dbt/finops_analytics/models/marts/marts.yml")

        for contract in (
            "ref('stg_account_usage__warehouse_events_history')",
            "lead(event_timestamp)",
            "RESUME_WAREHOUSE",
            "SUSPEND_WAREHOUSE",
            "EVENT_BOUNDED_ESTIMATE",
        ):
            with self.subTest(interval_contract=contract):
                self.assertIn(contract, intervals)

        for contract in (
            "ref('stg_account_usage__warehouse_load_history')",
            "ref('int_finops_warehouse_state_intervals')",
            "event_bounded_on_seconds",
            "active_observed_interval_seconds",
            "estimated_idle_seconds",
            "INSUFFICIENT_EVENT_BOUNDARY",
            "INSUFFICIENT_LOAD_COVERAGE",
            "ESTIMATED_FROM_EVENT_AND_LOAD",
        ):
            with self.subTest(utilization_contract=contract):
                self.assertIn(contract, utilization)

        self.assertIn("- name: finops_warehouse_utilization_daily", marts)
        self.assertIn("Not exact billed or physical idle time", marts)

    def test_query_and_warehouse_daily_marts_have_behavioral_data_tests(self) -> None:
        required_tests = (
            "finops_query_performance_daily_unique.sql",
            "finops_query_performance_daily_bucket_reconciliation.sql",
            "int_finops_query_history_nonnegative_durations.sql",
            "finops_warehouse_utilization_daily_unique.sql",
            "finops_warehouse_utilization_daily_nonnegative.sql",
            "finops_warehouse_utilization_daily_evidence_nullability.sql",
        )

        for filename in required_tests:
            with self.subTest(test=filename):
                sql = self.read(f"dbt/finops_analytics/tests/{filename}")
                self.assertIn("{{ ref(", sql)

        marts = self.read("dbt/finops_analytics/models/marts/marts.yml")
        self.assertIn(
            "warehouse_idle_stays_null_without_complete_event_and_load_evidence",
            marts,
        )
        self.assertIn("event_bounded_on_seconds: null", marts)

    def test_weekly_and_monthly_percentiles_derive_from_raw_query_history(self) -> None:
        periods = self.read(
            "dbt/finops_analytics/models/intermediate/"
            "int_finops_query_performance_periods.sql"
        )
        weekly = self.read(
            "dbt/finops_analytics/models/marts/"
            "finops_query_performance_weekly.sql"
        )
        monthly = self.read(
            "dbt/finops_analytics/models/marts/"
            "finops_query_performance_monthly.sql"
        )
        marts = self.read("dbt/finops_analytics/models/marts/marts.yml")

        self.assertIn("ref('int_finops_query_history')", periods)
        self.assertNotIn("ref('finops_query_performance_daily')", periods)
        for percentile in ("0.50", "0.90", "0.99"):
            self.assertIn(f"percentile_cont({percentile})", periods)
        self.assertEqual(periods.count("as number(38, 0)"), 3)
        self.assertIn("period_type = 'WEEK'", weekly)
        self.assertIn("period_type = 'MONTH'", monthly)
        self.assertIn("monthly_percentile_uses_raw_queries_not_weekly_averages", marts)

    def test_warehouse_name_preserves_missing_source_values(self) -> None:
        warehouse = self.read(
            "dbt/finops_analytics/models/marts/finops_warehouse_daily.sql"
        )
        marts = self.read("dbt/finops_analytics/models/marts/marts.yml")
        warehouse_name = marts.split("- name: warehouse_name", 1)[1].split(
            "- name: raw_credits_used", 1
        )[0]

        self.assertNotIn("coalesce(warehouse_name", warehouse.lower())
        self.assertIn("may be null", warehouse_name.lower())
        self.assertNotIn("not_null", warehouse_name)

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

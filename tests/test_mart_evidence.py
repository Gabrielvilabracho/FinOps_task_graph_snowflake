"""Deterministic execution of actual mart SELECTs with a narrow SQLite dialect adapter.

This is local logic proof, not dbt compilation or Snowflake fixed-point proof.
"""
from __future__ import annotations

import re
import sqlite3
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODELS = ROOT / "dbt/finops_analytics/models/marts"


def instant(value):
    parsed = datetime.fromisoformat(value)
    return parsed.replace(tzinfo=timezone.utc) if parsed.tzinfo is None else parsed


class MartFixture:
    def __init__(self):
        self.db = sqlite3.connect(":memory:")
        self.db.row_factory = sqlite3.Row
        self.db.create_function("IFF", 3, lambda c, a, b: a if c else b)
        self.db.create_function("GREATEST", 2, lambda a, b: max(a, b)
                                if a is not None and b is not None else None)
        self.db.create_function("TO_CHAR", 2, lambda v, fmt: v[:10])
        self.db.create_function("TO_TIMESTAMP_TZ", 1, lambda v: instant(v).isoformat(" "))
        self.db.create_function("UTC_DAY", 1, lambda v: instant(v[:10]).isoformat(" "))
        self.db.create_function("CONVERT_TIMEZONE", 2,
                                lambda zone, v: instant(v).astimezone(timezone.utc).isoformat(" "))
        self.db.create_function("TO_DATE", 1, lambda v: v[:10])
        self.db.create_function("DATEADD", 3, lambda unit, n, v:
                                (instant(v) + timedelta(**{unit.lower() + "s": n})).isoformat(" "))

    def table(self, name, columns, rows):
        self.db.execute(f"CREATE TABLE {name} ({', '.join(columns)})")
        self.db.executemany(f"INSERT INTO {name} VALUES ({','.join('?' for _ in columns)})", rows)

    def run(self, model, as_of="2026-11-21 00:00:00+00:00", source=None):
        sql = source if source is not None else (MODELS / f"{model}.sql").read_text()
        sql = re.sub(r"\{\{ ref\('([^']+)'\) \}\}", r"\1", sql)
        sql = re.sub(r"(\w+(?:\.\w+)?)::timestamp_tz", r"UTC_DAY(\1)", sql, flags=re.I)
        sql = re.sub(r"dateadd\((hour|day),", r"dateadd('\1',", sql, flags=re.I)
        sql = re.sub(r"current_timestamp\(\)", ":as_of", sql, flags=re.I)
        return [dict(row) for row in self.db.execute(sql, {"as_of": as_of})]

    def close(self):
        self.db.close()


class MartEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.fixture = MartFixture()
        self.addCleanup(self.fixture.close)

    def cost(self, values, days=("2026-11-17",), as_of="2026-11-21 00:00:00+00:00"):
        self.fixture.table("stg_account_usage__metering_daily_history",
                           ("usage_date", "service_type", "credits_used_compute",
                            "credits_used_cloud_services", "credits_used",
                            "credits_adjustment_cloud_services", "credits_billed"), values)
        self.fixture.table("int_finops_date_spine", ("analysis_date",), [(d,) for d in days])
        return self.fixture.run("finops_daily_cost", as_of)

    def test_daily_raw_adjustment_and_billed_are_not_added_as_three_expenses(self):
        rows = self.cost([
            ("2026-11-16", "WAREHOUSE_METERING", 1., 0., 1., 0., 1.),
            ("2026-11-17", "WAREHOUSE_METERING", 10., 1., 11., -.5, 10.5),
            ("2026-11-18", "WAREHOUSE_METERING", 1., 0., 1., 0., 1.),
        ])
        self.assertEqual(rows[0]["raw_credits_used"], 11)
        self.assertEqual(rows[0]["cloud_services_adjustment_credits"], -.5)
        self.assertEqual(rows[0]["billed_credits"], 10.5)
        self.assertTrue(rows[0]["is_source_complete"])

    def test_missing_day_inside_history_is_unknown_not_zero(self):
        row = self.cost([
            ("2026-11-16", "WAREHOUSE_METERING", 1., 0., 1., 0., 1.),
            ("2026-11-18", "WAREHOUSE_METERING", 1., 0., 1., 0., 1.),
        ])[0]
        self.assertFalse(row["is_source_complete"])
        self.assertIsNone(row["billed_credits"])
        self.assertEqual(row["evidence_reason"], "SOURCE_PUBLICATION_ABSENT")

    def test_null_financial_component_does_not_become_complete_sum(self):
        row = self.cost([
            ("2026-11-16", "WAREHOUSE_METERING", 1., 0., 1., 0., 1.),
            ("2026-11-17", "WAREHOUSE_METERING", 1., 0., 1., None, 1.),
            ("2026-11-18", "WAREHOUSE_METERING", 1., 0., 1., 0., 1.),
        ])[0]
        self.assertFalse(row["is_source_complete"])
        self.assertIsNone(row["cloud_services_adjustment_credits"])

    def test_first_history_day_and_provisional_window_are_not_final(self):
        values = [("2026-11-17", "WAREHOUSE_METERING", 1., 0., 1., 0., 1.),
                  ("2026-11-18", "WAREHOUSE_METERING", 1., 0., 1., 0., 1.)]
        rows = self.cost(values, days=("2026-11-17", "2026-11-18"),
                         as_of="2026-11-19 00:00:00+00:00")
        self.assertTrue(all(not row["is_source_complete"] for row in rows))

    def test_observed_mature_zero_remains_zero(self):
        row = self.cost([
            ("2026-11-16", "WAREHOUSE_METERING", 1., 0., 1., 0., 1.),
            ("2026-11-17", "WAREHOUSE_METERING", 0., 0., 0., 0., 0.),
            ("2026-11-18", "WAREHOUSE_METERING", 1., 0., 1., 0., 1.),
        ])[0]
        self.assertTrue(row["is_source_complete"])
        self.assertEqual(row["billed_credits"], 0)

    def test_each_financial_component_and_exact_maturity_boundary(self):
        for missing in (None, 2, 3, 4, 5, 6):
            with self.subTest(missing_component=missing):
                fixture = MartFixture()
                try:
                    row = ["2026-11-17", "WAREHOUSE_METERING", 10., 1., 11., -.5, 10.5]
                    if missing is not None:
                        row[missing] = None
                    fixture.table("stg_account_usage__metering_daily_history",
                        ("usage_date", "service_type", "credits_used_compute", "credits_used_cloud_services",
                         "credits_used", "credits_adjustment_cloud_services", "credits_billed"),
                        [("2026-11-16", "WAREHOUSE_METERING", 1., 0., 1., 0., 1.), row,
                         ("2026-11-18", "WAREHOUSE_METERING", 1., 0., 1., 0., 1.)])
                    fixture.table("int_finops_date_spine", ("analysis_date",), [("2026-11-17",)])
                    young = fixture.run("finops_daily_cost", "2026-11-19 23:59:59+00:00")[0]
                    self.assertEqual(young["evidence_reason"], "SOURCE_NOT_EXPECTED_COMPLETE")
                    mature = fixture.run("finops_daily_cost", "2026-11-20 00:00:00+00:00")[0]
                    self.assertEqual(bool(mature["is_source_complete"]), missing is None)
                    self.assertEqual(mature["evidence_reason"],
                                     None if missing is None else "SOURCE_VALUES_INCOMPLETE")
                    self.assertEqual(mature["billed_credits"], 10.5 if missing is None else None)
                finally:
                    fixture.close()

    def test_warehouse_partial_attribution_and_signed_residual(self):
        self.fixture.table("stg_account_usage__warehouse_metering_history",
                           ("start_time", "end_time", "warehouse_id", "warehouse_name",
                            "credits_used", "credits_used_compute", "credits_used_cloud_services",
                            "credits_attributed_compute_queries"), [
            ("2026-11-17 00:00:00+00:00", "2026-11-17 01:00:00+00:00", 1, "WH", 4., 4., 0., 1.),
            ("2026-11-17 01:00:00+00:00", "2026-11-17 02:00:00+00:00", 1, "WH", 4., 4., 0., None),
            ("2026-11-17 00:00:00+00:00", "2026-11-17 01:00:00+00:00", 2, None, 1., 1., 0., 2.),
            ("2026-11-18 00:00:00+00:00", "2026-11-18 01:00:00+00:00", 2, None, 1., 1., 0., 1.),
        ])
        rows = {row["warehouse_id"]: row for row in self.fixture.run("finops_warehouse_daily")
                if row["analysis_date"] == "2026-11-17"}
        self.assertIsNone(rows[1]["compute_residual_credits"])
        self.assertIsNone(rows[1]["estimated_idle_credits"])
        self.assertEqual(rows[2]["compute_residual_credits"], -1)
        self.assertEqual(rows[2]["estimated_idle_credits"], 0)
        self.assertIsNone(rows[2]["warehouse_name"])
        self.assertEqual(rows[2]["ownership_state"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()

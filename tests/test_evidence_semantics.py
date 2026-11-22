"""Execute shipped pure SQL expressions, not a second implementation of the rules.

SQLite adapters cover only CASE, arithmetic and the scalar functions below.
These fixtures do not prove Snowflake compilation, NUMBER precision or Scripting.
"""
from __future__ import annotations

import json
import re
import sqlite3
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "sql/10_core/10_finops_cost_policy.sql"


class SqlExpressions:
    def __init__(self, source: str):
        self.connection = sqlite3.connect(":memory:")
        self.connection.create_function("IFF", 3, lambda c, a, b: a if c else b)
        self.connection.create_function(
            "OBJECT_CONSTRUCT_KEEP_NULL", -1,
            lambda *items: json.dumps(dict(zip(items[::2], items[1::2]))),
        )
        self.connection.create_function("GREATEST", 2, lambda a, b: max(a, b)
                                        if a is not None and b is not None else None)
        self.functions = {}
        pattern = r"CREATE OR REPLACE FUNCTION (\w+)\((.*?)\)\s*RETURNS.*?AS\s*\$\$(.*?)\$\$;"
        for name, parameters, body in re.findall(pattern, source, re.S | re.I):
            names = [p.strip().split()[0] for p in re.split(r",(?![^()]*\))", parameters)]
            self.functions[name, len(names)] = (names, body.strip())
        for (name, arity) in self.functions:
            self.connection.create_function(name, arity,
                                            lambda *args, n=name: self.evaluate(n, *args))

    def evaluate(self, name, *values):
        names, body = self.functions[name, len(values)]
        for parameter in sorted(names, key=len, reverse=True):
            body = re.sub(rf"\b{parameter}\b", f":{parameter}", body)
        # Snowflake NUMBER division is fractional; SQLite integer division is not.
        bindings = [float(v) if type(v) is int else v for v in values]
        return self.connection.execute("SELECT " + body, dict(zip(names, bindings))).fetchone()[0]

    def close(self):
        self.connection.close()


class EvidenceSemanticsTests(unittest.TestCase):
    def setUp(self):
        self.sql = SqlExpressions(CORE.read_text())
        self.addCleanup(self.sql.close)

    def reason(self, age=12, wait=12, rows=1, known=1, covered=True):
        return self.sql.evaluate("FINOPS_EVIDENCE_REASON", age, wait, rows, known, covered)

    def test_observed_zero_requires_maturity_history_and_non_null_values(self):
        self.assertIsNone(self.reason())
        self.assertEqual(self.reason(age=11.99), "SOURCE_NOT_EXPECTED_COMPLETE")
        self.assertEqual(self.reason(covered=False), "HISTORY_NOT_COVERED")
        self.assertEqual(self.reason(covered=None), "HISTORY_NOT_COVERED")
        self.assertEqual(self.reason(rows=0, known=0), "SOURCE_PUBLICATION_ABSENT")
        self.assertEqual(self.reason(rows=2), "SOURCE_VALUES_INCOMPLETE")
        self.assertEqual(self.reason(age=None), "SOURCE_NOT_EXPECTED_COMPLETE")
        self.assertEqual(self.reason(wait=None), "SOURCE_NOT_EXPECTED_COMPLETE")

    def test_latency_includes_cloud_services_and_streaming(self):
        self.assertEqual(self.sql.evaluate("FINOPS_METERING_WAIT_HOURS", "WAREHOUSE_METERING"), 6)
        self.assertEqual(self.sql.evaluate("FINOPS_METERING_WAIT_HOURS", "SNOWPIPE_STREAMING"), 12)
        self.assertEqual(self.sql.evaluate("FINOPS_METERING_WAIT_HOURS", None), 12)

    def test_previous_policy_thresholds_and_missing_baseline_are_preserved(self):
        for current, previous, status, growth in (
            (25, 20, "NORMAL", .25), (26, 20, "ATTENTION", .3),
            (24, 10, "ATTENTION", 1.4), (20, None, "NORMAL", None),
            (20, 0, "NORMAL", None),
        ):
            with self.subTest(current=current, previous=previous):
                result = json.loads(self.sql.evaluate("FINOPS_CLASSIFY_COST", current, previous))
                self.assertEqual(result["status"], status)
                self.assertEqual(result["growth_ratio"], growth)

    def test_cost_collector_has_independent_baseline_and_financial_basis(self):
        source = (ROOT / "sql/20_procedures/21_finops_check_cost.sql").read_text()
        for marker in ("V_PREVIOUS_REASON", "V_PREVIOUS_KNOWN_COUNT", "V_FINANCIAL_REASON",
                       "DAILY_BILLED_CREDITS", "CREDITS_ADJUSTMENT_CLOUD_SERVICES",
                       "FINOPS_EVIDENCE_REASON", "history_start", "not_additive"):
            self.assertIn(marker, source)
        self.assertNotIn("WHEN :V_IS_COMPLETE THEN COALESCE(SUM(CREDITS_USED)", source)

    def test_residual_retains_sign_but_never_invents_attribution(self):
        for compute, attributed, rows, known, expected in (
            (4, 1, 2, 2, 3), (1, 2, 2, 2, -1), (0, 0, 1, 1, 0),
            (4, 1, 2, 1, None), (4, None, 1, 0, None), (None, 1, 1, 1, None),
            (0, 0, 0, 0, None),
        ):
            with self.subTest(compute=compute, attributed=attributed, known=known):
                self.assertEqual(self.sql.evaluate("FINOPS_COMPUTE_RESIDUAL", compute,
                                                  attributed, rows, known), expected)

    def test_warehouse_uses_residual_and_preserves_legacy_aliases(self):
        source = (ROOT / "sql/20_procedures/23_finops_check_warehouse.sql").read_text()
        for marker in ("FINOPS_COMPUTE_RESIDUAL", "compute_residual_credits",
                       "attribution_known_rows", "ownership_state", "UNKNOWN",
                       "estimated_idle_credits", "estimated_idle_ratio", "COMPUTE_RESIDUAL_CREDITS"):
            self.assertIn(marker, source)
        self.assertNotIn("- COALESCE(SUM(CREDITS_ATTRIBUTED_COMPUTE_QUERIES), 0)", source)

    def test_ai_keeps_empty_null_and_unfinished_details_unknown(self):
        source = (ROOT / "sql/20_procedures/25_finops_check_ai.sql").read_text()
        self.assertNotIn("COALESCE(SUM(CREDITS), 0)", source)
        for marker in ("FINOPS_EVIDENCE_REASON", "IS_COMPLETED", "IN_PROGRESS_QUERIES",
                       "CORTEX_AI_FUNCTION_CREDITS", "USER_AI_USAGE_HISTORY",
                       "SERVICE_TYPE", "not_additive", "NOT_COLLECTED", "SOURCE_UNAVAILABLE"):
            self.assertIn(marker, source)
        self.assertNotRegex(source, r"(?i)\b(USER_ID|USER_NAME|QUERY_TEXT|QUERY_TAG|ROLE_NAMES)\b")

    def test_report_exposes_readiness_and_does_not_authorize_actions(self):
        source = (ROOT / "sql/20_procedures/27_finops_report.sql").read_text()
        for marker in ("evidence_contract", "METRICS:evidence", "scope_note", "pending_gates",
                       "No automatic remediation", "Do not sum overlapping"):
            self.assertIn(marker, source)

    def test_ai_aggregation_keeps_whole_hours_and_deduplicates_completion_join(self):
        source = (ROOT / "sql/20_procedures/25_finops_check_ai.sql").read_text()
        query = re.search(r"WITH completed_queries AS \(.*?;", source, re.S).group(0)
        query = re.sub(r"INTO :V_AI_OBSERVED.*?\n  FROM", "FROM", query, flags=re.S)
        query = query.replace("SNOWFLAKE.ACCOUNT_USAGE.CORTEX_AI_FUNCTIONS_USAGE_HISTORY", "usage_history")
        db = self.sql.connection
        db.execute("CREATE TABLE usage_history (START_TIME, CREDITS, QUERY_ID, FUNCTION_NAME, MODEL_NAME, IS_COMPLETED)")
        params = {"V_WINDOW_START": "2026-11-17", "V_WINDOW_END": "2026-11-18"}
        for case, rows, expected in (
            ("empty", [], (None, 0, 0, 0, 0, 0, 0)),
            ("observed_zero", [("2026-11-17 00", 0., "q", "f", "m", 1)], (0, 1, 1, 0, 1, 1, 1)),
            ("null_credit", [("2026-11-17 00", None, "q", "f", "m", 1)], (None, 1, 0, 0, 1, 1, 1)),
            ("running", [("2026-11-17 00", 1., "q", "f", "m", 0)], (1, 1, 1, 1, 1, 1, 1)),
            ("multi_day", [("2026-11-17 00", 1., "q", "f", "m", 0),
                           ("2026-11-17 01", .5, "q", "f", "m", 0),
                           ("2026-11-18 00", 2., "q", "f", "m", 1),
                           ("2026-11-18 01", 3., "q", "f", "m", 1)], (1.5, 2, 2, 0, 1, 1, 1)),
        ):
            with self.subTest(case=case):
                db.execute("DELETE FROM usage_history")
                db.executemany("INSERT INTO usage_history VALUES (?,?,?,?,?,?)", rows)
                self.assertEqual(db.execute(query, params).fetchone(), expected)

    def test_report_lines_surface_unknowns_without_changing_legacy_modules(self):
        source = (ROOT / "sql/20_procedures/27_finops_report.sql").read_text()
        expression = re.search(r"LISTAGG\((.*?),\s*CHAR\(10\)\)\s*WITHIN", source, re.S).group(1)
        expression = re.sub(r"METRICS:([a-z_]+(?::[a-z_]+)*)(?:::STRING)?",
                            lambda m: "json_extract(METRICS, '$." + m[1].replace(":", ".") + "')",
                            expression)
        for module, status, metrics, expected in (
            ("ERRORS", "NORMAL", {}, "ERRORS: NORMAL"),
            ("AI", "DATA_INCOMPLETE", {"evidence": {"basis": "AI_SERVICE_DETAIL",
              "reason": "SOURCE_PUBLICATION_ABSENT", "scope_note": "not all AI expense"}},
             "readiness=SOURCE_PUBLICATION_ABSENT"),
            ("COST", "DATA_INCOMPLETE", {"evidence": {"basis": "RAW_CONSUMPTION",
              "financial": {"reason": "SOURCE_SESSION_NOT_UTC"}}}, "billed=SOURCE_SESSION_NOT_UTC"),
        ):
            with self.subTest(module=module):
                line = self.sql.connection.execute(
                    "SELECT " + expression + " FROM (SELECT ? AS MODULE_NAME, ? AS STATUS, ? AS METRICS)",
                    (module, status, json.dumps(metrics))).fetchone()[0]
                self.assertIn(expected, line)

    def test_fractional_policy_strict_boundaries_for_both_existing_overloads(self):
        for current, previous, expected in ((25., 20., "NORMAL"),
                (25.001, 20., "ATTENTION"), (13., 10., "NORMAL"),
                (13.001, 10., "ATTENTION"), (0., 0., "NORMAL"),
                (24.999, None, "NORMAL")):
            for extra in ((), (25., .30)):
                with self.subTest(current=current, previous=previous, extra=extra):
                    result = json.loads(self.sql.evaluate("FINOPS_CLASSIFY_COST", current, previous, *extra))
                    self.assertEqual(result["status"], expected)
                    if not previous:
                        self.assertIsNone(result["growth_ratio"])

    def test_metric_calls_match_shared_api(self):
        calls = 0
        for path in (ROOT / "sql/20_procedures").glob("*.sql"):
            text = path.read_text()
            declared = set(re.findall(
                r"\b([VP]_\w+)\s+(?:STRING|NUMBER|FLOAT|BOOLEAN|TIMESTAMP_\w+|DATE|ARRAY|OBJECT|VARIANT)\b", text))
            for match in re.finditer(r"CALL SP_FINOPS_RECORD_METRIC\(", text):
                depth, quoted, start, items = 1, False, match.end(), []
                i = start
                while depth:
                    char = text[i]
                    if char == "'":
                        if quoted and text[i:i + 2] == "''":
                            i += 2
                            continue
                        quoted = not quoted
                    elif not quoted:
                        if char == "(":
                            depth += 1
                        elif char == ")":
                            depth -= 1
                        if (char == "," and depth == 1) or depth == 0:
                            items.append(text[start:i].strip())
                            start = i + 1
                    i += 1
                self.assertEqual(len(items), 23, path.name)
                self.assertLessEqual(set(re.findall(r":([VP]_\w+)", ",".join(items))), declared)
                self.assertIn(items[11], ("'credits'", "'ratio'"))
                calls += 1
        self.assertEqual(calls, 7)

    def test_user_ai_subset_nulls_and_optional_source_boundaries(self):
        source = (ROOT / "sql/20_procedures/25_finops_check_ai.sql").read_text()
        query = re.search(r"SELECT COUNT\(\*\), COUNT\(CREDITS\), SUM\(CREDITS\).*?;", source, re.S)[0]
        query = re.sub(r"INTO :V_USER_ROWS.*?\n    FROM", "FROM", query, flags=re.S)
        query = query.replace("SNOWFLAKE.ACCOUNT_USAGE.USER_AI_USAGE_HISTORY", "user_ai")
        db = self.sql.connection
        db.execute("CREATE TABLE user_ai(USAGE_HOUR, SERVICE_TYPE, CREDITS)")
        params = {"V_WINDOW_START": "2026-11-17", "V_WINDOW_END": "2026-11-18"}
        self.assertEqual(db.execute(query, params).fetchone(), (0, 0, None))
        db.executemany("INSERT INTO user_ai VALUES (?,?,?)", [
            ("2026-11-17 00", "AI_FUNCTIONS", .75), ("2026-11-17 01", "AI_INFERENCE", .25),
            ("2026-11-17 02", "AI_INFERENCE", None), ("2026-11-18 00", "AI_FUNCTIONS", 50.)])
        self.assertEqual(db.execute(query, params).fetchone(), (3, 2, 1.))
        self.assertEqual(self.reason(age=1, wait=1, rows=3, known=2), "SOURCE_VALUES_INCOMPLETE")
        for filename, start, end in (
                ("21_finops_check_cost.sql", "-- Optional daily financial representation", "V_FINANCIAL :="),
                ("25_finops_check_ai.sql", "-- Broader optional subset", "V_COVERAGE :=")):
            text = (ROOT / "sql/20_procedures" / filename).read_text()
            block = text[text.index(start):text.index(end)]
            self.assertIn("EXCEPTION", block)
            self.assertIn("'SOURCE_UNAVAILABLE'", block)
            self.assertNotRegex(block, r"\b(SQLERRM|SQLCODE|RAISE|SP_FINOPS_FAIL_MODULE)\b")

    def test_legacy_report_lines_match_exactly(self):
        source = (ROOT / "sql/20_procedures/27_finops_report.sql").read_text()
        expression = re.search(r"LISTAGG\((.*?),\s*CHAR\(10\)\)\s*WITHIN", source, re.S)[1]
        expression = re.sub(r"METRICS:([a-z_]+(?::[a-z_]+)*)(?:::STRING)?",
            lambda m: "json_extract(METRICS, '$." + m[1].replace(":", ".") + "')", expression)
        for module in ("ERRORS", "QUERIES", "OTHER_COSTS"):
            for status in ("NORMAL", "FAILED", "REVIEW_REQUIRED", "DATA_INCOMPLETE"):
                line = self.sql.connection.execute("SELECT " + expression +
                    " FROM (SELECT ? MODULE_NAME, ? STATUS, '{}' METRICS)",
                    (module, status)).fetchone()[0]
                self.assertEqual(line, f"{module}: {status}")


if __name__ == "__main__":
    unittest.main()

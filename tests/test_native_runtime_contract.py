"""Offline guards complement the executable Snowflake regression probes."""
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]


class NativeRuntimeContractTests(unittest.TestCase):
    def test_collectors_bind_diagnostics_and_preserve_reraise(self):
        collectors = sorted((ROOT / "sql/20_procedures").glob("2[1-6]_*.sql"))
        self.assertEqual(len(collectors), 6)
        for path in collectors:
            with self.subTest(procedure=path.name):
                source = path.read_text()
                self.assertRegex(source, r"CALL SP_FINOPS_FAIL_MODULE\([^;]*:SQLCODE::STRING, :SQLERRM\);\s*RAISE;")

    def test_report_uses_literal_newline_delimiter(self):
        source = (ROOT / "sql/20_procedures/27_finops_report.sql").read_text()
        self.assertRegex(source, re.compile(
            r"LISTAGG\(.*?,\s*'\\n'\)\s*WITHIN GROUP \(ORDER BY MODULE_NAME\)", re.S))

    def test_alert_binds_diagnostics_in_both_merge_branches(self):
        source = (ROOT / "sql/20_procedures/28_finops_alert.sql").read_text()
        handler = source.split("EXCEPTION", 1)[1]
        self.assertEqual(handler.count("LEFT(:SQLERRM, 4000)"), 2)
        self.assertIn("'error_message', LEFT(SQLERRM, 4000)", handler)

    def test_metric_call_boundaries_match_the_shared_api(self):
        cost = (ROOT / "sql/20_procedures/21_finops_check_cost.sql").read_text()
        self.assertIn(":V_GROWTH_RATIO::NUMBER(38, 9)", cost)
        self.assertIn(":V_GROWTH_THRESHOLD::NUMBER(38, 9), 'ratio'", cost)
        for filename in ("21_finops_check_cost.sql", "23_finops_check_warehouse.sql", "25_finops_check_ai.sql"):
            with self.subTest(procedure=filename):
                source = (ROOT / "sql/20_procedures" / filename).read_text()
                self.assertIn(":V_WINDOW_START::TIMESTAMP_LTZ, :V_WINDOW_END::TIMESTAMP_LTZ", source)

    def test_metric_api_preserves_fractional_values(self):
        source = (ROOT / "sql/20_procedures/20_finops_run_lifecycle.sql").read_text()
        parameters = ("P_CURRENT_VALUE", "P_PREVIOUS_VALUE", "P_BASELINE_7D_VALUE",
                      "P_BASELINE_30D_VALUE", "P_DELTA_ABSOLUTE", "P_DELTA_PERCENT", "P_THRESHOLD_VALUE")
        for parameter in parameters:
            with self.subTest(parameter=parameter):
                self.assertTrue(f"{parameter} NUMBER(38, 9)" in source,
                                f"{parameter} must preserve the persisted metric scale")

    def test_variant_findings_use_select_projection(self):
        for filename in ("20_finops_run_lifecycle.sql", "21_finops_check_cost.sql"):
            source = (ROOT / "sql/20_procedures" / filename).read_text()
            for insert in re.findall(r"INSERT INTO FINOPS_FINDING\s*\(.*?;", source, re.S):
                if "OBJECT_CONSTRUCT(" in insert:
                    self.assertNotIn(") VALUES (", insert, f"Project VARIANT expressions through SELECT in {filename}")


if __name__ == "__main__":
    unittest.main()

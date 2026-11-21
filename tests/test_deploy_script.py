import os
from pathlib import Path
import shlex
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_FILES = (
    "sql/00_setup/01_finops_objects.sql",
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
    "sql/90_validation/90_validate_deployment.sql",
)


class DeployScriptTests(unittest.TestCase):
    def test_order_is_safe_and_activation_remains_manual(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary_path = Path(temporary_directory)
            mock_bin = temporary_path / "bin"
            mock_bin.mkdir()
            call_log = temporary_path / "calls"
            snow = mock_bin / "snow"
            snow.write_text(
                '#!/bin/sh\nprintf "%s\\n" "$*" >> "$SNOW_LOG"\n',
                encoding="utf-8",
            )
            snow.chmod(0o755)
            environment = os.environ | {
                "HOME": temporary_directory,
                "TMPDIR": temporary_directory,
                "SNOW_LOG": str(call_log),
                "PATH": f"{mock_bin}:{os.environ['PATH']}",
            }

            result = subprocess.run(
                ["bash", "scripts/deploy.sh", "probe"],
                cwd=ROOT,
                env=environment,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            calls = call_log.read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(calls), 1)
            arguments = shlex.split(calls[0])
            files = [
                Path(arguments[index + 1]).relative_to(ROOT).as_posix()
                for index, argument in enumerate(arguments)
                if argument == "--filename"
            ]
            self.assertEqual(files, list(EXPECTED_FILES))
            self.assertIn("--database FINOPS_DEV", calls[0])
            self.assertIn("--schema FINOPS", calls[0])
            self.assertIn("--role FINOPS_TASK_OWNER", calls[0])
            self.assertIn("--secondary-roles NONE", calls[0])
            self.assertIn("02_finops_grants.sql", result.stdout)
            self.assertIn("03_finops_task_owner_grants.sql", result.stdout)
            self.assertIn("31_resume_finops_task_graph.sql", result.stdout)

    def test_validation_requires_all_graph_tasks_to_remain_suspended(self) -> None:
        validation = (ROOT / "sql/90_validation/90_validate_deployment.sql").read_text(
            encoding="utf-8"
        )

        self.assertIn("EXPECTED_TASK_COUNT_INVALID EXCEPTION", validation)
        self.assertIn("UPPER(\"state\") = 'SUSPENDED'", validation)
        self.assertIn("SUSPENDED_TASK_COUNT_INVALID EXCEPTION", validation)
        self.assertIn("UNEXPECTED_TASK_COUNT_INVALID EXCEPTION", validation)
        self.assertIn("WHERE \"name\" LIKE 'FINOPS_%'", validation)

    def test_task_bodies_are_delimited_for_snowflake_cli(self) -> None:
        graph = (ROOT / "sql/30_tasks/30_finops_task_graph.sql").read_text(
            encoding="utf-8"
        )

        self.assertEqual(graph.count("AS\nEXECUTE IMMEDIATE $$"), 10)
        self.assertEqual(graph.count("END;\n$$;"), 10)


if __name__ == "__main__":
    unittest.main()

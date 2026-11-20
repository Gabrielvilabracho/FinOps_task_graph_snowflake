from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
HISTORICAL_TARGET = "DATALAB" + ".SPAIN"


class FinOpsDevDeploymentTests(unittest.TestCase):
    def test_historical_target_is_not_active_configuration(self) -> None:
        for path in ROOT.rglob("*"):
            if not path.is_file() or "openwiki" in path.parts:
                continue
            if path.suffix not in {".sql", ".py", ".yml", ".yaml", ".md", ".sh"}:
                continue

            text = path.read_text(encoding="utf-8")
            if HISTORICAL_TARGET not in text:
                continue
            relative_parts = path.relative_to(ROOT).parts
            if relative_parts[:2] == ("docs", "decisions"):
                continue
            if relative_parts[:2] == ("odd", "tasks"):
                before_log = text.split("## Log", 1)[0]
                self.assertNotIn(HISTORICAL_TARGET, before_log, path)
                continue
            self.fail(f"historical target remains active in {path}")

    def test_task_owner_template_has_explicit_scoped_create_grants(self) -> None:
        grants = (
            ROOT / "sql/00_setup/03_finops_task_owner_grants.sql"
        ).read_text(encoding="utf-8")

        for privilege in (
            "CREATE TABLE",
            "CREATE VIEW",
            "CREATE FUNCTION",
            "CREATE PROCEDURE",
            "CREATE TASK",
        ):
            with self.subTest(privilege=privilege):
                self.assertIn(
                    f"GRANT {privilege} ON SCHEMA FINOPS_DEV.FINOPS "
                    "TO ROLE FINOPS_TASK_OWNER",
                    grants,
                )

        self.assertIn("GRANT EXECUTE TASK ON ACCOUNT", grants)
        self.assertIn("GRANT EXECUTE MANAGED TASK ON ACCOUNT", grants)
        self.assertIn("CREATE SCHEMA IF NOT EXISTS FINOPS_DEV.FINOPS", grants)
        self.assertIn("GRANT USAGE ON WAREHOUSE COMPUTE_WH", grants)
        self.assertIn('GRANT ROLE FINOPS_TASK_OWNER TO USER "gvilabracho"', grants)
        self.assertNotIn("FINOPS_REPO_OPERATOR", grants)

    def test_task_owner_bootstrap_creates_database_before_schema(self) -> None:
        grants = (
            ROOT / "sql/00_setup/03_finops_task_owner_grants.sql"
        ).read_text(encoding="utf-8")

        database = grants.index("CREATE DATABASE IF NOT EXISTS FINOPS_DEV")
        schema = grants.index("CREATE SCHEMA IF NOT EXISTS FINOPS_DEV.FINOPS")
        self.assertLess(database, schema)

    def test_task_owner_has_exact_account_usage_database_roles(self) -> None:
        grants = (
            ROOT / "sql/00_setup/03_finops_task_owner_grants.sql"
        ).read_text(encoding="utf-8").upper()

        database_role_grants = {
            line.strip().rstrip(";")
            for line in grants.splitlines()
            if line.strip().startswith("GRANT DATABASE ROLE SNOWFLAKE.")
        }

        self.assertEqual(
            database_role_grants,
            {
                "GRANT DATABASE ROLE SNOWFLAKE.USAGE_VIEWER "
                "TO ROLE FINOPS_TASK_OWNER",
                "GRANT DATABASE ROLE SNOWFLAKE.GOVERNANCE_VIEWER "
                "TO ROLE FINOPS_TASK_OWNER",
            },
        )

    def test_clean_install_does_not_run_redundant_column_migrations(self) -> None:
        objects = (ROOT / "sql/00_setup/01_finops_objects.sql").read_text(
            encoding="utf-8"
        )

        self.assertNotIn("ALTER TABLE FINOPS_RUN ADD COLUMN", objects)
        self.assertNotIn("ALTER TABLE FINOPS_MODULE_RUN ADD COLUMN", objects)

    def test_config_seed_parses_variant_values_outside_values_clause(self) -> None:
        objects = (ROOT / "sql/00_setup/01_finops_objects.sql").read_text(
            encoding="utf-8"
        )

        self.assertIn("PARSE_JSON(CONFIG_VALUE_JSON) AS CONFIG_VALUE", objects)
        self.assertNotIn("TO_VARIANT(25::NUMBER)", objects)

    def test_validation_fails_closed_for_invalid_tasks(self) -> None:
        validation = (
            ROOT / "sql/90_validation/90_validate_deployment.sql"
        ).read_text(encoding="utf-8")

        for exception_name in (
            "EXPECTED_TASK_COUNT_INVALID",
            "SUSPENDED_TASK_COUNT_INVALID",
            "UNEXPECTED_TASK_COUNT_INVALID",
        ):
            with self.subTest(exception_name=exception_name):
                self.assertIn(f"{exception_name} EXCEPTION", validation)
                self.assertIn(f"RAISE {exception_name}", validation)

    def test_bootstrap_precedes_clean_install_deployment(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        bootstrap = readme.index("03_finops_task_owner_grants.sql")
        deploy = readme.index("./scripts/deploy.sh")
        self.assertLess(bootstrap, deploy)


if __name__ == "__main__":
    unittest.main()

from pathlib import Path
import unittest


SQL = (
    Path(__file__).resolve().parents[1]
    / "sql/00_setup/02_finops_grants.sql"
).read_text(encoding="utf-8").upper()
ACCESS_ROLE = "GG_APP_CC_REC_DATAWARE_DMO"


class FinOpsGrantSecurityTests(unittest.TestCase):
    def test_access_role_does_not_receive_unconfirmed_runtime_privileges(self) -> None:
        forbidden = (
            f"GRANT EXECUTE TASK ON ACCOUNT TO ROLE {ACCESS_ROLE}",
            f"GRANT EXECUTE MANAGED TASK ON ACCOUNT TO ROLE {ACCESS_ROLE}",
            f"GRANT DATABASE ROLE SNOWFLAKE.USAGE_VIEWER TO ROLE {ACCESS_ROLE}",
        )
        for grant in forbidden:
            with self.subTest(grant=grant):
                self.assertNotIn(grant, SQL)

    def test_shared_schema_grants_are_object_scoped(self) -> None:
        for object_type in ("TABLES", "VIEWS", "FUNCTIONS", "PROCEDURES", "TASKS"):
            with self.subTest(object_type=object_type):
                self.assertNotIn(
                    f"ON ALL {object_type} IN SCHEMA DATALAB.SPAIN",
                    SQL,
                )
                self.assertNotIn(
                    f"ON FUTURE {object_type} IN SCHEMA DATALAB.SPAIN",
                    SQL,
                )

    def test_parent_database_grant_uses_securityadmin(self) -> None:
        database_grant = SQL.index("GRANT USAGE ON DATABASE DATALAB")
        securityadmin = SQL.index("USE ROLE SECURITYADMIN")
        sysadmin = SQL.index("USE ROLE SYSADMIN")
        self.assertLess(securityadmin, database_grant)
        self.assertLess(database_grant, sysadmin)


if __name__ == "__main__":
    unittest.main()

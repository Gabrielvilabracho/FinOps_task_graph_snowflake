import hashlib
import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_PAGES = {
    "/openwiki/quickstart.md",
    "/openwiki/architecture/task-graph.md",
    "/openwiki/concepts/state-and-cost-policy.md",
    "/openwiki/operations/deployment-and-access.md",
    "/openwiki/testing/verification.md",
    "/openwiki/workflows/daily-finops-run.md",
}


class OpenWikiArtifactsTests(unittest.TestCase):
    def test_lifecycle_is_complete_and_consistent(self) -> None:
        manifest = json.loads(
            (ROOT / "openwiki/.page-manifest.json").read_text(encoding="utf-8")
        )
        last_update = json.loads(
            (ROOT / "openwiki/.last-update.json").read_text(encoding="utf-8")
        )

        self.assertEqual(set(manifest["pages"]), EXPECTED_PAGES)
        self.assertEqual(last_update["status"], "complete")
        self.assertFalse((ROOT / "openwiki/.run.json").exists())

        for page_path, metadata in manifest["pages"].items():
            page = ROOT / page_path.removeprefix("/")
            digest = "sha256:" + hashlib.sha256(page.read_bytes()).hexdigest()
            self.assertEqual(digest, metadata["pageVersion"])

            relative_path = Path(page_path.removeprefix("/")).relative_to("openwiki")
            claims_path = (
                ROOT / "openwiki/.claims" / relative_path.with_suffix(".json")
            )
            claims = json.loads(claims_path.read_text(encoding="utf-8"))
            self.assertEqual(claims["pageVersion"], digest)
            self.assertTrue(claims["claims"])

    def test_workflow_uses_trusted_triggers_and_pinned_actions(self) -> None:
        workflow = (ROOT / ".github/workflows/openwiki-update.yml").read_text(
            encoding="utf-8"
        )
        trigger_block = workflow.split("\non:\n", 1)[1].split("\npermissions:", 1)[0]
        triggers = re.findall(r"^  ([a-z_]+):", trigger_block, re.MULTILINE)
        self.assertEqual(triggers, ["workflow_dispatch", "schedule"])
        self.assertNotIn("${{ github.event", workflow)

        action_references = re.findall(r"uses:\s*[^@\s]+@([^\s]+)", workflow)
        self.assertTrue(action_references)
        self.assertTrue(
            all(re.fullmatch(r"[0-9a-f]{40}", ref) for ref in action_references)
        )
        self.assertIn("persist-credentials: false", workflow)

    def test_task_tracking_records_openwiki_complete(self) -> None:
        spec = (ROOT / "odd/tasks/snowflake-finops-task-graph.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("- T8 · S6 · inline · complete ·", spec)


if __name__ == "__main__":
    unittest.main()

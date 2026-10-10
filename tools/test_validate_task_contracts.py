"""在隔离的题库副本中注入真实漂移，确认发布前能拦截。"""
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from validate_task_contracts import PACK, validate_suite


class TaskContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.pack = Path(cls.temp.name) / "task-suite"
        shutil.copytree(PACK, cls.pack, ignore=shutil.ignore_patterns(
            "outputs", "tmp", "__pycache__"))
        cls.originals = {}

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def tearDown(self):
        for path, data in self.originals.items():
            path.write_bytes(data)
        self.originals.clear()

    def edit_json(self, relative, mutate):
        path = self.pack / relative
        self.originals[path] = path.read_bytes()
        obj = json.loads(path.read_text(encoding="utf-8"))
        mutate(obj)
        path.write_text(json.dumps(obj, ensure_ascii=False), encoding="utf-8")

    def test_current_suite(self):
        self.assertEqual(validate_suite(self.pack)["tasks"], 30)

    def test_prompt_drift(self):
        self.edit_json("tasks/A07-transit-topology/task.json",
                       lambda s: s.update(prompt=s["prompt"] + "额外要求"))
        with self.assertRaisesRegex(ValueError, "prompt与Markdown"):
            validate_suite(self.pack)

    def test_image_dimensions_drift(self):
        self.edit_json("tasks/A01-operations-dashboard/task.json",
                       lambda s: s["required_outputs"][0].update(width=1601))
        with self.assertRaisesRegex(ValueError, "图片交付表"):
            validate_suite(self.pack)

    def test_unlisted_audit_output(self):
        self.edit_json("tasks/A01-operations-dashboard/task.json",
                       lambda s: s.update(additional_outputs=[]))
        with self.assertRaisesRegex(ValueError, "额外交付声明"):
            validate_suite(self.pack)

    def test_markdown_report_omitted_from_json(self):
        self.edit_json("tasks/A15-reference-reconstruction/task.json",
                       lambda s: s["additional_outputs"].remove("comparison.md"))
        with self.assertRaisesRegex(ValueError, "额外交付声明"):
            validate_suite(self.pack)

    def test_missing_round_reference(self):
        self.edit_json("tasks/A21-staged-launch-change/task.json",
                       lambda s: s["rounds"][1].update(requirements_file="rounds/missing.md"))
        with self.assertRaisesRegex(ValueError, "引用失效"):
            validate_suite(self.pack)

    def test_round_path_without_prefix(self):
        self.edit_json("tasks/A21-staged-launch-change/task.json",
                       lambda s: s["rounds"][1]["additional_outputs"].__setitem__(
                           0, "design-tokens.json"))
        with self.assertRaisesRegex(ValueError, "唯一轮次前缀"):
            validate_suite(self.pack)

    def test_missing_artifact_definition(self):
        self.edit_json("tasks/A09-transform-atlas/templates/audit-fields.json",
                       lambda s: s.update(artifacts={}))
        with self.assertRaisesRegex(ValueError, "字段定义与交付"):
            validate_suite(self.pack)

    def test_creative_case_delivery_drift(self):
        self.edit_json("tasks/B01-ten-real-world-showcases/task.json",
                       lambda s: s.update(case_artifacts=["final.png", "case.md"]))
        with self.assertRaisesRegex(ValueError, "用例交付清单"):
            validate_suite(self.pack)


if __name__ == "__main__":
    unittest.main()

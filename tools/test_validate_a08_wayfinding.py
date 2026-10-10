"""A08 作者校验回归：覆盖地图重设计容易再次引入的问题。"""
import copy
from pathlib import Path
import unittest

from validate_a08_wayfinding import inspect_fixture, load, validate_repository

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / "task-suite/tasks/A08-accessible-wayfinding"


class WayfindingFixtureTests(unittest.TestCase):
    def setUp(self):
        self.rows = (FOLDER / "inputs/floor.txt").read_text(encoding="utf-8-sig").splitlines()
        self.legend = copy.deepcopy(load(FOLDER / "inputs/legend.json"))

    def put(self, x, y, value):
        self.rows[y] = self.rows[y][:x] + value + self.rows[y][x + 1:]

    def test_current_fixture_and_private_reference(self):
        reference = validate_repository(ROOT)
        self.assertEqual([r["steps"] for r in reference["routes"]], [35, 47])
        self.assertEqual([run["steps"] for run in reference["shared_runs"]], [9, 8])

    def test_accidental_equal_length_shortcut_is_rejected(self):
        # 入口附近新增一个格，制造两种等长转弯走法。
        self.put(2, 12, ".")
        with self.assertRaisesRegex(ValueError, "不是唯一最短解"):
            inspect_fixture(self.rows, self.legend)

    def test_broken_theme_passage_cannot_force_backtracking(self):
        # 切断环的上方通道后仍连通，但参观路线被迫返回已走过的格子。
        self.put(12, 3, "#")
        with self.assertRaisesRegex(ValueError, "重复格或折返"):
            inspect_fixture(self.rows, self.legend)

    def test_extra_boundary_opening_is_rejected(self):
        self.put(0, 12, ".")
        with self.assertRaisesRegex(ValueError, "边界只允许"):
            inspect_fixture(self.rows, self.legend)

    def test_isolated_walkable_cell_is_rejected(self):
        self.put(1, 1, ".")
        with self.assertRaisesRegex(ValueError, "孤立可走格"):
            inspect_fixture(self.rows, self.legend)

    def test_wrong_grid_width_is_rejected(self):
        self.rows[0] = self.rows[0][:-1]
        with self.assertRaisesRegex(ValueError, "行列"):
            inspect_fixture(self.rows, self.legend)

    def test_waypoint_order_drift_is_rejected(self):
        self.legend["routes"][1]["waypoints"] = ["S", "D", "B", "E"]
        with self.assertRaisesRegex(ValueError, "必经点顺序"):
            inspect_fixture(self.rows, self.legend)


if __name__ == "__main__":
    unittest.main()

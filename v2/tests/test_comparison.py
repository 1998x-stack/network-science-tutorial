import unittest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from compare_models import compare


class ComparisonTests(unittest.TestCase):
    def test_fixed_seeds_and_summary(self):
        report = compare(40, 4, [2, 3, 5])
        self.assertEqual(len(report["runs"]), 9)
        self.assertEqual(len(report["summary"]), 3)
        self.assertEqual(report, compare(40, 4, [2, 3, 5]))
        for record in report["summary"]:
            self.assertEqual(record["summary"]["mean_degree"]["samples"], 3)

    def test_rejects_duplicate_seeds(self):
        with self.assertRaises(ValueError):
            compare(40, 4, [1, 1])


if __name__ == "__main__":
    unittest.main()

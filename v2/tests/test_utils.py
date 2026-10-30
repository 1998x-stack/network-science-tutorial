import json
from pathlib import Path
import tempfile
import unittest

from netsci.utils import artifact_digest, write_json_atomic


class UtilsTests(unittest.TestCase):
    def test_digest_order_invariant(self):
        self.assertEqual(artifact_digest({"a": 1, "b": 2}), artifact_digest({"b": 2, "a": 1}))
        self.assertNotEqual(artifact_digest({"a": 1}), artifact_digest({"a": 2}))

    def test_atomic_json_file(self):
        with tempfile.TemporaryDirectory() as dirname:
            path = Path(dirname) / "sub" / "artifact.json"
            write_json_atomic(path, {"value": "网络"})
            self.assertEqual(json.loads(path.read_text(encoding="utf-8")), {"value": "网络"})
            with self.assertRaises(ValueError):
                write_json_atomic(path, {"non_finite": float('nan')})
            self.assertEqual(json.loads(path.read_text(encoding="utf-8")), {"value": "网络"})


if __name__ == "__main__":
    unittest.main()

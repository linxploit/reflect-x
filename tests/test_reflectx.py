"""
Basic unit tests for ReflectX's core detection logic.

Run with:
    python3 -m unittest discover -s tests
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import reflectx  # noqa: E402


class TestReflectionDetection(unittest.TestCase):

    def test_raw_reflection(self):
        marker = "rfx_abc123_test"
        body = f"<html><body>Result: {marker}</body></html>"
        rtype, contexts = reflectx.detect_reflection(body, marker)
        self.assertEqual(rtype, "RAW")
        self.assertIn("html_body", contexts)

    def test_encoded_reflection(self):
        marker = "rfx_abc123_test'\"<>&"
        import html
        body = f"<html><body>Result: {html.escape(marker)}</body></html>"
        rtype, _ = reflectx.detect_reflection(body, marker)
        self.assertEqual(rtype, "ENCODED")

    def test_no_reflection(self):
        marker = "rfx_zzz999_test"
        body = "<html><body>Nothing to see here</body></html>"
        rtype, _ = reflectx.detect_reflection(body, marker)
        self.assertEqual(rtype, "NONE")

    def test_script_context(self):
        marker = "rfx_ctxtest_test"
        body = f"<script>var x = '{marker}';</script>"
        rtype, contexts = reflectx.detect_reflection(body, marker)
        self.assertEqual(rtype, "RAW")
        self.assertIn("script_block", contexts)


class TestMarkerGeneration(unittest.TestCase):

    def test_default_marker_is_alnum_safe(self):
        marker = reflectx.random_marker()
        self.assertTrue(marker.startswith("rfx_"))
        self.assertTrue(marker.endswith("_test"))
        self.assertNotIn("<", marker)
        self.assertNotIn(">", marker)

    def test_probe_chars_marker(self):
        marker = reflectx.random_marker(probe_chars=True)
        for ch in "'\"<>&":
            self.assertIn(ch, marker)


class TestRiskClassification(unittest.TestCase):

    def test_risk_levels(self):
        result = reflectx.ScanResult(url="http://x", param="q", marker="m")
        result.reflection_type = "RAW"
        self.assertEqual(result.risk[0], "HIGH")

        result.reflection_type = "NONE"
        self.assertEqual(result.risk[0], "SAFE")


if __name__ == "__main__":
    unittest.main()

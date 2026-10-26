"""check_links 的行為測試：每個案例對應一個實際會誤判或漏檢的輸入。"""

from __future__ import annotations

import re
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))

import check_links  # noqa: E402


class CheckDocument(unittest.TestCase):
    def check(self, text: str, files: tuple[str, ...] = ("other.md",)) -> list[str]:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name in files:
                (root / name).write_text("x", encoding="utf-8")
            doc = root / "doc.md"
            doc.write_text(text, encoding="utf-8")
            return check_links.check_document(doc, root)

    def test_plain_existing_link_ok(self):
        self.assertEqual(self.check("[a](other.md)"), [])

    def test_missing_link_reported(self):
        self.assertEqual(len(self.check("[a](nope.md)")), 1)

    def test_link_with_title_is_not_a_false_failure(self):
        self.assertEqual(self.check('[a](other.md "標題")'), [])

    def test_missing_link_with_title_still_reported(self):
        self.assertEqual(len(self.check('[a](nope.md "標題")')), 1)

    def test_angle_bracket_target_with_space(self):
        self.assertEqual(self.check("[a](<my file.md>)", ("my file.md",)), [])

    def test_link_inside_fenced_code_is_ignored(self):
        self.assertEqual(self.check("```text\n[a](nope.md)\n```\n"), [])

    def test_link_inside_inline_code_is_ignored(self):
        self.assertEqual(self.check("範例 `[a](nope.md)` 不是連結"), [])

    def test_link_after_closed_fence_is_checked_again(self):
        self.assertEqual(len(self.check("```\nx\n```\n[a](nope.md)")), 1)

    def test_reference_style_definition_is_checked(self):
        self.assertEqual(len(self.check("[a][r]\n\n[r]: nope.md\n")), 1)
        self.assertEqual(self.check("[a][r]\n\n[r]: other.md\n"), [])

    def test_wrong_case_is_reported_even_on_case_insensitive_fs(self):
        # Windows／macOS 上 Other.md 會解析到 other.md，GitHub（Linux）上不會。
        self.assertEqual(len(self.check("[a](Other.md)")), 1)

    def test_anchor_only_and_external_skipped(self):
        self.assertEqual(self.check("[a](#x) [b](https://example.com/x.md)"), [])


if __name__ == "__main__":
    unittest.main()

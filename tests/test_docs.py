"""README／CHECKLIST 的內容性質：中英鏡像一致、範例程式不藏已知陷阱。"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


class Playbook(unittest.TestCase):
    def read(self, name: str) -> str:
        return (REPO / name).read_text(encoding="utf-8")

    def code_blocks(self, name: str) -> list[str]:
        return re.findall(r"```\w*\n(.*?)```", self.read(name), re.S)

    def test_readme_code_blocks_match_between_languages(self):
        self.assertEqual(self.code_blocks("README.md"), self.code_blocks("README.en.md"))

    def test_list_id_union_is_case_sensitive(self):
        # GraphQL node ID 是區分大小寫的 base64；Sort-Object -Unique 預設不分大小寫，
        # 兩個只差大小寫的 ID 會被併成一個，mutation 就少送一個既有 List。
        for name in ("README.md", "README.en.md"):
            for line in self.read(name).splitlines():
                if "Sort-Object" in line and "-Unique" in line:
                    self.assertIn("-CaseSensitive", line, f"{name}: {line.strip()}")

    def test_checklist_unique_coverage_item_is_conditional(self):
        # README 把「每個 starred repo 都進 List」列為可選策略，且允許保留未分類；
        # 清單不可把它寫成無條件必過項目。
        for line in self.read("CHECKLIST.md").splitlines():
            if "Unique List repository IDs" in line:
                self.assertRegex(line, r"若|需要")

    def test_lists_query_is_paginated_like_every_other_connection(self):
        for name in ("README.md", "README.en.md"):
            block = next(b for b in self.code_blocks(name) if "lists(first" in b)
            self.assertIn("pageInfo", block, name)


if __name__ == "__main__":
    unittest.main()

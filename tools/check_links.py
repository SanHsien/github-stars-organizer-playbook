#!/usr/bin/env python3
"""檢查 Markdown 之間的相對連結指得到東西。

這個 repo 是一份 runbook：README 是主文、CHECKLIST 是執行時逐項打勾的清單、
README.en 是英文鏡像，三份互相連來連去。文件被重新定位或改名時，這些連結
會靜靜地斷掉——runbook 讀到一半點不開的那一刻，才是最不該發現的時候。

只驗相對連結。外部網址交給人看：連 GitHub 官方文件的網址檢查會受限流與改版
影響，變成每隔一陣子就紅一次卻不是自己出錯的雜訊。

    python tools/check_links.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent.parent
LINK_PATTERN = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
SKIP_PREFIXES = ("http://", "https://", "mailto:", "tel:", "#")


def check_document(path: Path) -> list[str]:
    problems: list[str] = []
    for match in LINK_PATTERN.finditer(path.read_text(encoding="utf-8")):
        target = match.group(1).strip()
        if not target or target.startswith(SKIP_PREFIXES):
            continue
        # 去掉錨點：連到 other.md#section 時只驗檔案存在。
        file_part = unquote(target.split("#", 1)[0])
        if not file_part:
            continue
        resolved = (path.parent / file_part).resolve()
        if not resolved.exists():
            problems.append(f"{target} → 找不到 {resolved.relative_to(ROOT) if ROOT in resolved.parents else resolved}")
    return problems


def main() -> int:
    documents = sorted(ROOT.glob("*.md"))
    if not documents:
        print("找不到任何 Markdown 檔")
        return 1

    failures = 0
    for path in documents:
        problems = check_document(path)
        if problems:
            failures += 1
            for problem in problems:
                print(f"FAIL {path.name}: {problem}")
        else:
            print(f"OK   {path.name}")

    print(f"\n共 {len(documents)} 份文件，{failures} 份有斷掉的相對連結。")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())

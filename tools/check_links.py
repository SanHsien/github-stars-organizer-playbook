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
# 目標可以是 <含空白的路徑>，也可以是不含空白的路徑；其後可跟 "標題"／'標題'／(標題)。
LINK_PATTERN = re.compile(
    r"\[[^\]]*\]\(\s*(<[^>\n]*>|[^)\s]*)"
    r"(?:\s+(?:\"[^\"]*\"|'[^']*'|\([^)]*\)))?\s*\)"
)
REFERENCE_PATTERN = re.compile(r"^ {0,3}\[(?!\^)[^\]]+\]:\s*(<[^>\n]*>|\S+)", re.MULTILINE)
FENCE_PATTERN = re.compile(r"^ {0,3}(`{3,}|~{3,})")
INLINE_CODE_PATTERN = re.compile(r"(`+)(?:(?!\1).)+?\1")
SKIP_PREFIXES = ("http://", "https://", "mailto:", "tel:", "#")


def strip_code(text: str) -> str:
    """去掉 fenced code 與 inline code：裡面的 [x](y) 是範例，不是連結。"""
    kept: list[str] = []
    fence: str | None = None
    for line in text.splitlines():
        match = FENCE_PATTERN.match(line)
        if fence is None:
            if match:
                fence = match.group(1)
                continue
            kept.append(INLINE_CODE_PATTERN.sub("", line))
        elif (
            match
            and match.group(1)[0] == fence[0]
            and len(match.group(1)) >= len(fence)
            and not line.strip()[len(match.group(1)):].strip()  # 收尾圍欄不可帶 info string
        ):
            fence = None
    return "\n".join(kept)


def exists_exact(base: Path, relative: str) -> bool:
    """存在，且每一段的大小寫都和磁碟上一致。

    Windows／macOS 的檔案系統不分大小寫，`[x](readme.md)` 在本機通過，
    推上 GitHub（Linux）就斷掉；只有逐段比對實際目錄清單才抓得到。
    """
    current = base.resolve()
    for part in Path(relative).parts:
        if part in ("", "."):
            continue
        if part == "..":
            current = current.parent
            continue
        if not current.is_dir() or part not in {entry.name for entry in current.iterdir()}:
            return False
        current = current / part
    return True


def check_document(path: Path, root: Path = ROOT) -> list[str]:
    problems: list[str] = []
    text = strip_code(path.read_text(encoding="utf-8"))
    targets = [m.group(1) for m in LINK_PATTERN.finditer(text)]
    targets += [m.group(1) for m in REFERENCE_PATTERN.finditer(text)]
    for target in targets:
        target = target.strip()
        if target.startswith("<") and target.endswith(">"):
            target = target[1:-1].strip()
        if not target or target.startswith(SKIP_PREFIXES):
            continue
        # 去掉錨點：連到 other.md#section 時只驗檔案存在。
        file_part = unquote(target.split("#", 1)[0])
        if not file_part:
            continue
        if not exists_exact(path.parent, file_part):
            resolved = (path.parent / file_part).resolve()
            shown = resolved.relative_to(root) if root in resolved.parents else resolved
            problems.append(f"{target} → 找不到 {shown}")
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

# 路線圖

> 本 repo 後續工作的單一真相源。做完一項，就在同一個 commit 刪掉那一列；新工作只加在這裡。
> 現況段的數字是 2026-10-29 依 `main` `347a77d92948` 查的快照，開工前先重查 GitHub。

## 現況

純文件 repo（public、非 fork、無 release）：GitHub Stars Lists 分類、GraphQL 批次更新與驗證流程的 playbook，只有 `tools/check_links.py` 一支程式。2026-10-29 無 open issue／PR、Dependabot 與 Code scanning 告警皆 0，`main` 上 CI 與 CodeQL 最近一次皆 success（2026-10-29 `gh` 查詢）；沒有未完成線索，維持現狀。

## 近期：可以直接動手
| 項目 | 為什麼 | 驗收方式 | 建議執行者 | 證據 |
| --- | --- | --- | --- | --- |
| 無 | 深掃（2026-10-26）已修完連結檢查、README 與 CHECKLIST 的矛盾，並補單元測試；沒有 TODO／FIXME，不為了有事做而加工作 | 不適用 | 不適用 | commits `7a2c5a8`、`02d24d6`、`c61adce`；`.github/workflows/ci.yml:41,44` |

## 中期：等條件成立再做
| 項目 | 觸發條件 | 驗收方式 | 建議執行者 | 證據 |
| --- | --- | --- | --- | --- |
| 依實際套用 Stars Lists 的經驗修訂 README／CHECKLIST | 有 agent 或維護者照 playbook 實際跑一次分類，遇到文件沒涵蓋的 API 行為或失敗（例如 GraphQL schema 變動、分頁邊界） | 修訂處附可重現的觀察；`python -m unittest discover -s tests -v` 與 `python tools/check_links.py` 皆 exit 0；`README.md` 與 `README.en.md` 程式碼區塊一致（`tests/test_docs.py` 擋） | Claude Sonnet | `tests/test_docs.py`；`CHECKLIST.md` |
| 補錨點（`file.md#section`）驗證 | 文件出現因錨點改名而斷掉的連結 | `tools/check_links.py` 對錨點的測試（含 GitHub slug 規則）通過且不新增誤報 | Claude Sonnet | `tools/check_links.py` 註解（只驗檔案存在是設計取捨）；深掃報告（2026-10-26）「刻意不修」 |

## 刻意不做
| 不做什麼 | 理由 | 什麼情況下重新考慮 |
| --- | --- | --- |
| 切 release 或補 tag | 純文件 repo，沒有版本發佈需求 | 此 playbook 要被外部引用且需要固定版本時 |
| 為了讓稽核變綠而加裝飾性 workflow | CI 的連結檢查、單元測試與 CodeQL 已涵蓋唯一的程式與文件 | 不重新考慮 |
| 讓 `check_links.py` 驗證 repo 外的 `../` 路徑 | 只處理自己 repo 的根目錄 Markdown，無實際風險 | 此 repo 的文件開始連到其他 repo 的檔案時 |

## 維護方式

自有 repo：Dependabot 處理 Actions 與 CodeQL action 升級，合併前先看 diff 並確認 CI 綠；內容改動以 `python -m unittest discover -s tests -v` 與 `python tools/check_links.py` 為閘門。

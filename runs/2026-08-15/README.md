# SanHsien Stars 未分類盤點（2026-08-15）

這是一次 **read-only inventory + dry-run**。尚未建立新 List，也尚未呼叫 `updateUserListsForItem`。

依 playbook：必須先產出 dry-run，取得帳號本人明確授權，並由本人完成 GitHub OAuth／裝置碼後，才能寫入。

## 執行紀錄

| 項目 | 值 |
|---|---|
| GitHub 帳號 | `SanHsien` |
| 執行日期 | 2026-08-15 |
| Stars UI | 537 |
| `starredRepositories` | 535（已完整分頁） |
| Starred topics 差額 | 2（平台限制，不列為 repository 漏分） |
| 既有 Lists | 19（與 2026-07-28 相同，無預期外名稱） |
| Unique repositories in Lists | 512 |
| 未分類 repositories | **23** |
| Memberships | 525 |
| 額外 memberships（多重分類） | 13（12 個 repo 跨 List） |
| 此環境 GitHub CLI 帳號 | `cursor`（**不是** `SanHsien`） |
| 原始 token scopes | 雲端 agent 代管 token；未對 SanHsien 帳號新增 `user` scope |
| 寫入狀態 | 未執行 |

與 2026-07-28 比較：當時 513 筆全部入 List。此次 starred repositories 增至 535，unique listed 為 512（`ML Models & Research` 由 66 降為 65），代表期間約新增 23 筆 star，並有 1 筆已分類 repository 被 unstar。Lists 中沒有「已入 List 但未 star」的殘留。

GraphQL schema 仍提供 `createUserList` 與 `updateUserListsForItem`（`listIds` 為更新後完整集合）。

## 停止條件檢查

| 條件 | 結果 |
|---|---|
| 預期外的 List 名稱 | 無 |
| repository 數突然下降 | 無（535 > 513） |
| required List 不存在 | 既有 19 張都在；**建議新增** `Finance, Quant & Trading` |
| 未分類數量異常 | 23，與新增 star 規模相符 |
| memberships 完整分頁 | 是（`AI Agents & Coding` 117 筆已翻頁） |
| GitHub account 與指定帳號 | 目標帳號 `SanHsien` 的公開資料可讀；寫入身分不符 |

## 建議分類架構調整

未分類 23 筆中有 **10 筆量化金融／交易／預測市場**，既有 19 類無法乾淨容納（若硬塞，AI 交易框架會混進 coding agents，qlib／Lean 會混進通用 ML 或 Data）。

建議新增公開 List：

| List | Description |
|---|---|
| Finance, Quant & Trading | Quantitative finance, algorithmic trading, prediction markets, and investment research. |

分類優先序建議把 finance／quant／trading 視為高辨識度領域，與 Taiwan、hardware 同級，因此「AI 交易 agent」歸金融，不歸 `AI Agents & Coding`。

**此 List 尚未建立。** 若否決新增，見文末 fallback。

## Dry-run 摘要

| 項目 | 數量 |
|---|---:|
| starred repositories | 535 |
| existing lists | 19 |
| already classified | 512 |
| updates required | 23 |
| unclassified after plan | 0 |
| 建議新建 List | 1 |
| 新 memberships | 25（含 2 筆雙重分類） |
| 套用後 unique listed | 535 |
| 套用後 memberships | 550 |

雙重分類（`existing ∪ desired`，目前 existing 皆為空）：

- `gkfriend/codex-usage-companion` → `AI Agents & Coding` ∪ `Windows & Local-first`（比照 `nesszer/Win-CodexBar`）
- `Docat0209/qlib-tw-trader` → `Taiwan & Traditional Chinese` ∪ `Finance, Quant & Trading`

## 23 筆建議歸類

| Repository | 建議 List | 信心 | 說明 |
|---|---|---|---|
| [PeterPorzuczek/chatgpt-panel-chrome-extension](https://github.com/PeterPorzuczek/chatgpt-panel-chrome-extension) | AI Agents & Coding | 高 | ChatGPT 側邊欄 |
| [gkfriend/codex-usage-companion](https://github.com/gkfriend/codex-usage-companion) | AI Agents & Coding, Windows & Local-first | 高 | Codex Desktop 用量面板 |
| [xikhar/persona](https://github.com/xikhar/persona) | Voice, Video & Media | 高 | 桌面即時語音角色 |
| [herdrdev/herdr](https://github.com/herdrdev/herdr) | AI Agents & Coding | 高 | coding agents runtime |
| [kirodotdev/KiroCrew](https://github.com/kirodotdev/KiroCrew) | AI Agents & Coding | 高 | 持續型 agent 工作區 |
| [cloudflare/computer](https://github.com/cloudflare/computer) | AI Agents & Coding | 中 | 給 agent 的 sandbox 電腦；可改 DevOps |
| [chenlu-hung/my-skills](https://github.com/chenlu-hung/my-skills) | AI Agents & Coding | 高 | Claude Code skills |
| [drpwchen/claude-pacer](https://github.com/drpwchen/claude-pacer) | AI Agents & Coding | 高 | Claude Code 用量 guard |
| [stablyai/orca](https://github.com/stablyai/orca) | AI Agents & Coding | 高 | 平行 agents ADE |
| [hamanpaul/paulsha-cortex](https://github.com/hamanpaul/paulsha-cortex) | AI Agents & Coding | 高 | agent 治理平面 |
| [Hao0321/video-autopilot-kit](https://github.com/Hao0321/video-autopilot-kit) | Voice, Video & Media | 高 | YouTube／ffmpeg 影片自動化 |
| [goldmansachs/gs-quant](https://github.com/goldmansachs/gs-quant) | Finance, Quant & Trading | 高 | 量化金融 toolkit |
| [microsoft/qlib](https://github.com/microsoft/qlib) | Finance, Quant & Trading | 中 | AI 量化平台；可改 ML |
| [QuantConnect/Lean](https://github.com/QuantConnect/Lean) | Finance, Quant & Trading | 高 | 演算法交易引擎 |
| [TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents) | Finance, Quant & Trading | 高 | 多 agent 交易框架 |
| [virattt/ai-hedge-fund](https://github.com/virattt/ai-hedge-fund) | Finance, Quant & Trading | 高 | AI hedge fund |
| [NoFxAiOS/nofx](https://github.com/NoFxAiOS/nofx) | Finance, Quant & Trading | 高 | AI 交易終端 |
| [Jon-Becker/prediction-market-analysis](https://github.com/Jon-Becker/prediction-market-analysis) | Finance, Quant & Trading | 高 | 預測市場資料 |
| [pmxt-dev/pmxt](https://github.com/pmxt-dev/pmxt) | Finance, Quant & Trading | 高 | 預測市場交易 API |
| [TraderAlice/OpenAlice](https://github.com/TraderAlice/OpenAlice) | Finance, Quant & Trading | 高 | AI 交易 agent |
| [Docat0209/qlib-tw-trader](https://github.com/Docat0209/qlib-tw-trader) | Taiwan & Traditional Chinese, Finance, Quant & Trading | 高 | 台股量化 |
| [ossf/best-practices-badge](https://github.com/ossf/best-practices-badge) | Security & Privacy | 高 | OpenSSF 安全徽章 |
| [agentcrew-academy/harness-starter-kit](https://github.com/agentcrew-academy/harness-starter-kit) | AI Agents & Coding | 高 | Claude／Codex hooks；繁中 README 不加 Taiwan |

機器自動分類後，已對模糊項目讀 README 首段。無需硬塞的項目為 0；2 筆標為人工覆核（見上表信心「中」）。

## 套用後各 List 預估數

| List | 目前 | 預估 |
|---|---:|---:|
| AI Agents & Coding | 117 | 127 |
| ML Models & Research | 65 | 65 |
| Voice, Video & Media | 63 | 65 |
| Stickers & Creative Tools | 49 | 49 |
| LINE & Chatbots | 43 | 43 |
| Taiwan & Traditional Chinese | 27 | 28 |
| Windows & Local-first | 25 | 26 |
| Automation & Productivity | 24 | 24 |
| Security & Privacy | 21 | 22 |
| Fonts & Typography | 16 | 16 |
| Translation & Language | 14 | 14 |
| Data, Docs & Knowledge | 12 | 12 |
| Utilities & System Tools | 11 | 11 |
| Web & App Development | 11 | 11 |
| **Finance, Quant & Trading** | 0（未建） | **10** |
| Learning & Awesome Lists | 8 | 8 |
| Mobile & Cross-platform | 6 | 6 |
| DevOps & Self-hosting | 5 | 5 |
| Games & Fun | 5 | 5 |
| Hardware & IoT | 3 | 3 |

## 寫入尚未執行的原因

1. 此雲端 agent 的 `gh` active account 是 `cursor`，不能改 SanHsien 的 User Lists。
2. Playbook 禁止在使用者明確授權前建立 List 或改 memberships。
3. GitHub 登入、裝置碼與 OAuth 確認必須由 `SanHsien` 本人操作。

授權後下一 agent 應：

1. 以 `SanHsien` 登入，必要時暫時加上 `user` scope。
2. 確認是否建立 `Finance, Quant & Trading`，以及 `cloudflare/computer`、`microsoft/qlib` 的歸類。
3. 重新分頁讀取遠端 Lists／memberships，**不要**直接沿用本計畫中的過期 ID 硬跑。
4. 先 `createUserList`，再用 GitHub 回傳的 node ID。
5. 每筆送出 `existing_list_ids ∪ desired_list_ids`，每批約 10 筆。
6. 寫入後重新抓取，驗證 unique List repository IDs == 535。
7. 移除臨時 `user` scope，刪除含 token 的暫存檔。

機器可讀計畫見 [`plan.json`](plan.json)。本目錄不含 token、裝置碼或完整 starred dump。

## Fallback：不新增 Finance List

| Repository | Fallback List |
|---|---|
| goldmansachs/gs-quant | Data, Docs & Knowledge |
| microsoft/qlib | ML Models & Research |
| QuantConnect/Lean | Data, Docs & Knowledge |
| TauricResearch/TradingAgents | AI Agents & Coding |
| virattt/ai-hedge-fund | AI Agents & Coding |
| NoFxAiOS/nofx | AI Agents & Coding |
| Jon-Becker/prediction-market-analysis | Data, Docs & Knowledge |
| pmxt-dev/pmxt | Web & App Development |
| TraderAlice/OpenAlice | AI Agents & Coding |
| Docat0209/qlib-tw-trader | Taiwan & Traditional Chinese, ML Models & Research |

其餘 13 筆與建議方案相同。此 fallback 會把交易 agent 混進 coding agents，不建議除非明確拒絕新 List。

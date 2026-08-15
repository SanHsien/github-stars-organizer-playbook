# SanHsien Stars 未分類整理（2026-08-15）

狀態：**已寫入並通過完整分頁驗證。** 新建 [Finance, Quant & Trading](https://github.com/stars/SanHsien/lists/finance-quant-trading)。未 unstar、未刪除既有 Lists。

## 最終結果

| 項目 | 寫入前 | 寫入後 |
|---|---:|---:|
| Stars UI | 537 | 537 |
| Starred repositories | 535 | 535 |
| Starred topics 差額 | 2 | 2 |
| Lists | 19 | 20 |
| Unique repositories in Lists | 512 | **535** |
| 未分類 repositories | 23 | **0** |
| Memberships | 525 | 550 |
| 跨 List repositories | 12 | 14 |

驗證：

- unique(List repository IDs) == starredRepositories.totalCount
- missing repository IDs == 0
- 23 筆目標 membership 全部存在
- 原有 memberships 全部仍在（lost = 0）
- topics 差額 2 不列為漏分

## 執行紀錄

| 項目 | 值 |
|---|---|
| GitHub 帳號 | `SanHsien` |
| 執行日期 | 2026-08-15 |
| 寫入身分 | `viewer.login == SanHsien` |
| 臨時 OAuth scope | 寫入時含 `user`；本環境已 `gh auth logout --user SanHsien` 刪除本地 token |
| GraphQL | `createUserList`、`updateUserListsForItem` 仍可用；`listIds` 為完整集合 |
| 批次 | 10 + 10 + 3，無 GraphQL errors |
| 新建 List ID | `UL_kwDOAgphSs4AhlP_`（slug: `finance-quant-trading`） |

寫入前重新分頁讀取遠端狀態，未沿用過期計畫硬跑。分類決策沿用已確認的 dry-run（含 `cloudflare/computer` → AI Agents、`microsoft/qlib` → Finance）。

## 寫入後各 List 數量

| List | Count |
|---|---:|
| AI Agents & Coding | 127 |
| ML Models & Research | 65 |
| Voice, Video & Media | 65 |
| Stickers & Creative Tools | 49 |
| LINE & Chatbots | 43 |
| Taiwan & Traditional Chinese | 28 |
| Windows & Local-first | 26 |
| Automation & Productivity | 24 |
| Security & Privacy | 22 |
| Fonts & Typography | 16 |
| Translation & Language | 14 |
| Data, Docs & Knowledge | 12 |
| Utilities & System Tools | 11 |
| Web & App Development | 11 |
| Finance, Quant & Trading | 10 |
| Learning & Awesome Lists | 8 |
| Mobile & Cross-platform | 6 |
| DevOps & Self-hosting | 5 |
| Games & Fun | 5 |
| Hardware & IoT | 3 |

## 23 筆實際歸類

| Repository | List |
|---|---|
| [PeterPorzuczek/chatgpt-panel-chrome-extension](https://github.com/PeterPorzuczek/chatgpt-panel-chrome-extension) | AI Agents & Coding |
| [gkfriend/codex-usage-companion](https://github.com/gkfriend/codex-usage-companion) | AI Agents & Coding ∪ Windows & Local-first |
| [xikhar/persona](https://github.com/xikhar/persona) | Voice, Video & Media |
| [herdrdev/herdr](https://github.com/herdrdev/herdr) | AI Agents & Coding |
| [kirodotdev/KiroCrew](https://github.com/kirodotdev/KiroCrew) | AI Agents & Coding |
| [cloudflare/computer](https://github.com/cloudflare/computer) | AI Agents & Coding |
| [chenlu-hung/my-skills](https://github.com/chenlu-hung/my-skills) | AI Agents & Coding |
| [drpwchen/claude-pacer](https://github.com/drpwchen/claude-pacer) | AI Agents & Coding |
| [stablyai/orca](https://github.com/stablyai/orca) | AI Agents & Coding |
| [hamanpaul/paulsha-cortex](https://github.com/hamanpaul/paulsha-cortex) | AI Agents & Coding |
| [Hao0321/video-autopilot-kit](https://github.com/Hao0321/video-autopilot-kit) | Voice, Video & Media |
| [goldmansachs/gs-quant](https://github.com/goldmansachs/gs-quant) | Finance, Quant & Trading |
| [microsoft/qlib](https://github.com/microsoft/qlib) | Finance, Quant & Trading |
| [QuantConnect/Lean](https://github.com/QuantConnect/Lean) | Finance, Quant & Trading |
| [TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents) | Finance, Quant & Trading |
| [virattt/ai-hedge-fund](https://github.com/virattt/ai-hedge-fund) | Finance, Quant & Trading |
| [NoFxAiOS/nofx](https://github.com/NoFxAiOS/nofx) | Finance, Quant & Trading |
| [Jon-Becker/prediction-market-analysis](https://github.com/Jon-Becker/prediction-market-analysis) | Finance, Quant & Trading |
| [pmxt-dev/pmxt](https://github.com/pmxt-dev/pmxt) | Finance, Quant & Trading |
| [TraderAlice/OpenAlice](https://github.com/TraderAlice/OpenAlice) | Finance, Quant & Trading |
| [Docat0209/qlib-tw-trader](https://github.com/Docat0209/qlib-tw-trader) | Taiwan & Traditional Chinese ∪ Finance, Quant & Trading |
| [ossf/best-practices-badge](https://github.com/ossf/best-practices-badge) | Security & Privacy |
| [agentcrew-academy/harness-starter-kit](https://github.com/agentcrew-academy/harness-starter-kit) | AI Agents & Coding |

## OAuth 收尾

本雲端環境已登出 `SanHsien`，本地不再保存該帳號 token。`gh auth logout` **不會撤銷** GitHub 上的 OAuth grant。若要撤銷 GitHub CLI 這次授權（含 `user` scope），請到 [Authorized OAuth apps](https://github.com/settings/applications) 對 **GitHub CLI** 選擇 Revoke Access。注意這會撤銷所有裝置上由 GitHub CLI 產生的 token。

機器可讀驗證見 [`verify.json`](verify.json)。本目錄不含 token、裝置碼或完整 starred dump。

# AGENTS.md

本 repository 是 GitHub Stars Lists 安全整理流程的可重用規格。

執行任務前先閱讀：

- [`README.md`](README.md)：流程、安全邊界與核心 GraphQL 契約。
- [`CHECKLIST.md`](CHECKLIST.md)：實際執行時的逐項核對表。

AI agent 必須遵守：

1. 使用繁體中文與使用者溝通，除非使用者明確要求其他語言。
2. 先做 read-only inventory 與 dry-run；未確認計畫前不得建立 Lists 或修改 memberships。
3. `updateUserListsForItem.listIds` 必須是既有與目標 List IDs 的完整聯集，不可破壞原有多重分類。
4. starred repositories 與每張 UserList 都必須完整分頁讀取與驗證。
5. 自動分類後人工覆核未命中與模糊項目；不確定時保留未分類，不硬猜。
6. mutation 失敗時重新讀取遠端狀態，重新產生 idempotent plan，不使用過期計畫續跑。
7. 完成後重新抓取遠端資料驗證 desired memberships、原始 memberships 與 unexpected removals。
8. GitHub OAuth、裝置碼與登入確認必須由使用者本人操作；不得記錄 token、API key 或裝置碼。
9. 任務結束後移除臨時 OAuth scope 並清除暫存分類資料。
10. 不 unstar、不刪除既有 Lists，也不把 Stars UI 與 GraphQL 數量差異在沒有證據時直接報成 repository 遺漏。

文件維護原則：

- README 保留可重用流程，不放使用者個人某次執行的歷史統計快照。
- CHECKLIST 只維護執行順序，不重複 README 的完整教學。
- CLAUDE.md 只作為 Claude Code 薄入口。
- GitHub GraphQL schema、OAuth scope 或 Stars UI 若變更，以最新官方文件與 live introspection 為準，再同步更新 README。

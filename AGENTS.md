# AGENTS.md

本 repository 是 GitHub Stars Lists 整理流程的單一真相源。

AI agent 執行任務前必須完整閱讀 [`README.md`](README.md)，並遵守：

1. 使用繁體中文與使用者溝通。
2. 先做 read-only inventory 與 dry-run，取得明確授權後才建立 Lists 或修改 memberships。
3. `updateUserListsForItem` 必須送出既有與目標 List IDs 的聯集，不可破壞原有多重分類。
4. starred repositories 與每張 UserList 都必須分頁讀取。
5. 自動分類後必須人工覆核未命中與模糊項目。
6. 批次 mutation 失敗時重新讀取遠端狀態，不使用過期計畫續跑。
7. 完成後以 unique repository ID 聯集驗證零遺漏。
8. GitHub OAuth、裝置碼與登入確認必須由使用者本人操作。
9. 任務結束後移除臨時 OAuth scope 並清除暫存資料。
10. 不 unstar、不刪除既有 Lists，也不把 starred topics 誤報為 repository 漏分。

若 GitHub GraphQL schema、OAuth scope 或 Stars Lists UI 已變更，以最新官方文件與 live introspection 結果為準，並同步更新 README。

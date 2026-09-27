# GitHub Stars Organizer Checklist

## 執行前

- [ ] 確認 GitHub active account。
- [ ] 記錄原始 OAuth scopes。
- [ ] 記錄 Stars UI 總數。
- [ ] 分頁取得全部 starred repositories。
- [ ] 取得全部 Lists。
- [ ] 逐 List 分頁取得完整 memberships。
- [ ] 確認 repository 數與 topic 差額。

## 規劃

- [ ] 與使用者確認分類架構。
- [ ] 以名稱、description、language、topics 初分。
- [ ] 列出未命中與模糊項目。
- [ ] 人工閱讀必要的 README。
- [ ] 建立 manual overrides。
- [ ] 輸出 dry-run 與各分類預估數。
- [ ] 確認沒有預期外的刪除或覆寫。

## 寫入

- [ ] 必要時由使用者授權臨時 `user` scope。
- [ ] 建立缺少的 Lists。
- [ ] 重新取得 List node IDs。
- [ ] 對每個 repository 計算 existing ∪ desired。
- [ ] 僅更新真正缺少目標 membership 的項目。
- [ ] 每批約 10 筆 mutation。
- [ ] 每批檢查 exit code 與 GraphQL errors。

## 驗證

- [ ] 重新分頁抓取 starred repositories。
- [ ] 重新逐 List 分頁抓取 memberships。
- [ ] Unique List repository IDs 等於 starred repository IDs。
- [ ] Missing repositories 為 0，或有明確人工保留清單。
- [ ] 原始 memberships 全部仍存在。
- [ ] topics 差額未被誤報為遺漏。

## 收尾

- [ ] 移除臨時 `user` scope。
- [ ] 再次執行 `gh auth status`。
- [ ] 刪除暫存腳本與 API 輸出。
- [ ] 關閉 OAuth 臨時視窗。
- [ ] 回報 Lists 數、唯一 repository 數、memberships、遺漏與限制。

# GitHub Stars Organizer Playbook

[繁體中文](README.md) | [English](README.en.md)

一套可交給 AI agent 執行的 GitHub Stars Lists 整理 runbook。它不是一鍵分類器，也不是 GitHub App；重點是把大量 starred repositories 安全整理到 Lists，同時保留既有多重分類、留下 dry-run 與驗證證據，並避免 OAuth 與批次 mutation 造成不可逆損失。

> GitHub 的 User Lists 型別與 `updateUserListsForItem` mutation 目前仍列在公開 GraphQL schema。每次執行前仍應以最新官方文件或 live introspection 確認欄位、scope 與 UI 行為。

## 適合什麼情況

適合：

- Stars 數量很多，想用 GitHub Lists 重新整理。
- 已有 Lists，而且必須保留 repository 原本的重複 memberships。
- 想先讓 AI 初分，再人工覆核模糊項目。
- 希望每次更新都能 dry-run、分批寫入並完整重驗。

不適合：

- 想把 starred topics 當成 repository 放進 Lists。
- 想完全無人監督地處理 OAuth、裝置碼或登入確認。
- 想在沒有 inventory / dry-run 的情況下直接大量 mutation。

## 核心安全規則

1. **先讀再寫。** 先完整取得 starred repositories、Lists 與每張 List 的 memberships。
2. **所有 connection 都要分頁。** `first: 100` 不是完整資料保證。
3. **`listIds` 是完整結果，不是 append。** 每次 mutation 都必須送出：

   ```text
   existing_list_ids ∪ desired_list_ids
   ```

4. **先 dry-run。** 正式寫入前輸出總數、待更新數、未分類項目、各分類預估數與多重 memberships。
5. **OAuth 由使用者本人完成。** AI 不代填裝置碼、不自動確認 GitHub 授權頁。
6. **失敗就重新讀遠端狀態。** 不從過期的 mutation plan 硬續跑。
7. **API 沒報錯不等於完成。** 寫入後重新分頁抓取全部資料，以集合比較驗證。

完整執行時可搭配 [`CHECKLIST.md`](CHECKLIST.md)。

## 先決條件

- 已安裝 [GitHub CLI](https://cli.github.com/)。
- `gh auth status -h github.com` 顯示正確 active account。
- 使用者有權修改自己的 Stars Lists。
- PowerShell 7 或 Windows PowerShell。

先確認帳號與 scopes：

```powershell
gh auth status -h github.com
```

若 Lists mutation 回報 scope 不足，可暫時要求 `user` scope：

```powershell
gh auth refresh -h github.com --scopes user --clipboard
```

裝置授權流程必須由使用者本人完成。任務結束後再移除臨時 scope。

## 執行流程

### 1. 建立 read-only inventory

先記錄：

- GitHub active account。
- Stars UI 顯示總數。
- `viewer.starredRepositories.totalCount`。
- 既有 Lists 名稱與數量。
- 原始 OAuth scopes。
- 執行日期。

不要保存 token、API key 或裝置驗證碼。

取得 starred repositories 時至少讀取：

```graphql
query($endCursor: String) {
  viewer {
    starredRepositories(first: 100, after: $endCursor) {
      totalCount
      nodes {
        id
        nameWithOwner
        description
        primaryLanguage { name }
        repositoryTopics(first: 30) {
          nodes { topic { name } }
        }
      }
      pageInfo { hasNextPage endCursor }
    }
  }
}
```

分類至少使用 `nameWithOwner`、description、primary language 與 repository topics；名稱只能當提示，不能作為唯一判斷依據。

### 2. 取得 Lists 與完整 memberships

先取得 List metadata：

```graphql
query {
  viewer {
    lists(first: 100) {
      nodes { id name slug isPrivate }
    }
  }
}
```

接著**逐 List** 分頁讀取 items：

```graphql
query($listId: ID!, $endCursor: String) {
  node(id: $listId) {
    ... on UserList {
      id
      name
      items(first: 100, after: $endCursor) {
        totalCount
        nodes {
          ... on Repository { id nameWithOwner }
        }
        pageInfo { hasNextPage endCursor }
      }
    }
  }
}
```

建立兩個 lookup：

```text
list_name -> list_id
repository_id -> existing_list_ids[]
```

只讀 `items(first: 100)` 第一頁會讓超過 100 筆的 List 被截斷，後續 union 可能誤刪舊 membership。

### 3. 分類並人工覆核

分類架構先經使用者確認。建議以「主要用途」而不是單純技術關鍵字分類，例如：

- AI Agents & Coding
- ML Models & Research
- Voice, Video & Media
- Stickers & Creative Tools
- LINE & Chatbots
- Windows & Local-first
- Automation & Productivity
- Security & Privacy
- Data, Docs & Knowledge
- Web & App Development
- DevOps & Self-hosting
- Utilities & System Tools

同一 repository 可有多重 membership；不要因為 description 提到 AI 就一律丟進 AI 類。

對未命中或模糊項目，輸出：

```text
owner/name | description | language | topics
```

人工覆核順序：description / topics → README 首段 → 主要用途。仍無法判斷時保留未分類，不要硬塞。

### 4. 產生 dry-run

至少輸出：

```text
starred repositories
existing lists
already classified repositories
updates required
unclassified repositories
estimated count per category
repositories with multiple memberships
```

遇到以下情況就停止：

- active account 不符。
- repository 數量突然下降。
- 既有 memberships 無法完整分頁。
- required List 不存在。
- 未分類數量異常。
- 出現預期外的刪除或 membership 減少。

### 5. 計算安全 union，再分批 mutation

PowerShell 核心邏輯：

```powershell
$existing = @($currentMemberships[$repository.id])
$desiredListId = $listByName[$category].id
$listIds = @($existing + $desiredListId | Sort-Object -Unique)
```

只有目標 membership 尚不存在時才需要 mutation。

GraphQL mutation：

```graphql
mutation {
  updateUserListsForItem(
    input: {
      itemId: "REPOSITORY_NODE_ID"
      listIds: ["EXISTING_LIST_ID", "DESIRED_LIST_ID"]
    }
  ) {
    lists { id name }
  }
}
```

大量更新可用 aliases 分批處理；每批都要檢查 CLI exit code 與 GraphQL `errors`。若任一批失敗，重新讀取 Lists / memberships，再產生新的 idempotent plan。

### 6. 重新抓取全部資料驗證

完成 mutation 後，不沿用寫入前快取。重新執行 starred repositories 與所有 List memberships 的完整分頁查詢。

核心驗證：

```text
missing desired memberships == 0
all original memberships still exist
unexpected removals == 0
```

若你的策略要求每個 starred repository 至少進入一張 List，再另外驗證：

```text
unique(repository IDs across Lists) == starredRepositories.totalCount
```

注意：List counts 相加可能大於 repository 數，因為同一 repository 可以存在多張 Lists。

Stars UI 顯示總數也可能和 `starredRepositories.totalCount` 不同；不要在沒有證據時把差額直接報成 repository 遺漏。

### 7. 清理權限與暫存資料

若執行過程暫時加入 `user` scope：

```powershell
gh auth refresh -h github.com --remove-scopes user --clipboard
```

由使用者完成 GitHub 裝置授權後，再確認：

```powershell
gh auth status -h github.com
```

最後：

- 刪除暫存分類腳本與 API 輸出。
- 不刪除既有 Lists。
- 不 unstar repositories 或 topics。
- 回報 Lists 數量、更新數、未分類數、多重 memberships、驗證結果與 scope 清理狀態。

## 常見失敗

### 原本的重複分類消失

通常是把 `listIds` 誤當成 append，或 memberships 沒有完整分頁。重新抓遠端狀態，再以 `existing ∪ desired` 計算。

### 超過 100 筆後驗證失敗

通常是 verifier 只讀第一頁。驗證器必須和寫入前 inventory 使用相同的逐 List pagination 邏輯。

### PowerShell 空集合變成 `$null`

空 generic collection 經 pipeline / Hashtable 指派可能被展開。優先使用陣列 union，或明確型別的 `Dictionary[string, HashSet[string]]`。

## 文件責任

| 文件 | 用途 |
|---|---|
| [`README.md`](README.md) / [`README.en.md`](README.en.md) | 可重用流程、安全邊界與核心 API 契約 |
| [`CHECKLIST.md`](CHECKLIST.md) | 實際執行時的逐項核對表 |
| [`AGENTS.md`](AGENTS.md) | AI agent 必須遵守的不變規則 |
| [`CLAUDE.md`](CLAUDE.md) | Claude Code 薄入口 |

## 官方參考

- [GitHub GraphQL Users reference](https://docs.github.com/en/graphql/reference/users)
- [GitHub GraphQL public schema](https://docs.github.com/en/graphql/overview/public-schema)
- [Saving repositories with stars](https://docs.github.com/en/get-started/exploring-projects-on-github/saving-repositories-with-stars)
- [GitHub CLI `gh auth refresh`](https://cli.github.com/manual/gh_auth_refresh)

## License

MIT

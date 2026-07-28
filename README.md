# GitHub Stars Organizer Playbook

一套可交給 AI agent 重複執行的 GitHub Stars Lists 整理流程。目標不是只把 repository 塞進分類，而是做到：

- 不覆蓋使用者原本的多重清單關係。
- 先 dry-run，再分批寫入。
- 對超過 100 筆的清單正確分頁。
- 將可自動判斷與必須人工覆核的項目分開。
- 完成後驗證零遺漏，並移除臨時 OAuth 權限。
- 留下可供下一個 AI 重新驗證的證據。

> GitHub Lists 目前仍是 public preview；執行前應重新確認 GraphQL schema 與官方文件是否改變。

## 適用範圍

本流程適用於：

- 將大量 starred repositories 整理到 GitHub 公開 Lists。
- 已經有部分 Lists，且必須保留既有重複分類。
- Stars 頁面總數包含 starred topics，導致 UI 數量與 repository API 數量不同。
- 希望由 AI 做初步分類，再人工覆核模糊項目。

GitHub Lists 只能收納 repositories。若 Stars 頁面顯示的總數高於 `viewer.starredRepositories.totalCount`，差額通常是 starred topics，不是遺漏。

## 安全規則

AI agent 執行前必須遵守以下邊界：

1. 先取得目前 Lists 與所有 memberships，不可直接以單一目標 List 覆寫。
2. `updateUserListsForItem` 的 `listIds` 表示更新後的完整清單集合，不是單純追加。
3. 寫入值必須是：

   ```text
   existing_list_ids ∪ desired_list_ids
   ```

4. 在 mutation 前輸出 dry-run：repository 數量、待更新數、未分類清單與各分類預估數。
5. 不得自動處理 GitHub 登入、裝置驗證碼或 OAuth 確認頁；這一步交由使用者本人。
6. mutation 失敗或回傳 GraphQL `errors` 時停止，重新讀取遠端狀態後再續跑。
7. 寫入後必須重新抓取全部資料驗證，不可用「API 沒報錯」當作完成證據。
8. 任務完成後移除臨時增加的 OAuth scope，並刪除含有分類結果的暫存檔。

## 先決條件

- 已安裝 [GitHub CLI](https://cli.github.com/)。
- `gh auth status -h github.com` 顯示正確的 active account。
- 有權修改該帳號的 Stars Lists。
- PowerShell 7 或 Windows PowerShell。

先確認登入帳號與 scope：

```powershell
gh auth status -h github.com
```

Lists mutation 若回報 scope 不足，可暫時加入 `user` scope：

```powershell
gh auth refresh -h github.com --scopes user --clipboard
```

這會啟動 GitHub 裝置授權流程，必須由使用者本人完成。

## 完整流程

### 1. 建立執行紀錄

執行前記錄：

- GitHub 帳號。
- Stars UI 顯示總數。
- `starredRepositories` repository 數。
- 已存在的 Lists 名稱與數量。
- 原始 token scopes。
- 執行日期。

不要在紀錄中保存 token、API key 或裝置驗證碼。

### 2. 取得所有 starred repositories

使用支援 global node ID 的 GraphQL 查詢：

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
      pageInfo {
        hasNextPage
        endCursor
      }
    }
  }
}
```

GitHub CLI 範例：

```powershell
$query = @'
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
'@

gh api graphql `
  --paginate `
  --slurp `
  -H "X-Github-Next-Global-ID: 1" `
  -f "query=$query"
```

分類時至少使用：

- `nameWithOwner`
- description
- primary language
- repository topics

名稱只能當提示，不能作為唯一判斷依據。

### 3. 取得 Lists 與完整 memberships

先抓 List metadata：

```graphql
query {
  viewer {
    lists(first: 100) {
      nodes {
        id
        name
        slug
        isPrivate
      }
    }
  }
}
```

再逐一依 List ID 分頁抓取 items：

```graphql
query($listId: ID!, $endCursor: String) {
  node(id: $listId) {
    ... on UserList {
      id
      name
      items(first: 100, after: $endCursor) {
        totalCount
        nodes {
          ... on Repository {
            id
            nameWithOwner
          }
        }
        pageInfo {
          hasNextPage
          endCursor
        }
      }
    }
  }
}
```

不要只查：

```graphql
lists {
  nodes {
    items(first: 100)
  }
}
```

當任一 List 超過 100 筆時，這種寫法會悄悄截斷 membership，使後續 union 遺失舊分類。

建議建立兩個 lookup：

```text
list_name -> list_id
repository_id -> existing_list_ids[]
```

### 4. 設計分類架構

分類架構應先經使用者確認。以下是實際處理 513 個 repositories 時使用的通用類別：

| List | 典型線索 |
|---|---|
| AI Agents & Coding | agent、LLM、ChatGPT、Claude、Codex、RAG、prompt、MCP |
| ML Models & Research | PyTorch、TensorFlow、模型、論文、computer vision、diffusion |
| Voice, Video & Media | Whisper、TTS、audio、video、subtitle、YouTube、FFmpeg |
| Stickers & Creative Tools | sticker、image generation、drawing、photo、design、3D |
| LINE & Chatbots | LINE Bot、Messaging API、Telegram bot、Discord bot、chatbot |
| Taiwan & Traditional Chinese | Taiwan、台灣、繁體中文、正體、注音、台語 |
| Windows & Local-first | Windows、WinUI、Win32、PowerShell、desktop utility |
| Automation & Productivity | automation、workflow、RSS、calendar、clipboard、scraper |
| Security & Privacy | security、privacy、pentest、password、VPN、vulnerability |
| Fonts & Typography | font、typeface、typography、字型 |
| Translation & Language | translation、localization、dictionary、簡繁轉換 |
| Data, Docs & Knowledge | database、SQL、PDF、OCR、knowledge、Notion、spreadsheet |
| Utilities & System Tools | utility、converter、manager、viewer、CLI、package |
| Web & App Development | frontend、backend、React、Vue、Django、FastAPI、extension |
| Learning & Awesome Lists | awesome、tutorial、course、guide、roadmap、book |
| Mobile & Cross-platform | Android、iOS、Flutter、React Native、Kotlin、Swift |
| DevOps & Self-hosting | Docker、Kubernetes、server、hosting、CI/CD、monitoring |
| Games & Fun | game、anime、manga、comic、entertainment |
| Hardware & IoT | ESP32、Arduino、Raspberry Pi、firmware、sensor |

#### 分類優先序

關鍵字可能同時命中多個類別，因此需要固定優先序。可依下列方向安排：

1. 高辨識度領域：sticker、LINE bot、font、Taiwan、hardware。
2. 媒體能力：voice、video、Whisper、TTS。
3. 安全、翻譯、Windows、行動平台。
4. ML research 與 AI agents。
5. Web、DevOps、Docs、Learning。
6. Utilities 作為最後 fallback。

不要把所有提到 AI 的 repository 都放到 AI List。例如：

- AI 影片分析工具可優先放 `Voice, Video & Media`。
- AI 圖像生成可優先放 `Stickers & Creative Tools`。
- 模型論文實作可優先放 `ML Models & Research`。

### 5. 建立 manual overrides

自動分類後，將未命中或語意模糊的 repository 列出：

```text
owner/name | description | language | topics
```

人工覆核順序：

1. 讀 repository description 與 topics。
2. 若仍不清楚，讀 README 首段。
3. 判斷 repository 的主要用途，而非只看使用技術。
4. 寫入明確的 override map。

PowerShell 範例：

```powershell
$manualOverrides = @{
    "owner/repository" = "AI Agents & Coding"
    "owner/another-repository" = "Utilities & System Tools"
}
```

如果確實無法判斷，保留在未分類報告，不要硬塞。

### 6. 視需要建立 Lists

建立公開 List：

```graphql
mutation {
  createUserList(
    input: {
      name: "AI Agents & Coding"
      description: "AI agents, coding assistants, LLM tooling and MCP."
      isPrivate: false
    }
  ) {
    list {
      id
      name
      slug
      isPrivate
    }
  }
}
```

建立後重新查詢 Lists，使用 GitHub 回傳的 node ID，不可自行推導 ID。

### 7. 產生 dry-run

正式寫入前至少檢查：

```text
starred repositories
existing lists
already classified repositories
updates required
unclassified repositories
estimated count per category
repositories with multiple memberships
```

以下任一條件成立時停止：

- 有預期外的 List 名稱。
- repository 數突然下降。
- required List 不存在。
- 未分類數量異常。
- 目前 memberships 無法完整分頁。
- GitHub account 與使用者指定帳號不符。

### 8. 計算安全的 membership union

對每一個 repository：

```powershell
$existing = @($currentMemberships[$repository.id])
$desiredListId = $listByName[$category].id
$listIds = @($existing + $desiredListId | Sort-Object -Unique)
```

只有 `$existing -notcontains $desiredListId` 時才需 mutation。

注意 PowerShell 的空集合展開：把空的 generic collection 直接存入 Hashtable 時可能得到 `$null`。最簡單的做法是使用陣列，或使用明確型別的 `Dictionary[string, HashSet[string]]`。

### 9. 分批執行 mutation

單筆 mutation：

```graphql
mutation {
  updateUserListsForItem(
    input: {
      itemId: "REPOSITORY_NODE_ID"
      listIds: ["EXISTING_LIST_ID", "DESIRED_LIST_ID"]
    }
  ) {
    lists {
      id
      name
    }
  }
}
```

大量更新可用 aliases，每批約 10 筆：

```graphql
mutation {
  m0: updateUserListsForItem(
    input: { itemId: "R_1", listIds: ["UL_1"] }
  ) {
    lists { id name }
  }
  m1: updateUserListsForItem(
    input: { itemId: "R_2", listIds: ["UL_2", "UL_3"] }
  ) {
    lists { id name }
  }
}
```

每批都必須：

- 檢查 CLI exit code。
- 解析 GraphQL `errors`。
- 記錄完成進度。
- 不在 log 中輸出 token。

若中途失敗，不要從舊計畫硬續跑。重新取得 Lists 與 memberships，再產生新的 idempotent 更新計畫。

### 10. 完整分頁重驗

更新完成後重新執行步驟 2 與步驟 3，不可沿用寫入前快取。

驗證條件：

```text
unique(repository IDs in every List) == starredRepositories.totalCount
missing repository IDs == 0
every desired membership exists
all original memberships still exist
```

List counts 相加可能大於 repository 數，因為同一 repository 可屬於多張 Lists；應比較唯一 repository ID 的聯集。

### 11. 判斷 UI 總數差異

如果：

```text
Stars UI total = 515
starredRepositories total = 513
```

差額 2 通常是 starred topics。topics 不屬於 `UserListItems` 的 repository 分類範圍，應在報告中明確列為「平台限制」，不可報成漏分。

### 12. 未分類篩選限制

GitHub Stars 頁面目前沒有「未加入任何 List」的反向篩選。Stars 搜尋框只依 repository 或 topic 名稱搜尋；UI 另提供語言、類型與排序。

可採用的替代方式：

- 每次執行本流程，以集合差集產生未分類清單。
- 建立 `Inbox / 待分類` List，新增 star 時先放入，分類後再移除。
- 定期排程 read-only audit；偵測新 star 後開 issue 或輸出報告，不直接自動分類。

### 13. 移除臨時 scope

完成遠端驗證後移除臨時 `user` scope：

```powershell
gh auth refresh -h github.com --remove-scopes user --clipboard
```

由使用者完成 GitHub 裝置授權後，再確認：

```powershell
gh auth status -h github.com
```

輸出不應再包含 `user`。

### 14. 清理與交付

最後：

- 刪除暫存分類腳本與 API 輸出。
- 關閉為 OAuth 開啟的臨時終端機。
- 不刪除使用者原本的 Lists。
- 不 unstar repositories 或 topics。
- 回報分類結果、各 List 數量、未分類數、topics 差額及 scope 清理結果。

## 實際案例：SanHsien

2026-07-28 實際執行結果：

| 項目 | 結果 |
|---|---:|
| Stars UI | 515 |
| Starred repositories | 513 |
| Starred topics 差額 | 2 |
| Lists | 19 |
| Unique repositories in Lists | 513 |
| Missing repositories | 0 |
| Memberships | 526 |
| 額外 memberships | 13 |

List 結果：

| List | Count |
|---|---:|
| AI Agents & Coding | 117 |
| ML Models & Research | 66 |
| Voice, Video & Media | 63 |
| Stickers & Creative Tools | 49 |
| LINE & Chatbots | 43 |
| Taiwan & Traditional Chinese | 27 |
| Windows & Local-first | 25 |
| Automation & Productivity | 24 |
| Security & Privacy | 21 |
| Fonts & Typography | 16 |
| Translation & Language | 14 |
| Data, Docs & Knowledge | 12 |
| Utilities & System Tools | 11 |
| Web & App Development | 11 |
| Learning & Awesome Lists | 8 |
| Mobile & Cross-platform | 6 |
| DevOps & Self-hosting | 5 |
| Games & Fun | 5 |
| Hardware & IoT | 3 |

## 常見失敗與修正

### mutation 前沒有完整取得 memberships

**症狀：** 原本的重複分類消失。

**原因：** `listIds` 被誤當成追加操作，或 `items(first: 100)` 截斷。

**修正：** 逐 List 分頁，送出完整 union。

### 寫入成功，但驗證器報超過 100 筆

**症狀：** mutation 全部完成，驗證階段因 List 大於 100 筆停止。

**原因：** 驗證器只查第一頁。

**修正：** 驗證器與寫入前讀取器必須共用相同的逐 List 分頁函式。

### PowerShell 對空 HashSet 呼叫方法失敗

**症狀：**

```text
You cannot call a method on a null-valued expression.
```

**原因：** 空 collection 經 PowerShell pipeline/Hashtable 指派時被展開。

**修正：** 使用陣列 union，或以明確型別 Dictionary 保存 HashSet。

### UI 顯示數量與 GraphQL 不一致

**症狀：** Stars UI 多出少量項目。

**原因：** UI 同時計算 starred repositories 與 starred topics。

**修正：** 分別記錄，topics 不列為 repository 分類遺漏。

## AI agent 最終回報範本

```markdown
GitHub Stars 分類已完成：

- Stars UI：{ui_total}
- Repositories：{repository_total}
- Topics：{topic_delta}
- Lists：{list_count}
- 已分類 repositories：{classified_unique}
- 未分類 repositories：{missing_count}
- Memberships：{membership_total}
- 臨時 OAuth scope：已移除／尚待使用者確認
- 暫存檔：已清理／尚待清理

注意：
- GitHub 沒有原生「未加入任何 List」篩選。
- List 數量總和可能因多重分類大於 repository 數。
```

## 官方參考

- [Saving repositories with stars](https://docs.github.com/en/get-started/exploring-projects-on-github/saving-repositories-with-stars)
- [GitHub GraphQL Users reference](https://docs.github.com/en/graphql/reference/users)
- [GitHub CLI `gh auth refresh`](https://cli.github.com/manual/gh_auth_refresh)

## License

MIT

# GitHub Stars Organizer Playbook

[繁體中文](README.md) | [English](README.en.md)

A reusable workflow that AI agents can follow to organize GitHub Stars with Lists. The goal is not merely to place repositories into categories, but to:

- Preserve the user's existing multi-list memberships.
- Produce a dry run before writing changes in batches.
- Paginate Lists correctly when they contain more than 100 items.
- Separate automatic classification from cases that require human review.
- Verify that no repository is missing and remove temporary OAuth permissions afterward.
- Leave enough evidence for another AI agent to verify the result independently.

> GitHub Lists are currently in public preview. Recheck the GraphQL schema and official documentation before every run.

## Scope

This workflow is suitable for:

- Organizing a large collection of starred repositories into public GitHub Lists.
- Accounts that already use Lists and whose existing overlapping memberships must be preserved.
- Stars pages whose totals include starred topics, causing the UI count to differ from the repository API count.
- Workflows where AI performs initial classification and a human reviews ambiguous repositories.

GitHub Lists contain repositories. If the total shown on the Stars page is higher than `viewer.starredRepositories.totalCount`, the difference is usually starred topics rather than missing repositories.

## Safety Rules

An AI agent must follow these boundaries before making changes:

1. Read all current Lists and memberships before updating anything. Never overwrite memberships with only one target List.
2. The `listIds` field of `updateUserListsForItem` represents the complete set of Lists after the update; it is not an append-only operation.
3. Every write must use:

   ```text
   existing_list_ids ∪ desired_list_ids
   ```

4. Produce a dry run before mutations, including the repository count, required updates, unclassified repositories, and estimated category counts.
5. Do not automate GitHub login, device-code entry, or OAuth confirmation pages. The user must complete those steps.
6. Stop when a mutation fails or returns GraphQL `errors`. Re-read the remote state before resuming.
7. Re-fetch all data after writing. An API request returning without an error is not sufficient proof of completion.
8. Remove any temporarily added OAuth scope and delete temporary files containing classification results when the task is complete.

## Prerequisites

- [GitHub CLI](https://cli.github.com/) is installed.
- `gh auth status -h github.com` shows the intended active account.
- The account is allowed to update its Stars Lists.
- PowerShell 7 or Windows PowerShell is available.

Check the active account and current scopes:

```powershell
gh auth status -h github.com
```

If the Lists mutation reports an insufficient scope, temporarily add the `user` scope:

```powershell
gh auth refresh -h github.com --scopes user --clipboard
```

This starts GitHub's device authorization flow and must be completed by the user.

## End-to-End Workflow

### 1. Create a Run Record

Record the following before execution:

- GitHub account.
- Total shown in the Stars UI.
- Repository count from `starredRepositories`.
- Names and sizes of existing Lists.
- Original token scopes.
- Execution date.

Never store a token, API key, or device code in the record.

### 2. Fetch All Starred Repositories

Use a paginated GraphQL query with global node IDs:

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

GitHub CLI example:

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

Use at least these fields for classification:

- `nameWithOwner`
- description
- primary language
- repository topics

A repository name is only a hint and must not be the sole classification signal.

### 3. Fetch Lists and Complete Memberships

First fetch List metadata:

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

Then paginate the items of each List by its List ID:

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

Do not rely only on:

```graphql
lists {
  nodes {
    items(first: 100)
  }
}
```

When any List contains more than 100 repositories, that query silently truncates its memberships. A later union could then remove memberships that were not present on the first page.

Build these two lookups:

```text
list_name -> list_id
repository_id -> existing_list_ids[]
```

### 4. Design the Category Structure

The user should confirm the category structure first. These general-purpose categories were used in a real run covering 513 repositories:

| List | Typical signals |
|---|---|
| AI Agents & Coding | agent, LLM, ChatGPT, Claude, Codex, RAG, prompt, MCP |
| ML Models & Research | PyTorch, TensorFlow, models, papers, computer vision, diffusion |
| Voice, Video & Media | Whisper, TTS, audio, video, subtitles, YouTube, FFmpeg |
| Stickers & Creative Tools | sticker, image generation, drawing, photo, design, 3D |
| LINE & Chatbots | LINE Bot, Messaging API, Telegram bot, Discord bot, chatbot |
| Taiwan & Traditional Chinese | Taiwan, Traditional Chinese, Bopomofo, Taiwanese |
| Windows & Local-first | Windows, WinUI, Win32, PowerShell, desktop utility |
| Automation & Productivity | automation, workflow, RSS, calendar, clipboard, scraper |
| Security & Privacy | security, privacy, pentest, password, VPN, vulnerability |
| Fonts & Typography | font, typeface, typography |
| Translation & Language | translation, localization, dictionary, script conversion |
| Data, Docs & Knowledge | database, SQL, PDF, OCR, knowledge, Notion, spreadsheet |
| Utilities & System Tools | utility, converter, manager, viewer, CLI, package |
| Web & App Development | frontend, backend, React, Vue, Django, FastAPI, extension |
| Learning & Awesome Lists | awesome, tutorial, course, guide, roadmap, book |
| Mobile & Cross-platform | Android, iOS, Flutter, React Native, Kotlin, Swift |
| DevOps & Self-hosting | Docker, Kubernetes, server, hosting, CI/CD, monitoring |
| Games & Fun | game, anime, manga, comic, entertainment |
| Hardware & IoT | ESP32, Arduino, Raspberry Pi, firmware, sensor |

#### Classification Priority

Keywords can match several categories, so classification needs a fixed priority order. A useful order is:

1. High-confidence domains: stickers, LINE bots, fonts, Taiwan, and hardware.
2. Media capabilities: voice, video, Whisper, and TTS.
3. Security, translation, Windows, and mobile platforms.
4. ML research and AI agents.
5. Web, DevOps, Docs, and Learning.
6. Utilities as the final fallback.

Do not place every repository that mentions AI into the AI List. For example:

- An AI video-analysis tool may belong in `Voice, Video & Media`.
- An AI image-generation tool may belong in `Stickers & Creative Tools`.
- A research implementation of a model may belong in `ML Models & Research`.

### 5. Create Manual Overrides

After automatic classification, list unmatched and ambiguous repositories:

```text
owner/name | description | language | topics
```

Review them in this order:

1. Read the repository description and topics.
2. If the purpose is still unclear, read the first section of the README.
3. Classify by the repository's primary purpose rather than the technologies it uses.
4. Add an explicit override.

PowerShell example:

```powershell
$manualOverrides = @{
    "owner/repository" = "AI Agents & Coding"
    "owner/another-repository" = "Utilities & System Tools"
}
```

If a repository genuinely cannot be classified, leave it in the unclassified report rather than forcing it into an unsuitable List.

### 6. Create Lists When Needed

Create a public List:

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

After creating Lists, fetch them again and use the node IDs returned by GitHub. Never derive or invent node IDs.

### 7. Produce a Dry Run

At minimum, inspect:

```text
starred repositories
existing lists
already classified repositories
updates required
unclassified repositories
estimated count per category
repositories with multiple memberships
```

Stop if any of these conditions occur:

- An unexpected List name appears.
- The repository count drops unexpectedly.
- A required List does not exist.
- The number of unclassified repositories is abnormal.
- Current memberships cannot be fully paginated.
- The active GitHub account does not match the account specified by the user.

### 8. Calculate a Safe Membership Union

For each repository:

```powershell
$existing = @($currentMemberships[$repository.id])
$desiredListId = $listByName[$category].id
$listIds = @($existing + $desiredListId | Sort-Object -Unique)
```

Only send a mutation when `$existing -notcontains $desiredListId`.

Be aware of PowerShell empty-collection expansion. Assigning an empty generic collection directly into a Hashtable can result in `$null`. The simplest safe approach is to use arrays, or use an explicitly typed `Dictionary[string, HashSet[string]]`.

### 9. Run Mutations in Batches

Single-item mutation:

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

For large updates, use aliases with approximately 10 mutations per request:

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

For every batch:

- Check the CLI exit code.
- Parse GraphQL `errors`.
- Record progress.
- Never print the token in logs.

If a batch fails, do not continue from a stale plan. Re-fetch Lists and memberships, then generate a new idempotent update plan.

### 10. Re-verify with Complete Pagination

After all updates, repeat steps 2 and 3 without reusing pre-write data.

Verification conditions:

```text
unique(repository IDs in every List) == starredRepositories.totalCount
missing repository IDs == 0
every desired membership exists
all original memberships still exist
```

The sum of List counts can be greater than the number of repositories because one repository can belong to several Lists. Compare the union of unique repository IDs instead.

### 11. Explain UI Count Differences

For example:

```text
Stars UI total = 515
starredRepositories total = 513
```

The difference of two is usually starred topics. Topics are outside the repository-classification scope of `UserListItems`; report them as a platform limitation rather than missing repositories.

### 12. Understand the Unclassified-Filter Limitation

The GitHub Stars page does not currently provide an inverse filter for items that do not belong to any List. The Stars search field searches only repository or topic names; the UI also offers language, type, and sorting controls.

Available workarounds:

- Calculate a set difference during every run and produce an unclassified report.
- Create an `Inbox / To classify` List, add new stars there first, and remove them after classification.
- Run a scheduled read-only audit that opens an issue or produces a report when new stars are detected, without classifying them automatically.

### 13. Remove the Temporary Scope

After remote verification, remove the temporary `user` scope:

```powershell
gh auth refresh -h github.com --remove-scopes user --clipboard
```

After the user completes GitHub's device authorization flow, verify:

```powershell
gh auth status -h github.com
```

The output should no longer include `user`.

### 14. Clean Up and Report

Finally:

- Delete temporary classification scripts and API output.
- Close temporary terminals opened for OAuth.
- Do not delete the user's existing Lists.
- Do not unstar repositories or topics.
- Report category counts, the number of unclassified repositories, the topic difference, and the OAuth-scope cleanup result.

## Case Study: SanHsien

Actual result from 2026-07-28:

| Item | Result |
|---|---:|
| Stars UI | 515 |
| Starred repositories | 513 |
| Starred topics difference | 2 |
| Lists | 19 |
| Unique repositories in Lists | 513 |
| Missing repositories | 0 |
| Memberships | 526 |
| Additional memberships | 13 |

List results:

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

## Common Failures and Fixes

### Memberships Were Not Fully Fetched Before Mutation

**Symptom:** Existing overlapping classifications disappear.

**Cause:** `listIds` was treated as append-only, or `items(first: 100)` truncated a List.

**Fix:** Paginate each List separately and submit the complete union.

### Writes Succeed but Verification Fails Above 100 Items

**Symptom:** All mutations finish, but verification stops because a List contains more than 100 items.

**Cause:** The verifier reads only the first page.

**Fix:** The verifier and the pre-write reader must share the same per-List pagination function.

### Calling a Method on an Empty PowerShell HashSet Fails

**Symptom:**

```text
You cannot call a method on a null-valued expression.
```

**Cause:** PowerShell expands an empty collection during pipeline or Hashtable assignment.

**Fix:** Use an array union or store the HashSet in an explicitly typed Dictionary.

### The UI Count and GraphQL Count Differ

**Symptom:** The Stars UI shows a small number of extra items.

**Cause:** The UI counts starred repositories and starred topics together.

**Fix:** Record them separately. Do not report topics as unclassified repositories.

## AI Agent Final Report Template

```markdown
GitHub Stars classification is complete:

- Stars UI: {ui_total}
- Repositories: {repository_total}
- Topics: {topic_delta}
- Lists: {list_count}
- Classified repositories: {classified_unique}
- Unclassified repositories: {missing_count}
- Memberships: {membership_total}
- Temporary OAuth scope: removed / awaiting user confirmation
- Temporary files: cleaned / pending cleanup

Notes:
- GitHub does not provide a native "not in any List" filter.
- The sum of List counts may exceed the repository count because of overlapping memberships.
```

## Official References

- [Saving repositories with stars](https://docs.github.com/en/get-started/exploring-projects-on-github/saving-repositories-with-stars)
- [GitHub GraphQL Users reference](https://docs.github.com/en/graphql/reference/users)
- [GitHub CLI `gh auth refresh`](https://cli.github.com/manual/gh_auth_refresh)

## License

MIT

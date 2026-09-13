# GitHub Stars Organizer Playbook

[繁體中文](README.md) | [English](README.en.md)

A reusable runbook that AI agents can follow to organize GitHub Stars with Lists. It is not a one-click classifier or a GitHub App. Its purpose is to reorganize large collections of starred repositories safely while preserving existing multi-list memberships, producing a dry run before writes, and leaving enough evidence to verify the final state.

> GitHub User Lists types and the `updateUserListsForItem` mutation are currently present in the public GraphQL schema. Before every run, verify the latest official documentation or live introspection for schema, scope, and UI changes.

## When to use it

Good fit:

- You have many starred repositories and want to organize them with GitHub Lists.
- Existing Lists already overlap and those memberships must be preserved.
- AI should perform an initial classification while a human reviews ambiguous cases.
- Every update should be dry-run first, applied in batches, and fully re-verified.

Not a good fit:

- Treating starred topics as repositories that can be placed in Lists.
- Fully unattended OAuth, device-code, or login confirmation.
- Bulk mutations without inventory and a dry run.

## Safety invariants

1. **Read before writing.** Fetch all starred repositories, Lists, and memberships first.
2. **Paginate every connection.** `first: 100` is not proof that the data set is complete.
3. **`listIds` is the complete result, not an append operation.** Every mutation must use:

   ```text
   existing_list_ids ∪ desired_list_ids
   ```

4. **Dry-run first.** Report totals, planned updates, unclassified items, category estimates, and overlapping memberships.
5. **OAuth stays human-controlled.** The agent must not enter device codes or approve GitHub authorization pages.
6. **Re-read remote state after failure.** Never resume from a stale mutation plan.
7. **No-error is not completion evidence.** Re-fetch all data after writes and verify with set comparisons.

Use [`CHECKLIST.md`](CHECKLIST.md) during an actual run.

## Prerequisites

- [GitHub CLI](https://cli.github.com/) is installed.
- `gh auth status -h github.com` shows the intended active account.
- The user can modify their own Stars Lists.
- PowerShell 7 or Windows PowerShell is available.

Check the account and scopes:

```powershell
gh auth status -h github.com
```

If a Lists mutation reports insufficient scope, temporarily request `user`:

```powershell
gh auth refresh -h github.com --scopes user --clipboard
```

The user must complete the device authorization flow. Remove temporary scope again after the task.

## Workflow

### 1. Build a read-only inventory

Record:

- Active GitHub account.
- Stars UI total.
- `viewer.starredRepositories.totalCount`.
- Existing List names and counts.
- Original OAuth scopes.
- Execution date.

Never store tokens, API keys, or device codes.

Fetch starred repositories with enough metadata for classification:

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

Use at least `nameWithOwner`, description, primary language, and repository topics. Names are hints, not sufficient classification evidence.

### 2. Fetch Lists and complete memberships

Fetch List metadata:

```graphql
query {
  viewer {
    lists(first: 100) {
      nodes { id name slug isPrivate }
    }
  }
}
```

Then paginate **each List** by ID:

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

Build two lookups:

```text
list_name -> list_id
repository_id -> existing_list_ids[]
```

Reading only the first `items(first: 100)` page can silently truncate a large List and cause later union logic to drop old memberships.

### 3. Classify, then review ambiguous cases

Have the user confirm the taxonomy first. Prefer categories based on primary purpose, for example:

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

A repository may legitimately belong to several Lists. Do not place everything that mentions AI into an AI category.

For unmatched or ambiguous items, output:

```text
owner/name | description | language | topics
```

Review in this order: description / topics → first README section → primary purpose. If the purpose is still unclear, leave the repository unclassified instead of forcing a guess.

### 4. Produce a dry run

At minimum report:

```text
starred repositories
existing lists
already classified repositories
updates required
unclassified repositories
estimated count per category
repositories with multiple memberships
```

Stop if:

- The active account is wrong.
- Repository totals drop unexpectedly.
- Existing memberships cannot be fully paginated.
- A required List is missing.
- The unclassified count is abnormal.
- The plan contains unexpected removals or membership reductions.

### 5. Compute the safe union and mutate in batches

Core PowerShell logic:

```powershell
$existing = @($currentMemberships[$repository.id])
$desiredListId = $listByName[$category].id
$listIds = @($existing + $desiredListId | Sort-Object -Unique)
```

Only mutate when the desired membership is missing.

GraphQL mutation:

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

Large updates can use aliases in small batches. For every batch, check the CLI exit code and GraphQL `errors`. If any batch fails, re-fetch Lists and memberships and generate a new idempotent plan.

### 6. Re-fetch and verify everything

Do not reuse pre-write data. Repeat full pagination for starred repositories and all List memberships.

Core verification:

```text
missing desired memberships == 0
all original memberships still exist
unexpected removals == 0
```

If your policy requires every starred repository to appear in at least one List, also verify:

```text
unique(repository IDs across Lists) == starredRepositories.totalCount
```

The sum of List counts can exceed the repository total because memberships may overlap.

The Stars UI total may also differ from `starredRepositories.totalCount`; do not label the difference as missing repositories without evidence.

### 7. Remove temporary access and files

If `user` scope was added temporarily:

```powershell
gh auth refresh -h github.com --remove-scopes user --clipboard
```

After the user completes GitHub's device flow, verify:

```powershell
gh auth status -h github.com
```

Finally:

- Delete temporary classification scripts and API output.
- Do not delete existing Lists.
- Do not unstar repositories or topics.
- Report List counts, updates, unclassified items, overlapping memberships, verification results, and OAuth cleanup state.

## Common failures

### Existing overlapping classifications disappear

Usually `listIds` was treated as append-only or memberships were not fully paginated. Re-fetch remote state and recompute `existing ∪ desired`.

### Verification breaks above 100 items

The verifier is probably reading only the first page. It must use the same per-List pagination logic as the pre-write inventory.

### An empty PowerShell collection becomes `$null`

Pipeline / Hashtable assignment can expand an empty generic collection. Prefer array union or an explicitly typed `Dictionary[string, HashSet[string]]`.

## Documentation responsibilities

| File | Purpose |
|---|---|
| [`README.md`](README.md) / [`README.en.md`](README.en.md) | Reusable workflow, safety boundaries, and core API contracts |
| [`CHECKLIST.md`](CHECKLIST.md) | Step-by-step execution checklist |
| [`AGENTS.md`](AGENTS.md) | Invariants that AI agents must preserve |
| [`CLAUDE.md`](CLAUDE.md) | Thin Claude Code entry point |

## Official references

- [GitHub GraphQL Users reference](https://docs.github.com/en/graphql/reference/users)
- [GitHub GraphQL public schema](https://docs.github.com/en/graphql/overview/public-schema)
- [Saving repositories with stars](https://docs.github.com/en/get-started/exploring-projects-on-github/saving-repositories-with-stars)
- [GitHub CLI `gh auth refresh`](https://cli.github.com/manual/gh_auth_refresh)

## License

MIT

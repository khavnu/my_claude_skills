---
name: switch-figma-account
description: Use when switching between multiple Figma accounts for MCP access, or when the current Figma account has hit rate limits and another account should be used instead.
---

# Switch Figma Account

## Overview

Swaps Figma OAuth credentials in `~/.claude/.credentials.json` to use a different Figma account with the MCP plugin. **Requires Claude Code restart** to take effect.

## Account Storage

```
~/.claude/figma-accounts/
  Company.json    # Company Figma account
  Personal.json   # Personal Figma account (example)
```

Each file format:
```json
{ "credentials": { "serverName": "...", "accessToken": "...", "refreshToken": "...", ... } }
```

## Commands

### 1. List Available Accounts + Active

```bash
ACTIVE_TOKEN=$(jq -r '.mcpOAuth | to_entries[] | select(.key | startswith("plugin:figma:figma")) | .value.accessToken' \
  ~/.claude/.credentials.json | cut -c1-20)
echo "Available Figma accounts:"
for f in ~/.claude/figma-accounts/*.json; do
  NAME=$(basename "$f" .json)
  TOKEN=$(jq -r '.credentials.accessToken' "$f" | cut -c1-20)
  [[ "$TOKEN" == "$ACTIVE_TOKEN" ]] && echo "  * $NAME (ACTIVE)" || echo "    $NAME"
done
```

### 2. Switch to an Account

```bash
TARGET="Company"   # <-- replace with target account name
CREDS_FILE=~/.claude/figma-accounts/${TARGET}.json
if [[ ! -f "$CREDS_FILE" ]]; then echo "Account not found: $TARGET"; exit 1; fi
FIGMA_KEY=$(jq -r '.mcpOAuth | keys[] | select(startswith("plugin:figma:figma"))' ~/.claude/.credentials.json)
NEW_CREDS=$(jq '.credentials' "$CREDS_FILE")
TMP=$(mktemp)
jq --arg key "$FIGMA_KEY" --argjson creds "$NEW_CREDS" \
  '.mcpOAuth[$key] = $creds' ~/.claude/.credentials.json > "$TMP" && \
  mv "$TMP" ~/.claude/.credentials.json
echo "Switched to: $TARGET"
echo "=> Restart Claude Code to apply"
```

### 3. Save Current Active Account

Run this **after** authorizing a new account via OAuth (Figma MCP will prompt when you call any Figma tool).

```bash
NAME="Personal"   # <-- replace with account name to save
FIGMA_KEY=$(jq -r '.mcpOAuth | keys[] | select(startswith("plugin:figma:figma"))' ~/.claude/.credentials.json)
jq --arg key "$FIGMA_KEY" '{credentials: .mcpOAuth[$key]}' ~/.claude/.credentials.json \
  > ~/.claude/figma-accounts/${NAME}.json
echo "Saved: $NAME"
```

## Workflow

### Add a New Account (First Time)

1. Switch to the new account in the Figma MCP:
   - In Claude Code terminal run: `/mcp` → find Figma → Disconnect (hoặc xóa OAuth entry)
   - Hoặc: xóa tạm entry trong `.credentials.json`
2. Call any Figma tool (e.g. `/switch-figma-account` sẽ trigger list) → Claude Code sẽ prompt OAuth
3. Authorize với account mới
4. Chạy **Save Current** với tên account mới

### Switch Accounts (Routine)

1. Chạy `/switch-figma-account`
2. Agent list accounts, chạy switch script cho account muốn dùng
3. Restart Claude Code

## Important Notes

- **Restart required** — MCP server load credentials at startup, không hot-reload
- Nếu refresh token expired → cần re-authorize qua OAuth và save lại
- `~/.claude/figma-accounts/` chứa OAuth credentials — không commit lên git

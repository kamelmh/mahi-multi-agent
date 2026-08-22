# Gmail Integration — Setup Guide

> Two ways to read Gmail from MAHI/DSC agents.

---

## Option 1: IMAP (Quick — Works Now)

Uses Gmail App Password. No Google Cloud project needed.

### Setup (5 minutes)

1. **Enable 2FA** on your Google Account (if not already)
   - Go to https://myaccount.google.com/security
   - Enable 2-Step Verification

2. **Generate App Password**
   - Go to https://myaccount.google.com/apppasswords
   - Select app: "Mail"
   - Select device: "Other (Custom name)" → type "MAHI Agent"
   - Click "Generate"
   - Copy the 16-character password

3. **Set environment variable**
   ```bash
   # Windows (permanent)
   setx GITHUB_NOTIFIER_APP_PASSWORD "xxxx-xxxx-xxxx-xxxx"
   
   # Or in .env file
   echo GITHUB_NOTIFIER_APP_PASSWORD=xxxx-xxxx-xxxx-xxxx >> .env
   ```

4. **Test it**
   ```bash
   python github_notifications.py
   ```

### What it does
- Connects to Gmail via IMAP (port 993, SSL)
- Searches for emails from notifications@github.com
- Parses: repo, type (PR/issue), action, title, number, URL
- Returns structured data (terminal or JSON)

### Usage
```bash
# Unread GitHub notifications
python github_notifications.py

# All notifications (including read)
python github_notifications.py --all

# Last 24 hours
python github_notifications.py --hours 24

# Filter by repo
python github_notifications.py --repo mahi-multi-agent

# JSON output (for piping to other tools)
python github_notifications.py --json
```

---

## Option 2: Gmail MCP (Full Access)

Full Gmail API access: read, search, send, draft, labels, attachments.

### Setup (15 minutes)

#### Step 1: Google Cloud Project

1. Go to https://console.cloud.google.com
2. Create new project: "MAHI Gmail Agent"
3. Enable **Gmail API**:
   - APIs & Services → Library
   - Search "Gmail API" → Enable

#### Step 2: OAuth Credentials

1. APIs & Services → Credentials
2. Create Credentials → OAuth 2.0 Client ID
3. Application type: **Desktop app**
4. Name: "MAHI Gmail MCP"
5. Download JSON → save as:
   ```
   C:\Users\Admin\.gmail-mcp\gcp-oauth.keys.json
   ```

#### Step 3: Configure OAuth Consent

1. APIs & Services → OAuth consent screen
2. User type: **External** (or Internal if Google Workspace)
3. Add scopes: `gmail.readonly`, `gmail.send`, `gmail.modify`
4. Add test user: your Gmail address

#### Step 4: Authenticate

```bash
mkdir -p ~/.gmail-mcp
npx @gongrzhe/server-gmail-autoauth-mcp auth
```

This opens a browser → sign in → grant access → credentials.json is saved.

#### Step 5: Enable MCP

In `opencode.jsonc`, set `"enabled": true` for the gmail MCP server.

### Tools Available

| Tool | Description |
|------|-------------|
| `search_emails` | Search with Gmail query syntax |
| `read_email` | Read full email content |
| `send_email` | Send email (with attachments) |
| `create_draft` | Draft email (safer than send) |
| `list_labels` | List all labels |
| `modify_email` | Add/remove labels |
| `list_attachments` | List email attachments |
| `get_thread` | Read full thread |

### Gmail Search Examples

```
from:notifications@github.com           # GitHub notifications
is:unread newer_than:2d                 # Unread last 2 days
subject:invoice has:attachment          # Invoices with attachments
label:github is:unread                  # Unread in GitHub label
from:noreply@github.com is:unread       # Unread GitHub emails
```

---

## Recommendation

- **Start with Option 1 (IMAP)** — it works immediately, no cloud setup
- **Upgrade to Option 2 (MCP)** when you need:
  - Sending emails (agent-initiated)
  - Label management
  - Thread reading
  - Attachment handling
  - Integration with inbox-triage skill

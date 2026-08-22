#!/usr/bin/env python3
"""
GitHub Notification Checker — IMAP-based Gmail reader.
Reads GitHub notification emails from Gmail and returns structured data.

Usage:
    python github_notifications.py                    # Check unread GitHub notifications
    python github_notifications.py --all              # Check all (not just unread)
    python github_notifications.py --hours 24         # Last 24 hours only
    python github_notifications.py --json             # JSON output
    python github_notifications.py --repo owner/repo  # Filter by repo

Requires: Gmail App Password (not your regular password)
    1. Enable 2FA on Google Account
    2. Go to https://myaccount.google.com/apppasswords
    3. Generate app password for "Mail"
    4. Set env var: GITHUB_NOTIFIER_APP_PASSWORD=<password>

Author: MAHI Kamel — DSC Digital Services Center
"""

import imaplib
import email
from email.header import decode_header
import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, field, asdict
from typing import Optional

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
IMAP_SERVER = "imap.gmail.com"
IMAP_PORT = 993
GITHUB_EMAIL = os.environ.get("GITHUB_NOTIFIER_EMAIL", "kamelmahi71@gmail.com")
APP_PASSWORD = os.environ.get("GITHUB_NOTIFIER_APP_PASSWORD", "")

# GitHub notification email patterns
GITHUB_SENDERS = [
    "notifications@github.com",
    "github@noreply.github.com",
    "noreply@github.com",
]


@dataclass
class GitHubNotification:
    """A single parsed GitHub notification."""
    id: str = ""
    timestamp: str = ""
    repo: str = ""
    repo_url: str = ""
    type: str = ""           # pull_request, issue, discussion, release, security, etc.
    action: str = ""         # opened, closed, merged, commented, reviewed, etc.
    title: str = ""
    number: int = 0
    url: str = ""
    sender: str = ""
    sender_url: str = ""
    body_snippet: str = ""
    is_read: bool = False
    labels: list = field(default_factory=list)


def decode_mime_header(header_value: str) -> str:
    """Decode MIME-encoded header to string."""
    if not header_value:
        return ""
    decoded_parts = decode_header(header_value)
    result = []
    for part, charset in decoded_parts:
        if isinstance(part, bytes):
            result.append(part.decode(charset or "utf-8", errors="replace"))
        else:
            result.append(part)
    return " ".join(result)


def parse_github_notification(subject: str, sender: str, body: str, date_str: str) -> Optional[GitHubNotification]:
    """Parse a GitHub notification email into structured data."""
    n = GitHubNotification()
    n.sender = sender
    n.timestamp = date_str

    # --- Parse subject: "[repo/name] Action #123: Title" or "[repo/name] (type) Title" ---
    # Pattern 1: [owner/repo] Action #number: Title
    m = re.match(r'\[([^\]]+)\]\s*(?:\((\w+)\)\s*)?(.+?)(?:\s*#\d+:?\s*(.*))?$', subject)
    if m:
        n.repo = m.group(1)
        if m.group(2):
            n.type = m.group(2).lower()
        remaining = (m.group(3) or "").strip()
        title_part = (m.group(4) or "").strip()

        # Extract number
        num_match = re.search(r'#(\d+)', subject)
        if num_match:
            n.number = int(num_match.group(1))

        if title_part:
            n.title = title_part
        elif remaining:
            n.title = remaining
    else:
        # Pattern 2: [owner/repo] title (for workflow notifications)
        m2 = re.match(r'\[([^\]]+)\]\s*(.+)', subject)
        if m2:
            n.repo = m2.group(1)
            n.title = m2.group(2).strip()
        else:
            # Fallback: just use the whole subject
            n.title = subject

    # --- Detect type from subject keywords ---
    subject_lower = subject.lower()
    if not n.type:
        if "pull request" in subject_lower or "[pr]" in subject_lower:
            n.type = "pull_request"
        elif "issue" in subject_lower or "[issue]" in subject_lower:
            n.type = "issue"
        elif "discussion" in subject_lower:
            n.type = "discussion"
        elif "release" in subject_lower:
            n.type = "release"
        elif "security" in subject_lower or "vulnerability" in subject_lower:
            n.type = "security"
        elif "workflow" in subject_lower or "run failed" in subject_lower or "action" in subject_lower:
            n.type = "workflow"
        elif "token" in subject_lower or "oauth" in subject_lower or "third-party" in subject_lower:
            n.type = "account"
        else:
            n.type = "notification"

    # --- Extract number (try harder) ---
    if not n.number:
        num_match = re.search(r'#(\d+)', subject)
        if num_match:
            n.number = int(num_match.group(1))

    # --- Detect action ---
    action_patterns = {
        "opened": r"\bopened\b",
        "closed": r"\bclosed\b",
        "merged": r"\bmerged\b",
        "commented": r"\bcommented\b",
        "reviewed": r"\breviewed\b",
        "approved": r"\bapproved\b",
        "requested": r"\brequested\b",
        "pushed": r"\bpushed\b",
        "created": r"\bcreated\b",
        "deleted": r"\bdeleted\b",
        "published": r"\bpublished\b",
        "assigned": r"\bassigned\b",
        "mentioned": r"\bmentioned\b",
        "subscribed": r"\bsubscribed\b",
        "referenced": r"\breferenced\b",
        "completed": r"\bcompleted\b",
        "reopened": r"\breopened\b",
        "synchronized": r"\bsynchronized\b",
    }
    for action, pattern in action_patterns.items():
        if re.search(pattern, subject_lower):
            n.action = action
            break

    # --- Extract repo URL ---
    if n.repo:
        n.repo_url = f"https://github.com/{n.repo}"

    # --- Extract notification URL ---
    # GitHub notifications link format: https://github.com/owner/repo/pull/123
    url_match = re.search(r'https://github\.com/[^\s<>"]+', body)
    if url_match:
        n.url = url_match.group(0)
    elif n.repo and n.number:
        type_path = "pull" if n.type == "pull_request" else "issues"
        n.url = f"https://github.com/{n.repo}/{type_path}/{n.number}"

    # --- Extract sender info from body ---
    sender_match = re.search(r'style="font-weight:600"[^>]*>([^<]+)</a>', body)
    if sender_match:
        n.sender = sender_match.group(1).strip()

    # --- Body snippet ---
    # Strip HTML tags for a clean snippet
    clean_body = re.sub(r'<[^>]+>', ' ', body)
    clean_body = re.sub(r'\s+', ' ', clean_body).strip()
    n.body_snippet = clean_body[:300]

    return n


def check_github_notifications(
    unread_only: bool = True,
    hours: Optional[int] = None,
    repo_filter: Optional[str] = None,
) -> list[GitHubNotification]:
    """Connect to Gmail via IMAP and fetch GitHub notifications."""
    if not APP_PASSWORD:
        print("ERROR: Set GITHUB_NOTIFIER_APP_PASSWORD environment variable.")
        print("  1. Enable 2FA on Google Account")
        print("  2. Go to https://myaccount.google.com/apppasswords")
        print("  3. Generate app password for 'Mail'")
        print("  4. export GITHUB_NOTIFIER_APP_PASSWORD=<password>")
        sys.exit(1)

    # Connect
    mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
    mail.login(GITHUB_EMAIL, APP_PASSWORD)

    # Select inbox
    mail.select("INBOX")

    # Build search criteria — Gmail IMAP has quirks with OR, so we do separate searches
    # and merge results
    all_ids = set()

    for sender in GITHUB_SENDERS:
        criteria = []
        if unread_only:
            criteria.append("UNSEEN")
        criteria.append(f'FROM "{sender}"')
        if hours:
            since = datetime.now(timezone.utc) - timedelta(hours=hours)
            criteria.append(f'SINCE "{since.strftime("%d-%b-%Y")}"')

        search_query = " ".join(criteria)
        status, message_ids = mail.search(None, search_query)
        if status == "OK" and message_ids[0]:
            ids = message_ids[0].split()
            all_ids.update(ids)

    if not all_ids:
        mail.logout()
        return []

    # Sort IDs numerically
    ids = sorted(all_ids, key=lambda x: int(x))
    notifications = []

    for msg_id in ids:
        status, msg_data = mail.fetch(msg_id, "(RFC822)")
        if status != "OK":
            continue

        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)

        subject = decode_mime_header(msg.get("Subject", ""))
        sender = decode_mime_header(msg.get("From", ""))
        date_str = msg.get("Date", "")

        # Extract sender email address
        sender_email_match = re.search(r'<([^>]+)>', sender)
        sender_email = sender_email_match.group(1) if sender_email_match else sender

        # Only process GitHub notifications
        if not any(gh in sender_email.lower() for gh in GITHUB_SENDERS):
            continue

        # Get body (prefer plaintext)
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                ctype = part.get_content_type()
                if ctype == "text/plain":
                    body = part.get_payload(decode=True).decode("utf-8", errors="replace")
                    break
                elif ctype == "text/html" and not body:
                    body = part.get_payload(decode=True).decode("utf-8", errors="replace")
        else:
            body = msg.get_payload(decode=True).decode("utf-8", errors="replace")

        # Parse
        n = parse_github_notification(subject, sender_email, body, date_str)
        if n:
            # Mark read status
            n.is_read = "\\Seen" in str(msg_data)

            # Apply repo filter
            if repo_filter and repo_filter.lower() not in n.repo.lower():
                continue

            notifications.append(n)

    mail.logout()
    return notifications


def format_notification(n: GitHubNotification, index: int = 0) -> str:
    """Format a notification for terminal display."""
    type_icons = {
        "pull_request": "PR",
        "issue": "ISSUE",
        "discussion": "DISC",
        "release": "REL",
        "security": "SEC",
        "workflow": "CI",
        "account": "ACCT",
        "notification": "NOTIF",
    }
    type_label = type_icons.get(n.type, "NOTIF")
    action_label = n.action.upper() if n.action else ""

    lines = []
    lines.append(f"  [{type_label}] {n.repo} #{n.number} — {n.title}")
    if action_label:
        lines.append(f"         Action: {action_label}")
    if n.sender:
        lines.append(f"         From: {n.sender}")
    if n.url:
        lines.append(f"         URL: {n.url}")
    return "\n".join(lines)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Check GitHub notifications from Gmail")
    parser.add_argument("--all", action="store_true", help="Show all (not just unread)")
    parser.add_argument("--hours", type=int, default=None, help="Filter by hours back")
    parser.add_argument("--repo", type=str, default=None, help="Filter by repo (owner/name)")
    parser.add_argument("--type", type=str, default=None, help="Filter by type: workflow, pull_request, issue, account, security")
    parser.add_argument("--actionable", action="store_true", help="Only show items needing action (exclude informational)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    print(f"Checking GitHub notifications via Gmail IMAP...")
    print(f"Account: {GITHUB_EMAIL}")
    print()

    notifications = check_github_notifications(
        unread_only=not args.all,
        hours=args.hours,
        repo_filter=args.repo,
    )

    # Apply type filter
    if args.type:
        notifications = [n for n in notifications if n.type == args.type]

    # Apply actionable filter
    if args.actionable:
        informational_actions = {"subscribed", "mentioned", "referenced"}
        notifications = [n for n in notifications if n.action not in informational_actions]

    if not notifications:
        print("  No GitHub notifications found.")
        return

    if args.json:
        output = [asdict(n) for n in notifications]
        print(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        print(f"  Found {len(notifications)} GitHub notification(s):\n")
        for i, n in enumerate(notifications, 1):
            try:
                print(f"  {i}. {format_notification(n, i)}")
            except UnicodeEncodeError:
                safe = format_notification(n, i).encode("ascii", "replace").decode("ascii")
                print(f"  {i}. {safe}")
            print()

    # Summary
    types = {}
    for n in notifications:
        types[n.type] = types.get(n.type, 0) + 1
    print(f"  Summary: {', '.join(f'{v} {k}' for k, v in sorted(types.items()))}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
LifeWorkspace Career Map — CLI Tool
Manage CVs, cover letters, applications, and career planning.
"""

import argparse
import csv
import json
import os
import sys
import io
from datetime import datetime, timedelta
from pathlib import Path

# Fix encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Paths
BASE_DIR = Path(__file__).parent.parent
DOCS_DIR = BASE_DIR / "docs"
CV_DIR = BASE_DIR / "cv"
LETTRES_DIR = BASE_DIR / "lettres"
EMAILS_DIR = BASE_DIR / "emails"
ENTRETIEN_DIR = BASE_DIR / "entretien"
SUIVI_DIR = BASE_DIR / "suivi"
TEMPLATES_DIR = BASE_DIR / "templates"

# Colors
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
BOLD = "\033[1m"
RESET = "\033[0m"


def cmd_status(args):
    """Show career status overview."""
    print(f"\n{BOLD}{BLUE}{'='*50}{RESET}")
    print(f"{BOLD}  LIFEWORKSPACE CAREER MAP -- STATUS{RESET}")
    print(f"{BOLD}{BLUE}{'='*50}{RESET}\n")

    # Identity
    print(f"{BOLD}Identity:{RESET}")
    print(f"  Name: MAHI Kamel Abdelghani (Kamel Mahi)")
    print(f"  Email: kamelmahi71@gmail.com")
    print(f"  Phone: +213 676 773 892")
    print(f"  LinkedIn: linkedin.com/in/kamel-adelghani-mahi-16b78511b")
    print(f"  Portfolio: kamelmahi.netlify.app")
    print()

    # Education
    print(f"{BOLD}Education:{RESET}")
    print(f"  BTS Gestion des Stocks et Logistique — {YELLOW}IN PROGRESS{RESET} (expected 2026)")
    print(f"  BA English Language & Literature — {GREEN}COMPLETE{RESET} (2015-2020)")
    print(f"  Bac Lettres & Langues Étrangères — {GREEN}COMPLETE{RESET} (2015)")
    print()

    # Skills
    print(f"{BOLD}Key Skills:{RESET}")
    print(f"  VBA (Advanced) | Python (Intermediate) | Excel (Advanced)")
    print(f"  Wilson EOQ | ABC Analysis | FIFO/CMUP | Inventory Management")
    print(f"  Arabic (Native) | French (B1-B2) | English (C1)")
    print()

    # Platforms
    print(f"{BOLD}Platforms:{RESET}")
    print(f"  LinkedIn: {GREEN}9/10{RESET} — needs logistics headline update")
    print(f"  Fiverr: {GREEN}12/12{RESET} — 2 gigs live")
    print(f"  Upwork: {YELLOW}Needs connects{RESET} — 1 remaining")
    print(f"  Portfolio: {GREEN}Deployed{RESET} — needs DSS screenshots")
    print(f"  GitHub: {YELLOW}Needs README{RESET} on logistics repo")
    print()

    # Gaps
    print(f"{BOLD}Critical Gaps:{RESET}")
    print(f"  {RED}1. Service National — NOT VERIFIED{RESET}")
    print(f"  {YELLOW}2. BTS diploma — not received{RESET}")
    print(f"  {YELLOW}3. French CV — needs .docx + photo{RESET}")
    print(f"  {YELLOW}4. DSS figures — estimates, verify{RESET}")
    print(f"  {YELLOW}5. LinkedIn headline — not logistics-focused{RESET}")
    print()


def cmd_cvs(args):
    """List all CV versions."""
    print(f"\n{BOLD}{BLUE}{'='*50}{RESET}")
    print(f"{BOLD}  CV VERSIONS{RESET}")
    print(f"{BOLD}{BLUE}{'='*50}{RESET}\n")

    cv_files = list(CV_DIR.glob("*.md"))
    if not cv_files:
        print(f"  {YELLOW}No CV files found in {CV_DIR}{RESET}")
        return

    for f in sorted(cv_files):
        lang = "FR" if "_FR" in f.name else "EN"
        print(f"  {GREEN}✅{RESET} {f.name} ({lang})")

    print(f"\n  {BOLD}For Algerian logistics jobs:{RESET} Use FR version")
    print(f"  {BOLD}For international:{RESET} Use EN version")
    print()


def cmd_gaps(args):
    """Show what's missing before applying."""
    print(f"\n{BOLD}{BLUE}{'='*50}{RESET}")
    print(f"{BOLD}  GAPS -- What's Missing{RESET}")
    print(f"{BOLD}{BLUE}{'='*50}{RESET}\n")

    gaps_file = DOCS_DIR / "GAPS.md"
    if gaps_file.exists():
        content = gaps_file.read_text(encoding="utf-8")
        # Print critical gaps section
        in_section = False
        for line in content.split("\n"):
            if "Critical" in line:
                in_section = True
            elif "Important" in line and in_section:
                break
            if in_section:
                print(f"  {line}")
    else:
        print(f"  {YELLOW}GAPS.md not found{RESET}")
    print()


def cmd_track(args):
    """Track applications."""
    tracker_file = SUIVI_DIR / "applications.csv"

    if args.add:
        # Add new application
        row = {
            "entreprise": args.add,
            "poste": args.poste or "",
            "canal": args.canal or "",
            "deadline": args.deadline or "",
            "date_candidature": "",
            "statut": "🟡 À postuler",
            "relance_prevue": "",
            "notes": ""
        }

        file_exists = tracker_file.exists()
        with open(tracker_file, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=row.keys())
            if not file_exists:
                writer.writeheader()
            writer.writerow(row)

        print(f"  {GREEN}✅ Added: {args.add} ({args.poste or 'TBD'}){RESET}")
        return

    if args.list:
        # List all applications
        if not tracker_file.exists():
            print(f"  {YELLOW}No applications tracked yet{RESET}")
            return

        with open(tracker_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            print(f"\n  {'Entreprise':<25} {'Poste':<25} {'Deadline':<15} {'Statut'}")
            print(f"  {'─'*25} {'─'*25} {'─'*15} {'─'*20}")
            for row in reader:
                print(f"  {row['entreprise']:<25} {row['poste']:<25} {row.get('deadline',''):<15} {row.get('statut','')}")
        print()
        return

    # Default: show summary
    if tracker_file.exists():
        with open(tracker_file, "r", encoding="utf-8") as f:
            count = sum(1 for _ in csv.reader(f)) - 1  # minus header
        print(f"\n  {BOLD}Applications tracked:{RESET} {count}")
    else:
        print(f"\n  {YELLOW}No applications tracked yet{RESET}")
    print(f"\n  {BOLD}Usage:{RESET}")
    print(f"    python career.py track --add 'Company' --poste 'Job' --deadline '2026-08-01'")
    print(f"    python career.py track --list")
    print()


def cmd_lettre(args):
    """Generate a cover letter from template."""
    template_file = TEMPLATES_DIR / "lettre_template.md"
    if not template_file.exists():
        print(f"  {RED}Template not found: {template_file}{RESET}")
        return

    template = template_file.read_text(encoding="utf-8")
    company = args.company or "[NOM DE L'ENTREPRISE]"
    poste = args.poste or "[POSTE]"

    letter = template.replace("[ENTREPRISE]", company).replace("[POSTE]", poste)

    output_file = LETTRES_DIR / f"Lettre_{company.replace(' ', '_')}.md"
    output_file.write_text(letter, encoding="utf-8")

    print(f"  {GREEN}✅ Generated: {output_file.name}{RESET}")
    print(f"  {BOLD}Company:{RESET} {company}")
    print(f"  {BOLD}Position:{RESET} { poste}")
    print()


def cmd_deadlines(args):
    """Show upcoming deadlines."""
    print(f"\n{BOLD}{BLUE}{'='*50}{RESET}")
    print(f"{BOLD}  UPCOMING DEADLINES{RESET}")
    print(f"{BOLD}{BLUE}{'='*50}{RESET}\n")

    today = datetime.now()
    deadlines = [
        ("EVORIA COSMETICS", "2026-07-30", "Gestionnaire de Stocks", "Emploitic"),
        ("BOMARE COMPANY", "2026-08-01", "Gestionnaire de Stocks", "Email"),
        ("Mars Logistique", "2026-09-21", "Gestionnaire de Stocks", "Email"),
    ]

    for company, deadline_str, poste, canal in deadlines:
        deadline = datetime.strptime(deadline_str, "%Y-%m-%d")
        days_left = (deadline - today).days
        status = f"{RED}🔴 {days_left} days left{RESET}" if days_left <= 3 else f"{YELLOW}🟡 {days_left} days left{RESET}"
        if days_left < 0:
            status = f"{RED}❌ PASSED{RESET}"

        print(f"  {BOLD}{company}{RESET} — {poste}")
        print(f"    Deadline: {deadline_str} | Canal: {canal}")
        print(f"    Status: {status}")
        print()


def main():
    parser = argparse.ArgumentParser(
        description="LifeWorkspace Career Map — CLI Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # status
    subparsers.add_parser("status", help="Show career status overview")

    # cvs
    subparsers.add_parser("cvs", help="List all CV versions")

    # gaps
    subparsers.add_parser("gaps", help="Show what's missing before applying")

    # track
    track_parser = subparsers.add_parser("track", help="Track applications")
    track_parser.add_argument("--add", help="Add new application (company name)")
    track_parser.add_argument("--poste", help="Job title")
    track_parser.add_argument("--canal", help="Application channel")
    track_parser.add_argument("--deadline", help="Deadline (YYYY-MM-DD)")
    track_parser.add_argument("--list", action="store_true", help="List all applications")

    # lettre
    lettre_parser = subparsers.add_parser("lettre", help="Generate cover letter")
    lettre_parser.add_argument("--company", help="Company name")
    lettre_parser.add_argument("--poste", help="Job title")

    # deadlines
    subparsers.add_parser("deadlines", help="Show upcoming deadlines")

    args = parser.parse_args()

    if args.command == "status":
        cmd_status(args)
    elif args.command == "cvs":
        cmd_cvs(args)
    elif args.command == "gaps":
        cmd_gaps(args)
    elif args.command == "track":
        cmd_track(args)
    elif args.command == "lettre":
        cmd_lettre(args)
    elif args.command == "deadlines":
        cmd_deadlines(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

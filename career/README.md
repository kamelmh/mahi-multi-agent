# LifeWorkspace Career Map

> **Personal career management system** — CVs, cover letters, applications, platforms, all in one place.
> **Author:** MAHI Kamel Abdelghani (Kamel Mahi)
> **Last Updated:** 2026-07-29

---

## What This Is

A self-contained, portable career management repo. Everything you need to apply for jobs, track applications, and manage your professional presence — extracted from LifeWorkspace and organized for on-the-go use.

## Structure

```
lifeworkspace-career-map/
├── README.md                    ← You are here
├── docs/                        ← Strategy & planning
│   ├── CAREER_MASTERY_MAP.md    ← Single source of truth
│   ├── CHECKLIST_BEFORE_SENDING.md ← Pre-application checklist
│   ├── CV_VERSIONS_MAP.md       ← Every CV variant tracked
│   ├── PLATFORMS_AUDIT.md       ← LinkedIn, Fiverr, Upwork status
│   └── GAPS.md                  ← What's missing
├── cv/                          ← CV files
│   ├── CV_Mahi_Kamel_FR.md      ← French CV (logistics)
│   └── CV_Mahi_Kamel_EN.md      ← English CV (logistics)
├── lettres/                     ← Cover letters
│   ├── Lettre_EVORIA.md
│   ├── Lettre_BOMARE.md
│   ├── Lettre_Mars.md
│   ├── Lettre_Keller.md
│   ├── Lettre_Spontanee.md
│   ├── Lettre_Fonction_Publique.md
│   └── Lettre_Internationale.md
├── emails/                      ← Email templates
│   └── Modeles_Emails.md
├── entretien/                   ← Interview prep
│   └── Preparation_Entretien.md
├── suivi/                       ← Application tracking
│   └── Suivi_Candidatures.csv
├── templates/                   ← Reusable templates
│   ├── cv_template.md
│   ├── lettre_template.md
│   └── email_template.md
├── scripts/                     ← Automation
│   └── career.py                ← CLI tool
├── requirements.txt
└── .gitignore
```

## Quick Start

```bash
# See your career status
python scripts/career.py status

# List all CVs
python scripts/career.py cvs

# Generate a cover letter from template
python scripts/career.py lettre --company "Company Name" --poste "Gestionnaire de Stocks"

# Track an application
python scripts/career.py track --add "EVORIA COSMETICS" --poste "Gestionnaire de Stocks" --deadline "2026-07-30"

# Check what's missing before applying
python scripts/career.py gaps
```

## Current Target Companies

| Company | Deadline | Status |
|---------|----------|--------|
| EVORIA COSMETICS | Jul 30, 2026 | 🔴 URGENT |
| BOMARE COMPANY | Aug 1, 2026 | 🔴 URGENT |
| Mars Logistique | Sep 21, 2026 | 🟡 Ready |
| Keller Algérie | TBD | 🟡 Ready |

## Personal Info

| Field | Value |
|-------|-------|
| **Legal Name** | MAHI Kamel Abdelghani |
| **Preferred Name** | Kamel Mahi |
| **Email** | kamelmahi71@gmail.com |
| **Phone** | +213 676 773 892 |
| **LinkedIn** | linkedin.com/in/kamel-adelghani-mahi-16b78511b |
| **Portfolio** | kamelmahi.netlify.app |
| **GitHub** | github.com/kamelmh |

## License

Private — MAHI Kamel Abdelghani

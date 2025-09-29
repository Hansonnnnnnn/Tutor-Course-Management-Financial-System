# Tutor Lesson Records & Finance System

A lightweight CLI tool to record tutoring lessons and track income using a simple CSV backend.

## Features
- Add new lesson records with date, duration, rate, topic, homework, performance, notes, and next plan
- Query records by student name, student ID, topic, and month (YYYY-MM)
- Show all students with lesson counts
- Financial summary (total lessons, total hours, total income)
- Monthly summary (lessons, hours, income)
- Optional pretty tables with `rich`; plain-text fallback included

## Requirements
- Python 3.8+
- CSV file is stored as UTF-8: `teaching_records.csv`

## Optional dependency
- `rich` (for prettier tables)

Install optional dependency:
```bash
pip install rich
```

## Project structure
```
English/
  main.py               # CLI entry; menus, inputs, and output tables
  database_manager.py   # CSV schema checks, CRUD, queries, summaries
  models.py             # Dataclass for TeachingRecord
  teaching_records.csv  # Data file (auto-created on first run)
  README.md             # This file
```

## Getting started
1) (Optional) Create and activate a virtual environment
```bash
python -m venv .venv
# Windows PowerShell
. .venv\Scripts\Activate.ps1
# Windows cmd
.venv\Scripts\activate.bat
# macOS/Linux
source .venv/bin/activate
```

2) Install optional dependency for better tables (recommended):
```bash
pip install rich
```

3) Run the app
```bash
python main.py
```

## Usage overview
- The menu will guide you through:
  - Add new lesson record
  - Query lesson records
  - Show all students
  - Show financial summary
  - Show monthly summary
  - Exit

### Data entry notes
- Date format: `YYYY-MM-DD` (press Enter for today)
- Duration: minutes (integer > 0)
- Hourly Rate: currency in $ (float > 0)
- Month field is derived automatically (`YYYY-MM`) when saving

## CSV schema
File: `teaching_records.csv`

Columns:
- `student_name`
- `student_id`
- `date` (YYYY-MM-DD)
- `month` (YYYY-MM, auto-derived)
- `duration_minutes` (int)
- `hourly_rate` (float)
- `total_income` (float; auto-calculated)
- `topic_covered`
- `homework_assigned`
- `student_performance` (int: 1-10)
- `notes`
- `next_plan`

The app auto-initializes the CSV file and performs a one-time migration to add `month` if missing.

## Tips & troubleshooting
- If you see garbled emoji/symbols on Windows, use Windows Terminal or a font that supports emoji.
- If `teaching_records.csv` becomes corrupted, back it up, then let the app recreate a fresh file.
- Ensure your shell encoding is UTF-8 for best results.

## Localization
- The CLI text is in English. Currency symbol remains `$` by design.
- To switch locale manually, edit the prompt strings in `main.py` and message text in `database_manager.py`.

## License
- MIT - Massachusetts Institute of Technology License

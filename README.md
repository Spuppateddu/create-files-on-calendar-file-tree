# Calendar File Creator

This Python script creates markdown files in a calendar-based folder structure. It can create different types of files (work, notes, workout, youtube, news) based on configuration settings.

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Copy the `example.env` file to `.env` and customize the values as needed:
```bash
cp example.env .env
```

## Configuration

The `.env` file allows you to control various aspects of the script:

### Base Path
- `CALENDAR_BASE_PATH`: The base directory where all files will be created (default: "calendar")

### File Creation Controls
- Whether files can be created for past dates
- Which types of files can be created for the current day
- Which types of files can be created for future dates
- Which empty past files can be automatically deleted

The script will automatically delete past files that are empty (containing only the title) if the corresponding deletion flag is set to true in the `.env` file.

## Usage

Run the script:
```bash
python calendar_files_creator.py
```

The script will:
1. Create files for the current day
2. Create files for the next 30 days (configurable in the code)
3. Delete empty past files if configured to do so (files that only contain the title)

## Folder Structure

The script creates a folder structure like this (inside the base path):
```
calendar/
└── 2025/
    └── 06-June/
        ├── 01-Monday/
        │   ├── work.md
        │   ├── note.md
        │   ├── workout.md
        │   ├── youtube.md
        │   └── news.md
        └── 02-Tuesday/
            └── ...
```

Each markdown file will contain a header with the date and type, for example:
```markdown
# 5 Thursday June 2025 - Note
```

If a file already exists and is not empty, the script will skip it (no duplicates or overwrites).

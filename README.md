# Student OS

Student OS is a local student-life dashboard for organizing classes, assignments, attendance, notes, exams, tasks, projects, study sessions, habits, expenses, and grades. It runs on your computer and saves records in a local SQLite database.

## Features

- 33 databases across academics, notes and resources, exams, productivity, personal life, finances, self-learning, collaboration, progress, and student resources.
- Add, edit, and delete records; search and sort database entries.
- Link related records, such as courses with assignments, exams, and study sessions.
- Dashboard with upcoming deadlines and quick capture for tasks, notes, and study sessions.
- Local persistence: your entries remain in the database between launches.

## Run on Windows

Install Python 3.10 or newer. From this project folder, either double-click `start.bat` or run:

```bash
py -m student_os web
```

Keep the terminal window open while using the app. Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser. Stop the server with **Ctrl+C**.

You can also run the command from Git Bash or PowerShell, as long as the terminal is in this folder. If `py` is not available, use:

```bash
python -m student_os web
```

To use another port, add `--port`, for example `py -m student_os web --port 8080`.

## Run on macOS or Linux

From this folder, run:

```bash
python3 -m student_os web
```

Then open [http://127.0.0.1:8000](http://127.0.0.1:8000). Stop the server with **Ctrl+C**.

## Data and GitHub

On first launch, Student OS creates `student_os.sqlite3` in this project folder and loads the sample records. New and edited records are saved there. The database is listed in `.gitignore`, so it is not uploaded to GitHub with the source code.

## Project files

```text
student_os/
  schema.py       Database definitions and sample records
  web.py          Local web server and SQLite storage
  web/
    app.js        Dashboard interactions and entry forms
    index.html    Dashboard page
    styles.css    Dashboard styles
start.bat         Windows launcher
start.sh          macOS/Linux launcher
requirements.txt  Python dependency list
```

To check the schema's sample relations and internal links, run:

```bash
py -m student_os validate
```

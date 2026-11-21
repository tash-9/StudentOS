# Student OS

A standalone student-life dashboard based on the supplied Student OS blueprint. No Notion account, API key, or third-party Python package is required.

## Run on Windows

1. Install Python 3.10 or newer.
2. Double-click `start.bat`, or open PowerShell in this folder and run:

   ```powershell
   py -m student_os
   ```

3. Open [http://127.0.0.1:8000](http://127.0.0.1:8000).
4. Stop the server with Ctrl+C.

## Run on macOS or Linux

```sh
python3 -m student_os
```

Then open [http://127.0.0.1:8000](http://127.0.0.1:8000).

## Features

- Dashboard with upcoming assignments, tasks, and exams.
- 33 databases across academics, productivity, personal life, finances, learning, collaboration, and student resources.
- Create, edit, delete, search, and sort records.
- Relation fields for connecting records across databases.
- Sample records on first launch, saved locally in `student_os.sqlite3`.
- Dark mode preference saved in your browser.

The app stores data on this computer. Delete `student_os.sqlite3` to reset the sample workspace. Keep that database file out of GitHub; `.gitignore` excludes it.

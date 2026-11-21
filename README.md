# 🎓 Student OS

A connected Notion workspace for students: one set of related databases, with dashboards built from filtered views of them.

## Challenge problem

Students often track classes, assignment deadlines, notes, exams, and group work in separate places. That fragmentation adds mental load and makes important work easier to miss. Student OS gives learners one connected workspace with a deadline radar, weekly planning, and reusable profiles for high school, university, or self-learning.

It has 10 modules (Academic, Knowledge, Exams, Productivity, Personal, Finance, Self-Learning, Collaboration, Progress, Resources), 33 databases, 25 two-way relations, 23 rollups/formulas, sample data, and filtered database views for everyday student workflows.

## Two ways to use it

| | `notion` (recommended) | `zip` |
|---|---|---|
| Creates pages and databases | ✅ | ✅ |
| Property types, relations, rollups, formulas | ✅ automatic | Manual (guide included) |
| Filtered database views and home dashboard views | ✅ automatic | Manual |
| Sample data linked across databases | ✅ | ✅ (text, links after conversion) |
| Needs a Notion integration token | Yes | No |

The Notion API creates filtered database views and linked views on the home dashboard. Buttons and optional layouts such as boards or calendars can still be added in Notion; the generated **⚙️ Workspace Setup** page explains them.

## Setup

```bash
git clone <your-repo-url> student-os && cd student-os
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

### Run the local dashboard

The project also includes a complete local dashboard. It works without a Notion token and stores its records in `student_os.sqlite3` in this project folder. The first launch loads the sample data from the schema; after that, your edits persist between runs.

```bash
python -m student_os web
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000). Stop the server with `Ctrl+C`. To use another port, run `python -m student_os web --port 8080`.

The dashboard includes all 33 databases, cross-database relation selectors, search, sorting, and create/edit/delete flows. SQLite data stays on your machine. To reset the local dashboard to the original sample data, stop it and remove `student_os.sqlite3`.

### Option A: Build directly in Notion

1. Go to https://www.notion.so/profile/integrations → **New integration** (Internal). Enable Read, Update and Insert content. Copy the secret.
2. In Notion, create an empty page, then open **•••** → **Connections** → add your integration.
3. Copy `.env.example` to `.env` and fill in `NOTION_TOKEN` and `NOTION_PARENT_PAGE` (the page URL).
4. Run:

```bash
python -m student_os notion
# or: python -m student_os notion "https://www.notion.so/Student-OS-<page-id>"
```

The build can take several minutes because it creates the connected databases, sample records, formulas, and views through Notion's rate-limited API.

### Option B: Notion-importable ZIP

```bash
python -m student_os zip          # writes dist/Student-OS-Notion-Template.zip
```

In Notion, go to **Settings → Import → Text & Markdown** and upload the ZIP without unzipping it. Then follow the **⚙️ Workspace Setup** page to set property types, relations and rollups.

## Project layout

```
student_os/
  schema.py      # modules, databases, properties, sample rows, views, rollups/formulas
  template.py    # renders the Markdown/CSV page tree + setup guide
  export_zip.py  # writes the importable ZIP
  notion.py      # Notion API builder
  __main__.py    # CLI: zip | notion | validate
```

To customise the workspace, edit `schema.py`: add a database with `db(...)`, a relation with a `("relation", (target, synced_name))` column, or a computed property in `COMPUTED`. Run `python -m student_os validate` to check that sample relations and links resolve.

## Notes and limits

- Status-like columns are created as **Select**, because the API can't create Notion's Status type. You can convert them in Notion if you prefer.
- The Notion builder targets API version `2026-03-11` and uses data source IDs for schemas, relations, and database entries. It also creates core filtered views and linked dashboard views through the [Views API](https://developers.notion.com/guides/data-apis/working-with-views), following Notion's [API upgrade guide](https://developers.notion.com/guides/get-started/upgrade-guide-2025-09-03).
- The API rejects formulas that read through relations and rollups of rollups, so progress uses a `Done Score` formula with an Average rollup, and GPA uses a `GPA Points` formula.
- The builder sets the parent page's title to “Student OS” and appends content to it. Use an empty page.

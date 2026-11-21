"""Builds the Notion-importable Markdown/CSV page tree (path -> content)."""
import csv, io
from urllib.parse import quote

from .schema import DBS, DBN, M, MODULES, ROOT, ROLLUPS

TYPE_LABEL = {"title":"Title","text":"Text","select":"Select","multi":"Multi-select","status":"Status","date":"Date",
              "number":"Number","checkbox":"Checkbox","url":"URL","files":"Files & media","relation":"Relation"}

def rel_link(frm, to):
    a = frm.split("/")[:-1]; b = to.split("/")
    i = 0
    while i < len(a) and i < len(b) - 1 and a[i] == b[i]: i += 1
    return "/".join([".."] * (len(a) - i) + [quote(p) for p in b[i:]])

files = {}  # path -> content
def page_path(title, parent=None):
    return (parent.rsplit(".md", 1)[0] + "/" if parent else "") + title + ".md"

ROOT_MD = ROOT + ".md"
HOME = page_path("🏠 Home Dashboard", ROOT_MD)
SETUP = page_path("⚙️ Workspace Setup", ROOT_MD)
RESET = page_path("🔄 Weekly Reset", ROOT_MD)
PROFILE = page_path("🎯 My Student Profile", ROOT_MD)
MOD_PATHS = {i: page_path(M[i], ROOT_MD) for i in M}
def db_path(d): return MOD_PATHS[d["module"]].rsplit(".md", 1)[0] + "/" + d["name"] + ".csv"
def link(frm, to, label): return f"[{label}]({rel_link(frm, to)})"

# ---------- CSVs ----------
for d in DBS:
    buf = io.StringIO(); w = csv.writer(buf, lineterminator="\n")
    w.writerow([c[0] for c in d["cols"]])
    for r in d["rows"]:
        assert len(r) == len(d["cols"]), (d["name"], r)
        w.writerow(r)
    files[db_path(d)] = "\ufeff" + buf.getvalue()

# ---------- module pages ----------
def view_lines(d): return "\n".join(f"- {v}" for v in d["views"])
def db_block(d, here):
    return (f"## {d['section']}\n\n{d['desc']}\n\n{link(here, db_path(d), d['name'])}\n\n"
            f"**Suggested views:**\n{view_lines(d)}\n")

EXTRA = {
    1: [],
    2: [],
    3: [("after", "## Exam Preparation Checklist\n\n" + "\n".join("- [ ] " + x for x in [
        "Review syllabus","Organize study materials","Identify weak topics","Create revision schedule",
        "Complete practice questions","Take mock tests","Review mistakes","Prepare exam essentials"]) + "\n")],
    5: [("after", "## Daily Routine\n\n### 🌅 Morning Routine\n- [ ] Wake up & hydrate\n- [ ] Review today's Daily Planner\n\n"
         "### 📖 Study Routine\n- [ ] Pick top task\n- [ ] 2 × 50-minute focus blocks\n- [ ] Log the Study Session\n\n"
         "### 🌇 Evening Routine\n- [ ] Review what got done\n- [ ] Plan tomorrow's top 3\n\n"
         "### 🌙 Sleep Routine\n- [ ] Screens off 30 min before bed\n- [ ] Journal entry\n")],
    7: [("before", "## Online Course Tracker\n\nOnline courses live in the **Courses** database (Academic Manager) so they share notes, tasks and resources. The filtered linked view is below.\n"),
        ("after", "## Personal Projects\n\nProjects live in the **Projects** database (Productivity Center). The filtered linked view is below.\n")],
    8: [("before", "## Group Projects\n\nGroup work lives in the **Projects** database (Productivity Center). The filtered linked view is below.\n\n"
         "## Team Task Manager\n\nThe team's assignments live in the **Tasks** database (Productivity Center). The filtered linked view is below.\n")],
    9: [("after", "## Personal Statistics\n\nThese linked views summarize learning activity. Use each view's **Calculate** row for totals or counts:\n\n"
         "| Statistic | Source |\n|---|---|\n| Study hours | Study Sessions → This Week → Sum of Duration (min) |\n"
         "| Tasks completed | Tasks → Completed → Count |\n| Courses completed | Courses → Completed → Count |\n"
         "| Books completed | Reading Library → Reading Status = Finished → Count |\n| Skills developed | Skills → Count |\n"
         "| Goals achieved | Goals → Completed → Count |\n")],
    10: [("after", "## Student Emergency Hub\n\n### 🚨 Emergency Contacts\n- Campus security: \n- Family: \n- Doctor: \n\n"
          "### 🏫 Important University / School Information\n- Student ID: \n- Registrar office: \n- Advisor: \n\n"
          "### 📄 Essential Documents\nSee the Documents database above.\n\n### 🔗 Useful Links\n- Student portal: \n- Library: \n- LMS: \n")],
}

for i, (title, intro) in enumerate(MODULES, start=1):
    here = MOD_PATHS[i]
    parts = [f"# {title}\n", f"{intro}\n", f"← {link(here, HOME, '🏠 Home Dashboard')}\n", "---\n"]
    parts += [x for pos, x in EXTRA.get(i, []) if pos == "before"]
    parts += [db_block(d, here) for d in DBS if d["module"] == i]
    parts += [x for pos, x in EXTRA.get(i, []) if pos == "after"]
    files[here] = "\n".join(parts)

# ---------- home ----------
h = HOME
files[h] = f"""# 🏠 Home Dashboard

**Welcome back!** Your personal command center for everything related to learning and student life.

> 💡 Each dashboard section shows a filtered view of the same connected databases, so records stay in one place.

---

## ⚡ Quick Actions

Turn each line into a Notion **Button** (`/button` → “Add page to…” the database shown):

- ➕ Add a Task → Tasks
- 📝 Capture a Note → Notes
- 📚 Add a Course → Courses
- 📅 Add an Event → Class Timetable or Daily Planner
- 🎯 Add a Goal → Goals
- 🔖 Save a Resource → Resources
- 💡 Brain Dump → Brain Dump Inbox

---

## ☀️ Today

Today's planner, tasks, study sessions and active habits appear below.

## 🚨 Deadline Radar

Overdue work and the upcoming assignments, exams and tasks that need attention.

## 📊 My Progress

Recently completed tasks, active courses and current goals.

---

## 🧭 My Workspace

""" + "\n".join(f"{i}. {link(h, MOD_PATHS[i], M[i])}" for i in M) + f"""

---

{link(h, RESET, '🔄 Weekly Reset')} · {link(h, PROFILE, '🎯 My Student Profile')} · {link(h, SETUP, '⚙️ Workspace Setup')}
"""

files[RESET] = "# 🔄 Weekly Reset\n\nEvery weekend, review your student life.\n\n" + "\n".join("- [ ] " + x for x in [
    "Review completed tasks","Check overdue assignments","Review upcoming deadlines","Organize notes and files",
    "Update course progress","Plan next week's study sessions","Review personal goals","Set next week's top priorities",
    "Process the Brain Dump Inbox","Create next week's Weekly Planner page"]) + "\n\n> ➕ Linked views: **Tasks → Completed**, **Tasks → Overdue**, **Assignments → Pending Submission**, **Goals → Active**\n"

files[PROFILE] = """# 🎯 My Student Profile

**Learning Mode:** High School / University / Self-Learner

**Current Focus:**

**Learning Goals:**

**Preferred Study Hours:**

**Current Semester or Learning Period:**

**Personal Goals:**
"""

# ---------- setup ----------
s = SETUP
rels = []
for d in DBS:
    for c in d["cols"]:
        if c[1] == "relation":
            rels.append((d["name"], c[0], c[2][0], c[2][1]))
conn = {}
for a, _, b, _ in rels:
    conn.setdefault(a, set()).add(b); conn.setdefault(b, set()).add(a)

def fmt(c):
    t = TYPE_LABEL[c[1]]
    if c[1] == "relation": return f"{t} → {c[2][0]}"
    if c[1] == "number" and c[2]: return f"{t} ({c[2]})"
    if c[1] in ("select","multi","status") and c[2]: return f"{t}: {c[2]}"
    return t

prop_tables = []
for d in DBS:
    rows = "\n".join(f"| {c[0]} | {fmt(c)} |" for c in d["cols"])
    prop_tables.append(f"### {d['name']}  ·  {M[d['module']]}\n\n| Property | Type |\n|---|---|\n{rows}\n")

files[s] = f"""# ⚙️ Workspace Setup

Make this a real Student OS: one set of connected databases, many filtered views.

← {link(s, HOME, '🏠 Home Dashboard')}

---

## 1. Choose your learner profile

| Profile | Default modules | Databases to keep front and centre |
|---|---|---|
| High School | Subjects, Homework, Timetable, Attendance, Exams | Courses (rename **Subjects**), Assignments (rename **Homework**), Class Timetable, Attendance, Exams |
| University | Courses, Semesters, Assignments, Projects, GPA | Courses, Semesters, Assignments, Projects, Grades (GPA rolls up into Semesters) |
| Self-Learner | Courses, Skills, Roadmaps, Resources, Projects | Courses (Online Courses view), Skills, Learning Roadmaps, Resources, Projects |

Set your choice in {link(s, PROFILE, '🎯 My Student Profile')}. Modules you don't need can be moved into an “Archive” page. Keep the databases, because other modules relate to them.

## 2. Convert property types

Notion imports every CSV column as Text. Open each database, click a column header → **Edit property** → **Type**, and set the types listed in section 7. Do the Select, Status, Date, Number and Checkbox columns first.

## 3. Create the relations (do these in this order)

For each row: open the database in the first column, change the property to **Relation**, pick the target database, and switch on **Show on [target]** using the name in the last column. When you convert a Text column that holds page names, Notion should link the matching sample pages. If it doesn't, re-link them by hand or delete the sample rows.

| Database | Property | Relates to | Show on target as |
|---|---|---|---|
""" + "\n".join(f"| {a} | {p} | {b} | {q} |" for a, p, b, q in rels) + f"""

### Connection map

| Database | Connects to |
|---|---|
""" + "\n".join(f"| {k} | {', '.join(sorted(conn[k]))} |" for k in
    ["Courses","Tasks","Notes","Exams","Study Sessions","Goals","Resources","Projects","Expenses","Habits"]) + f"""

## 4. Add rollups and formulas

Do these after the relations exist. **+ Add property** → Rollup / Formula.

| Database | New property | Type | Configuration |
|---|---|---|---|
""" + "\n".join(f"| {a} | {p} | {t} | `{c}` |" if t == "Formula" else f"| {a} | {p} | {t} | {c} |" for a, p, t, c in ROLLUPS) + f"""

> Add the rows in order: each formula or rollup may depend on one above it (e.g. **Done Score** before **Progress (%)**).

## 5. Create the database views

| Database | Views |
|---|---|
""" + "\n".join(f"| {d['name']} | " + "<br>".join(d["views"]) + " |" for d in DBS) + f"""

## 6. Build the dashboards

1. Open {link(s, HOME, '🏠 Home Dashboard')}. Replace each “➕ Linked view” line with `/linked` → database → view.
2. Do the same on module pages for the virtual sections (Online Course Tracker, Personal Projects, Group Projects, Team Task Manager, Personal Statistics).
3. Turn the Quick Actions into Buttons.
4. Optional: drag sections into columns, and add page icons and covers.
5. Delete the sample rows when you're ready, or keep them as examples.

## 7. Property reference

{chr(10).join(prop_tables)}
"""

# ---------- root ----------
r = ROOT_MD
files[r] = f"""# 🎓 Student OS

### Your entire learning life. One workspace.

> One place to plan, learn, organize, and grow.

---

## Start here

- {link(r, HOME, '🏠 Home Dashboard')}: your daily command center
- {link(r, SETUP, '⚙️ Workspace Setup')}: finish the setup (≈20–30 min) and pick your learner profile
- {link(r, PROFILE, '🎯 My Student Profile')}
- {link(r, RESET, '🔄 Weekly Reset')}

## Modules

""" + "\n".join(f"{i}. {link(r, MOD_PATHS[i], M[i])}" for i in M) + """

---

### STUDENT OS
*Stay organized. Keep learning. Keep growing.*
"""



def validate():
    bad = []
    for d in DBS:
        for ci, c in enumerate(d["cols"]):
            if c[1] == "relation":
                titles = {r[0] for r in DBN[c[2][0]]["rows"]}
                for r in d["rows"]:
                    for v in filter(None, [x.strip() for x in r[ci].split(",")]):
                        if v not in titles: bad.append((d["name"], c[0], v))
    # validate md links resolve
    import re, posixpath
    from urllib.parse import unquote
    for p, txt in files.items():
        if p.endswith(".md"):
            for t in re.findall(r"\]\(([^)]+)\)", txt):
                if t.startswith("http"): continue
                tgt = posixpath.normpath(posixpath.join(posixpath.dirname(p), unquote(t)))
                if tgt not in files: bad.append((p, t))
    return bad


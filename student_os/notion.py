"""Builds Student OS directly in Notion via the public API (relations, rollups, formulas, sample data)."""
import re, time, posixpath
from urllib.parse import unquote

import requests

from . import template as B
from .schema import COMPUTED

H = {"Notion-Version": "2026-03-11", "Content-Type": "application/json"}
API = "https://api.notion.com/v1"
WARN = []

def call(method, path, body=None):
    for attempt in range(6):
        try:
            r = requests.request(method, API + path, headers=H, json=body, timeout=120)
        except (requests.Timeout, requests.ConnectionError):
            time.sleep(2 + attempt * 2); continue
        if r.status_code in (429, 502, 503, 504) or r.status_code == 409:
            time.sleep(float(r.headers.get("Retry-After", 1 + attempt))); continue
        if r.status_code >= 400:
            raise RuntimeError(f"{method} {path} -> {r.status_code}: {r.text[:500]}")
        time.sleep(0.34)
        return r.json()
    raise RuntimeError(f"{method} {path} retries exhausted")

def url(i): return "https://www.notion.so/" + i.replace("-", "")
LINKS = {}  # zip path -> notion id

# ---------- markdown -> blocks ----------
TOK = re.compile(r"\*\*(.+?)\*\*|`(.+?)`|\[([^\]]+)\]\(([^)]+)\)|\*(.+?)\*")
def rich(s, here=None):
    out, pos = [], 0
    def add(t, ann=None, link=None):
        if not t: return
        for k in range(0, len(t), 1900):
            o = {"type": "text", "text": {"content": t[k:k+1900]}}
            if link: o["text"]["link"] = {"url": link}
            if ann: o["annotations"] = ann
            out.append(o)
    for m in TOK.finditer(s):
        add(s[pos:m.start()]); pos = m.end()
        if m.group(1) is not None: add(m.group(1), {"bold": True})
        elif m.group(2) is not None: add(m.group(2), {"code": True})
        elif m.group(3) is not None:
            tgt = m.group(4)
            if not tgt.startswith("http"):
                p = posixpath.normpath(posixpath.join(posixpath.dirname(here), unquote(tgt)))
                tgt = url(LINKS[p]) if p in LINKS else None
            add(m.group(3), None, tgt)
        else: add(m.group(5), {"italic": True})
    add(s[pos:])
    return out

def blk(t, **c): return {"object": "block", "type": t, t: c}
def md_blocks(md, here=None, skip_h1=True):
    lines, out, i = md.split("\n"), [], 0
    while i < len(lines):
        l = lines[i]; s = l.strip()
        if not s: i += 1; continue
        if s.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r"-+", c) for c in cells): rows.append(cells)
                i += 1
            w = len(rows[0])
            out.append(blk("table", table_width=w, has_column_header=True, has_row_header=False,
                children=[blk("table_row", cells=[rich(c.replace("<br>", "\n"), here) for c in (r + [""] * w)[:w]]) for r in rows]))
            continue
        if s.startswith("# "):
            if not skip_h1: out.append(blk("heading_1", rich_text=rich(s[2:], here)))
        elif s.startswith("### "): out.append(blk("heading_3", rich_text=rich(s[4:], here)))
        elif s.startswith("## "): out.append(blk("heading_2", rich_text=rich(s[3:], here)))
        elif s == "---": out.append(blk("divider"))
        elif s.startswith("- [ ] "): out.append(blk("to_do", rich_text=rich(s[6:], here), checked=False))
        elif s.startswith("- "): out.append(blk("bulleted_list_item", rich_text=rich(s[2:], here)))
        elif re.match(r"\d+\. ", s): out.append(blk("numbered_list_item", rich_text=rich(s.split(". ", 1)[1], here)))
        elif s.startswith("> "):
            t = s[2:]; icon = "💡"
            for e in ("➕", "💡"):
                if t.startswith(e): icon, t = e, t[len(e):].strip()
            out.append(blk("callout", rich_text=rich(t, here), icon={"type": "emoji", "emoji": icon}, color="gray_background"))
        else: out.append(blk("paragraph", rich_text=rich(s, here)))
        i += 1
    return out

def append(pid, blocks):
    created = []
    for k in range(0, len(blocks), 90):
        created.extend(call("PATCH", f"/blocks/{pid}/children", {"children": blocks[k:k+90]}).get("results", []))
    return created

def split_icon(title):
    e, rest = title.split(" ", 1)
    return e, rest

def page(parent, title, icon=None):
    body = {"parent": {"page_id": parent}, "properties": {"title": {"title": [{"text": {"content": title}}]}}}
    if icon: body["icon"] = {"type": "emoji", "emoji": icon}
    return call("POST", "/pages", body)["id"]

# ---------- database schema ----------
DB_ICON = {"Courses":"📘","Semesters":"🗓️","Class Timetable":"⏰","Assignments":"📄","Attendance":"✅","Notes":"🗒️",
  "Resources":"🔖","Reading Library":"📖","Brain Dump Inbox":"💭","Exams":"🧪","Revision Planner":"🔁","Syllabus Tracker":"📋",
  "Tasks":"☑️","Projects":"🛠️","Daily Planner":"☀️","Weekly Planner":"📆","Study Sessions":"⏱️","Habits":"🔥","Goals":"🎯",
  "Personal Journal":"📓","Expenses":"💸","Monthly Budget":"🧾","Savings Goals":"🐷","Subscriptions":"🔄","Skills":"🧠",
  "Learning Roadmaps":"🗺️","Meeting Notes":"🗣️","Grades":"💯","Achievements":"🏅","Monthly Reviews":"🪞","Contacts":"📇",
  "Documents":"🗂️","Scholarships & Opportunities":"🎓"}
COLORS = ["blue","green","yellow","orange","red","purple","pink","brown","gray","default"]
STATUS_COLORS = {"Not Started":"gray","In Progress":"blue","Done":"green","Completed":"green","Submitted":"purple","Overdue":"red",
  "Active":"green","Archived":"gray","High":"red","Medium":"yellow","Low":"blue","Upcoming":"yellow","Current":"green"}

def select_filter(prop, operator, value):
    return {"property": prop, "select": {operator: value}}

def date_filter(prop, operator, value=None):
    return {"property": prop, "date": {operator: value if value is not None else {}}}

def all_filters(*filters):
    return {"and": list(filters)}

# Portable relative date filters stay current as the student moves through the semester.
VIEW_SPECS = {
    "Tasks": [
        ("Today", all_filters(date_filter("Due Date", "equals", "today"), select_filter("Status", "does_not_equal", "Done"))),
        ("Upcoming", all_filters(date_filter("Due Date", "after", "today"), select_filter("Status", "does_not_equal", "Done"))),
        ("Overdue", all_filters(date_filter("Due Date", "before", "today"), select_filter("Status", "does_not_equal", "Done"))),
        ("Completed", select_filter("Status", "equals", "Done")),
        ("Team Tasks", select_filter("Category", "equals", "Team")),
    ],
    "Assignments": [("Pending Submission", select_filter("Status", "equals", ["Not Started", "In Progress", "Overdue"]))],
    "Courses": [("Active", select_filter("Status", "equals", "Active")),
                ("Completed", select_filter("Status", "equals", "Completed")),
                ("Online Courses", select_filter("Course Type", "equals", "Online Course"))],
    "Daily Planner": [("Today", date_filter("Date", "equals", "today"))],
    "Weekly Planner": [("This Week", date_filter("Week Start", "this_week"))],
    "Study Sessions": [("This Week", date_filter("Date", "this_week"))],
    "Habits": [("Active", select_filter("Status", "equals", "Active"))],
    "Goals": [("Active", select_filter("Status", "equals", "Active")),
              ("Completed", select_filter("Status", "equals", "Completed"))],
    "Exams": [("Upcoming", select_filter("Status", "equals", "Upcoming")),
              ("Completed", select_filter("Status", "equals", "Completed"))],
    "Projects": [("Personal Projects", select_filter("Type", "equals", "Personal")),
                 ("Group Projects", select_filter("Type", "equals", "Group"))],
    "Reading Library": [("Finished", select_filter("Reading Status", "equals", "Finished"))],
    "Expenses": [("This Month", date_filter("Date", "this_month"))],
    "Skills": [("All Skills", None)],
}

def create_database_views(dbid, source_id):
    for dbname, specs in VIEW_SPECS.items():
        for name, filter_spec in specs:
            body = {"database_id": dbid[dbname], "data_source_id": source_id[dbname], "name": name, "type": "table"}
            if filter_spec:
                body["filter"] = filter_spec
            call("POST", "/views", body)
        log("views", dbname, "done")

def heading_anchors(blocks, created):
    anchors = {}
    for block, result in zip(blocks, created):
        if block.get("type", "").startswith("heading_"):
            kind = block["type"]
            title = "".join(x.get("text", {}).get("content", "") for x in block[kind].get("rich_text", []))
            anchors[title] = result["id"]
            clean_title = re.sub(r"^[^\w]+", "", title).strip()
            if clean_title:
                anchors[clean_title] = result["id"]
    return anchors

def create_linked_views(page_id, anchors, sections, source_id):
    for heading, views in sections.items():
        anchor = anchors.get(heading)
        if not anchor:
            log("linked view section missing:", heading)
            continue
        # Inserting each view after the same heading reverses its order, so create backwards.
        for dbname, view_name in reversed(views):
            filter_spec = next((f for name, f in VIEW_SPECS[dbname] if name == view_name), None)
            body = {"create_database": {"parent": {"type": "page_id", "page_id": page_id},
                        "position": {"type": "after_block", "block_id": anchor}},
                    "data_source_id": source_id[dbname], "name": f"{view_name} — {dbname}", "type": "table"}
            if filter_spec:
                body["filter"] = filter_spec
            call("POST", "/views", body)
        log("linked views", heading, "done")

def create_dashboard_views(home_id, blocks, created, source_id):
    sections = {
        "Today": [("Tasks", "Today"), ("Daily Planner", "Today"), ("Study Sessions", "This Week"), ("Habits", "Active")],
        "Deadline Radar": [("Tasks", "Overdue"), ("Assignments", "Pending Submission"), ("Exams", "Upcoming"), ("Tasks", "Upcoming")],
        "My Progress": [("Tasks", "Completed"), ("Study Sessions", "This Week"), ("Courses", "Active"), ("Goals", "Active")],
    }
    create_linked_views(home_id, heading_anchors(blocks, created), sections, source_id)

def create_module_views(anchors_by_page, source_id):
    sections = {
        7: {"Online Course Tracker": [("Courses", "Online Courses")],
            "Personal Projects": [("Projects", "Personal Projects")]},
        8: {"Group Projects": [("Projects", "Group Projects")],
            "Team Task Manager": [("Tasks", "Team Tasks")]},
        9: {"Personal Statistics": [("Study Sessions", "This Week"), ("Tasks", "Completed"),
            ("Courses", "Completed"), ("Reading Library", "Finished"), ("Skills", "All Skills"), ("Goals", "Completed")]},
    }
    for module, section_views in sections.items():
        page_id = LINKS[B.MOD_PATHS[module]]
        create_linked_views(page_id, anchors_by_page.get(module, {}), section_views, source_id)

def opts(detail):
    return [{"name": o, "color": STATUS_COLORS.get(o, COLORS[k % len(COLORS)])} for k, o in enumerate(detail.split(" · "))]
def prop_schema(c):
    n, t, d = c
    if t == "title": return {"title": {}}
    if t == "text": return {"rich_text": {}}
    if t in ("select", "status"): return {"select": {"options": opts(d)}}
    if t == "multi": return {"multi_select": {"options": opts(d)}}
    if t == "date": return {"date": {}}
    if t == "number": return {"number": {"format": "number" if d != "Currency" else "number_with_commas"}}
    if t == "checkbox": return {"checkbox": {}}
    if t == "url": return {"url": {}}
    if t == "files": return {"files": {}}
def prop_value(c, v):
    n, t, d = c
    if t == "title": return {"title": [{"text": {"content": v}}]}
    if t == "text": return {"rich_text": [{"text": {"content": v}}]}
    if t in ("select", "status"): return {"select": {"name": v}}
    if t == "multi": return {"multi_select": [{"name": x.strip()} for x in v.split(",")]}
    if t == "date": return {"date": {"start": v}}
    if t == "number": return {"number": float(v)}
    if t == "checkbox": return {"checkbox": v == "Yes"}
    if t == "url": return {"url": v}
    return None

def log(*a): print(*a, flush=True)


def page_id_from(url_or_id):
    ids = re.findall(r"[0-9a-f]{32}", url_or_id.replace("-", "").lower())
    if not ids: raise SystemExit(f"Could not find a Notion page ID in: {url_or_id}")
    return ids[-1]


def build(parent_url, token):
    H["Authorization"] = f"Bearer {token}"
    PARENT = page_id_from(parent_url)
    try:
        call("GET", f"/pages/{PARENT}")
    except RuntimeError as e:
        raise SystemExit(f"Cannot open the parent page. Share it with your integration (••• → Connections).\n{e}")
    call("PATCH", f"/pages/{PARENT}", {"icon": {"type": "emoji", "emoji": "🎓"},
        "properties": {"title": {"title": [{"text": {"content": "Student OS"}}]}}})
    root = PARENT
    LINKS[B.ROOT_MD] = root

    append(root, md_blocks("### Your entire learning life. One workspace.\n\n> 💡 One place to plan, learn, organize, and grow.\n\n---\n\n## Start here"))
    for path in [B.HOME, B.SETUP, B.PROFILE, B.RESET]:
        e, t = split_icon(path.rsplit("/", 1)[1][:-3]); LINKS[path] = page(root, t, e)
    append(root, md_blocks("## Modules"))
    for i in B.M:
        e, t = split_icon(B.M[i]); LINKS[B.MOD_PATHS[i]] = page(root, t, e)
    append(root, md_blocks("---\n\n### STUDENT OS\n\n*Stay organized. Keep learning. Keep growing.*"))
    log("pages created")

    # modules + databases
    dbid, source_id = {}, {}
    module_anchors = {}
    for i, (title, intro) in enumerate(B.MODULES, start=1):
        here = B.MOD_PATHS[i]; pid = LINKS[here]
        module_anchors[i] = {}
        append(pid, md_blocks(f"{intro}\n\n← [🏠 Home Dashboard]({B.rel_link(here, B.HOME)})\n\n---", here))
        for pos, x in B.EXTRA.get(i, []):
            if pos == "before":
                blocks = md_blocks(x, here)
                created = append(pid, blocks)
                module_anchors[i].update(heading_anchors(blocks, created))
        for d in [d for d in B.DBS if d["module"] == i]:
            append(pid, md_blocks(f"## {d['section']}\n\n{d['desc']}", here))
            props = {c[0]: prop_schema(c) for c in d["cols"] if c[1] != "relation"}
            r = call("POST", "/databases", {"parent": {"page_id": pid}, "icon": {"type": "emoji", "emoji": DB_ICON[d["name"]]},
                "title": [{"text": {"content": d["name"]}}], "is_inline": True,
                "initial_data_source": {"properties": props}})
            dbid[d["name"]] = r["id"]
            source_id[d["name"]] = r["data_sources"][0]["id"]
            LINKS[B.db_path(d)] = r["id"]
        for pos, x in B.EXTRA.get(i, []):
            if pos == "after":
                blocks = md_blocks(x, here)
                created = append(pid, blocks)
                module_anchors[i].update(heading_anchors(blocks, created))
        log("module", i, "done")

    # relations (two-way, renamed on target)
    for d in B.DBS:
        for c in d["cols"]:
            if c[1] != "relation": continue
            tgt, synced = c[2]
            r = call("PATCH", f"/data_sources/{source_id[d['name']]}", {"properties": {c[0]: {"relation": {
                "data_source_id": source_id[tgt], "type": "dual_property", "dual_property": {}}}}})
            auto = r["properties"][c[0]]["relation"]["dual_property"]["synced_property_name"]
            if auto != synced:
                call("PATCH", f"/data_sources/{source_id[tgt]}", {"properties": {auto: {"name": synced}}})
    log("relations done")

    # rollups & formulas
    for dbn, name, kind, cfg in COMPUTED:
        if kind == "rollup":
            rel, prop, fn = cfg
            body = {"rollup": {"relation_property_name": rel, "rollup_property_name": prop, "function": fn}}
        else:
            body = {"formula": {"expression": cfg}}
        try:
            call("PATCH", f"/data_sources/{source_id[dbn]}", {"properties": {name: body}})
        except Exception as e:
            WARN.append(f"{dbn}.{name}: {e}")
    log("rollups/formulas done")

    # Filtered database views are supported by current Notion API versions.
    create_database_views(dbid, source_id)
    create_module_views(module_anchors, source_id)

    # sample rows: pass 1 without relations, pass 2 relations
    rowid = {}
    for d in B.DBS:
        for r in d["rows"]:
            props = {}
            for c, v in zip(d["cols"], r):
                if c[1] == "relation" or not v: continue
                pv = prop_value(c, v)
                if pv: props[c[0]] = pv
            res = call("POST", "/pages", {"parent": {"data_source_id": source_id[d["name"]]}, "properties": props})
            rowid[(d["name"], r[0])] = res["id"]
    for d in B.DBS:
        for r in d["rows"]:
            props = {}
            for c, v in zip(d["cols"], r):
                if c[1] == "relation" and v:
                    props[c[0]] = {"relation": [{"id": rowid[(c[2][0], x.strip())]} for x in v.split(",")]}
            if props: call("PATCH", f"/pages/{rowid[(d['name'], r[0])]}", {"properties": props})
    log("sample rows done")

    # home, reset, profile, setup
    home_blocks, home_created = None, None
    for path in [B.HOME, B.RESET, B.PROFILE]:
        blocks = md_blocks(B.files[path], path)
        created = append(LINKS[path], blocks)
        if path == B.HOME:
            home_blocks, home_created = blocks, created
    append(LINKS[B.SETUP], md_blocks(setup_md(), B.SETUP))
    create_dashboard_views(LINKS[B.HOME], home_blocks, home_created, source_id)
    log("Done:", url(root))
    for w in WARN: log("WARNING", w)
    return url(root)

def setup_md():
    s = B.SETUP
    conn = {}
    for d in B.DBS:
        for c in d["cols"]:
            if c[1] == "relation":
                conn.setdefault(d["name"], set()).add(c[2][0]); conn.setdefault(c[2][0], set()).add(d["name"])
    return f"""Your databases, relations, rollups, formulas, sample data, core filtered views and home dashboard linked views are built automatically. Use the notes below for optional layouts and buttons.

← [🏠 Home Dashboard]({B.rel_link(s, B.HOME)})

---

## 1. Choose your learner profile

| Profile | Default modules | Databases to keep front and centre |
|---|---|---|
| High School | Subjects, Homework, Timetable, Attendance, Exams | Courses (rename **Subjects**), Assignments (rename **Homework**), Class Timetable, Attendance, Exams |
| University | Courses, Semesters, Assignments, Projects, GPA | Courses, Semesters, Assignments, Projects, Grades (GPA rolls up into Semesters) |
| Self-Learner | Courses, Skills, Roadmaps, Resources, Projects | Courses (Online Courses view), Skills, Learning Roadmaps, Resources, Projects |

Set your choice in [🎯 My Student Profile]({B.rel_link(s, B.PROFILE)}). Move modules you don't use into an “Archive” page, but keep their databases because other modules relate to them.

## 2. How everything connects

| Database | Connects to |
|---|---|
""" + "\n".join(f"| {k} | {', '.join(sorted(conn[k]))} |" for k in
    ["Courses","Tasks","Notes","Exams","Study Sessions","Goals","Resources","Projects","Expenses","Habits"]) + """

Automatic properties: Courses → Assignments Done (%), Study Hours, Next Exam, Average Grade · Semesters → GPA, Total Credits · Goals and Projects → Progress (%) · Exams → Revision Progress, Days Left · Monthly Budget → Total Expenses, Remaining Budget · Tasks → Overdue · Habits → Times Completed.

## 3. Core views created automatically

The builder creates Today, Upcoming, Overdue and Completed task views; Pending Submission assignments; Active and Completed courses and goals; Upcoming and Completed exams; This Week planner and study views; Active habits; Personal and Group Projects; Finished Reading; and This Month expenses. The property reference below documents further view ideas; add those when useful.

Open each database, click **+** next to the view tabs, and add these views:

| Database | Views |
|---|---|
""" + "\n".join(f"| {d['name']} | " + "<br>".join(d["views"]) + " |" for d in B.DBS) + f"""

## 4. Build the dashboards

1. Open [🏠 Home Dashboard]({B.rel_link(s, B.HOME)}); its Today, Deadline Radar and My Progress sections already contain linked views.
2. The Self-Learning, Collaboration and Progress modules also include linked views for Online Course Tracker, Personal Projects, Group Projects, Team Task Manager and Personal Statistics.
3. Turn the Quick Actions into Buttons (`/button` → Add page to…).
4. Optional: change Status columns from Select to Notion's Status type to get grouped To-do / In progress / Complete.
5. Delete the sample rows when you're ready.
"""

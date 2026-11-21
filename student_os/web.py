"""Local browser dashboard backed by SQLite; independent of a Notion account."""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, parse_qs
import datetime as dt
import json
import sqlite3
import uuid
import os

from .schema import DBS, MODULES

ROOT = Path(__file__).resolve().parent
WEB = ROOT / "web"
DB_PATH = Path(os.environ.get("STUDENT_OS_DB", ROOT.parent / "student_os.sqlite3"))
DATABASES = {d["name"]: d for d in DBS}


def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def stamp():
    return dt.datetime.now().isoformat(timespec="seconds")


def clean_data(database, data):
    result = {}
    for name, _kind, _detail in DATABASES[database]["cols"]:
        value = data.get(name, "")
        if isinstance(value, (dict, list)):
            value = json.dumps(value, ensure_ascii=False)
        result[name] = str(value or "").strip()
    return result


def setup():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with connect() as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS records (id TEXT PRIMARY KEY, database_name TEXT NOT NULL, data TEXT NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL)")
        conn.execute("CREATE TABLE IF NOT EXISTS app_meta (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
        seeded = conn.execute("SELECT value FROM app_meta WHERE key='sample_data_seeded'").fetchone()
        if not seeded:
            now = stamp()
            for database in DBS:
                for row in database["rows"]:
                    values = {col[0]: val for col, val in zip(database["cols"], row)}
                    conn.execute("INSERT INTO records VALUES (?,?,?,?,?)", (str(uuid.uuid4()), database["name"], json.dumps(clean_data(database["name"], values), ensure_ascii=False), now, now))
            conn.execute("INSERT INTO app_meta VALUES ('sample_data_seeded','yes')")


def public_record(row):
    return {"id": row["id"], "database": row["database_name"], "data": json.loads(row["data"]), "createdAt": row["created_at"], "updatedAt": row["updated_at"]}


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB), **kwargs)

    def log_message(self, *_args):
        pass

    def send_json(self, value, status=200):
        raw = json.dumps(value, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(raw)

    def read_json(self):
        size = int(self.headers.get("Content-Length", "0"))
        return json.loads(self.rfile.read(size) or b"{}")

    def do_GET(self):
        path = urlparse(self.path)
        if path.path == "/api/workspace":
            modules = [{"name": name, "description": desc} for name, desc in MODULES]
            dbs = [{"name": d["name"], "module": d["module"], "section": d["section"], "description": d["desc"],
                    "fields": [{"name": n, "type": t, "detail": detail, "target": detail[0] if t == "relation" else None}
                               for n, t, detail in d["cols"]]} for d in DBS]
            return self.send_json({"modules": modules, "databases": dbs})
        if path.path == "/api/records":
            dbname = parse_qs(path.query).get("database", [None])[0]
            if dbname and dbname not in DATABASES:
                return self.send_json({"error": "Unknown database"}, 400)
            with connect() as conn:
                rows = conn.execute("SELECT * FROM records" + (" WHERE database_name=?" if dbname else "") + " ORDER BY updated_at DESC", ([dbname] if dbname else [])).fetchall()
            return self.send_json([public_record(r) for r in rows])
        if path.path == "/api/summary":
            with connect() as conn:
                rows = conn.execute("SELECT database_name,data FROM records").fetchall()
            all_rows = [{"database": r["database_name"], **json.loads(r["data"])} for r in rows]
            today, end = dt.date.today(), dt.date.today() + dt.timedelta(days=7)
            deadlines = []
            for row in all_rows:
                date_key = {"Tasks": "Due Date", "Assignments": "Due Date", "Exams": "Exam Date"}.get(row["database"])
                if not date_key:
                    continue
                try:
                    due = dt.date.fromisoformat(str(row.get(date_key, ""))[:10])
                except ValueError:
                    continue
                status = str(row.get("Status", "")).lower()
                if today <= due <= end and status not in {"done", "completed", "submitted"}:
                    deadlines.append({"title": row.get("Task Name") or row.get("Assignment Name") or row.get("Exam Name") or "Deadline", "date": due.isoformat(), "database": row["database"], "priority": row.get("Priority", "")})
            counts = {d["name"]: sum(1 for r in all_rows if r["database"] == d["name"]) for d in DBS}
            return self.send_json({"counts": counts, "total": len(all_rows), "deadlines": sorted(deadlines, key=lambda d: d["date"])[:10], "today": today.isoformat()})
        return super().do_GET()

    def do_POST(self):
        if urlparse(self.path).path != "/api/records":
            return self.send_json({"error": "Not found"}, 404)
        body, database = self.read_json(), None
        database = body.get("database")
        if database not in DATABASES:
            return self.send_json({"error": "Unknown database"}, 400)
        now, rid = stamp(), str(uuid.uuid4())
        data = clean_data(database, body.get("data", {}))
        with connect() as conn:
            conn.execute("INSERT INTO records VALUES (?,?,?,?,?)", (rid, database, json.dumps(data, ensure_ascii=False), now, now))
        return self.send_json({"id": rid, "database": database, "data": data, "createdAt": now, "updatedAt": now}, 201)

    def do_PUT(self):
        rid = urlparse(self.path).path.rsplit("/", 1)[-1]
        with connect() as conn:
            row = conn.execute("SELECT database_name FROM records WHERE id=?", (rid,)).fetchone()
            if not row:
                return self.send_json({"error": "Record not found"}, 404)
            database = row["database_name"]
            data = clean_data(database, self.read_json().get("data", {}))
            now = stamp()
            conn.execute("UPDATE records SET data=?,updated_at=? WHERE id=?", (json.dumps(data, ensure_ascii=False), now, rid))
        return self.send_json({"id": rid, "database": database, "data": data, "updatedAt": now})

    def do_DELETE(self):
        rid = urlparse(self.path).path.rsplit("/", 1)[-1]
        with connect() as conn:
            result = conn.execute("DELETE FROM records WHERE id=?", (rid,))
        return self.send_json({"deleted": result.rowcount > 0})


def run(host="127.0.0.1", port=8000):
    setup()
    print(f"Student OS dashboard: http://{host}:{port}")
    print(f"Local database: {DB_PATH}")
    ThreadingHTTPServer((host, port), Handler).serve_forever()

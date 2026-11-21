import argparse
import os
import sys


def _load_dotenv():
    if os.path.exists(".env"):
        for line in open(".env", encoding="utf-8"):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def main(argv=None):
    p = argparse.ArgumentParser(prog="student_os", description="Build the Student OS Notion workspace.")
    sub = p.add_subparsers(dest="cmd", required=True)
    z = sub.add_parser("zip", help="Export a Notion-importable ZIP (Markdown + CSV).")
    z.add_argument("--out", default="dist", help="Output directory (default: dist)")
    n = sub.add_parser("notion", help="Build the workspace in Notion via the API.")
    n.add_argument("page", nargs="?", default=None, help="Parent page URL or ID (or NOTION_PARENT_PAGE in .env)")
    w = sub.add_parser("web", help="Run the local browser dashboard (no Notion account required).")
    w.add_argument("--host", default="127.0.0.1", help="Interface to bind (default: 127.0.0.1)")
    w.add_argument("--port", type=int, default=8000, help="Port to use (default: 8000)")
    sub.add_parser("validate", help="Check sample relations and internal links.")
    a = p.parse_args(argv)

    if a.cmd == "zip":
        from .export_zip import export
        for f in export(a.out):
            print("wrote", f)
    elif a.cmd == "validate":
        from .template import validate
        bad = validate()
        print("OK" if not bad else bad)
        sys.exit(1 if bad else 0)
    elif a.cmd == "web":
        from .web import run
        run(a.host, a.port)
    else:
        _load_dotenv()
        token = os.environ.get("NOTION_TOKEN")
        page = a.page or os.environ.get("NOTION_PARENT_PAGE")
        if not token:
            sys.exit("Set NOTION_TOKEN (environment variable or .env).")
        if not page:
            sys.exit("Pass the parent page URL, or set NOTION_PARENT_PAGE in .env.")
        from .notion import build
        build(page, token)


if __name__ == "__main__":
    main()

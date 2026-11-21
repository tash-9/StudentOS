"""Writes the Notion-importable ZIP (Markdown pages + CSV databases) and the setup guide."""
import os
import zipfile

from . import template as T


def export(out_dir="dist"):
    problems = T.validate()
    if problems:
        raise SystemExit(f"Template validation failed: {problems}")
    os.makedirs(out_dir, exist_ok=True)
    zpath = os.path.join(out_dir, "Student-OS-Notion-Template.zip")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(T.files):
            z.writestr(p, T.files[p])
    gpath = os.path.join(out_dir, "Workspace-Setup-Guide.md")
    with open(gpath, "w", encoding="utf-8") as f:
        f.write(T.files[T.SETUP])
    return zpath, gpath

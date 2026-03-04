from __future__ import annotations

import argparse
import json
from pathlib import Path

import uvicorn

from .config import CONFIG_PATH, load_config, resolve_notes_dir, save_config
from .core import add_paper, ensure_layout, list_notes, search_notes
from .web import create_app


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="paper-digester",
        description="Turn arXiv links/ids or PDFs into structured Markdown notes.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="Create notes folder and index")
    p_init.add_argument("--notes-dir", help="Directory to store notes and INDEX.md")
    p_init.set_defaults(func=cmd_init)

    p_add = sub.add_parser("add", help="Add a paper note from arXiv URL/id or local PDF")
    p_add.add_argument("source", help="arXiv URL, arXiv id, or local PDF path")
    p_add.add_argument("--tags", nargs="*", default=[], help="Optional tags")
    p_add.add_argument("--notes-dir", help="Directory to store notes and INDEX.md")
    p_add.add_argument("--download-pdf", action="store_true", help="Download arXiv PDF to notes_dir/pdfs")
    p_add.set_defaults(func=cmd_add)

    p_list = sub.add_parser("list", help="List notes newest-first")
    p_list.set_defaults(func=cmd_list)

    p_search = sub.add_parser("search", help="Search notes by keyword")
    p_search.add_argument("keyword")
    p_search.set_defaults(func=cmd_search)

    p_web = sub.add_parser("web", help="Start local web dashboard")
    p_web.add_argument("--notes-dir", help="Directory to read notes from")
    p_web.add_argument("--host", default="127.0.0.1")
    p_web.add_argument("--port", type=int, default=8017)
    p_web.set_defaults(func=cmd_web)

    p_config = sub.add_parser("config", help="Config operations")
    config_sub = p_config.add_subparsers(dest="config_cmd", required=True)
    p_cfg_show = config_sub.add_parser("show", help="Show current config")
    p_cfg_show.set_defaults(func=cmd_config_show)

    p_cfg_set = config_sub.add_parser("set", help="Set config value")
    p_cfg_set.add_argument("key", choices=["notes_dir"])
    p_cfg_set.add_argument("value")
    p_cfg_set.set_defaults(func=cmd_config_set)

    return parser


def cmd_init(args: argparse.Namespace) -> int:
    notes_dir = resolve_notes_dir(args.notes_dir)
    save_config(notes_dir)
    ensure_layout(notes_dir)
    print(f"Initialized {notes_dir} and {notes_dir / 'INDEX.md'}")
    return 0


def cmd_add(args: argparse.Namespace) -> int:
    root = Path.cwd()
    notes_dir = resolve_notes_dir(args.notes_dir)
    if args.notes_dir:
        save_config(notes_dir)
    note_path = add_paper(
        root,
        notes_dir,
        args.source,
        tags=args.tags,
        download_pdf=args.download_pdf,
    )
    print(f"Added note: {note_path}")
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    notes_dir = resolve_notes_dir()
    notes = list_notes(notes_dir)
    if not notes:
        print("No notes yet. Run: paper-digester add <source>")
        return 0
    for n in notes:
        print(n.name)
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    notes_dir = resolve_notes_dir()
    matches = search_notes(notes_dir, args.keyword)
    if not matches:
        print("No matches.")
        return 0
    for m in matches:
        print(m.name)
    return 0


def cmd_web(args: argparse.Namespace) -> int:
    notes_dir = resolve_notes_dir(args.notes_dir)
    app = create_app(notes_dir)
    print(f"Dashboard: http://{args.host}:{args.port}")
    uvicorn.run(app, host=args.host, port=args.port)
    return 0


def cmd_config_show(args: argparse.Namespace) -> int:
    cfg = load_config()
    print(json.dumps(cfg, indent=2))
    print(f"Config path: {CONFIG_PATH}")
    return 0


def cmd_config_set(args: argparse.Namespace) -> int:
    if args.key == "notes_dir":
        save_config(args.value)
    print("Config updated.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)

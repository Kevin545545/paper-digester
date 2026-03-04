from __future__ import annotations

import argparse
from pathlib import Path

from .config import resolve_notes_dir, save_config
from .core import add_paper, ensure_layout, list_notes, search_notes


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
    p_add.set_defaults(func=cmd_add)

    p_list = sub.add_parser("list", help="List notes newest-first")
    p_list.set_defaults(func=cmd_list)

    p_search = sub.add_parser("search", help="Search notes by keyword")
    p_search.add_argument("keyword")
    p_search.set_defaults(func=cmd_search)

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
    note_path = add_paper(root, notes_dir, args.source, tags=args.tags)
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


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)

# paper-digester

> A tiny CLI that turns arXiv links or PDFs into structured Markdown notes + an index, perfect for grad students.

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](#install)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](./LICENSE)

`paper-digester` helps you go from "I should read this paper" to reusable notes in seconds.

## Screenshots

- _CLI demo gif placeholder:_ `docs/demo.gif`
- _Sample note screenshot placeholder:_ `docs/note.png`

## Features

- Add from arXiv URL / arXiv ID / local PDF
- Structured Markdown templates for active reading
- Auto-maintained `notes/INDEX.md` table sorted newest-first
- Full-text keyword search over your notes
- Safe local file handling for PDF inputs

## Install

### Option A: pipx (recommended)

```bash
pipx install .
```

### Option B: pip

```bash
python -m pip install -e .
```

## Quickstart

```bash
paper-digester init
paper-digester add https://arxiv.org/abs/1706.03762 --tags transformers attention
paper-digester search attention
```

You can also add by arXiv ID:

```bash
paper-digester add 2401.12345
```

Or add a local PDF (restricted to safe project paths):

```bash
paper-digester add ./papers/my_paper.pdf --tags class-project
```

## Example Output (note file)

```md
# Attention Is All You Need

- **Authors:** Ashish Vaswani, Noam Shazeer, ...
- **Year:** 2017
- **Source:** arXiv:1706.03762
- **Added-at:** 2026-03-04T19:22:10+00:00
- **Keywords:**
- **Tags:** transformers, attention

## Abstract

The dominant sequence transduction models are based on complex recurrent...

## Key Contributions

- 

## Method Overview

- 

## Strengths/Weaknesses

- Strengths:
- Weaknesses:

## My Questions

- 
```

## CLI Commands

- `paper-digester init [--notes-dir PATH]`
- `paper-digester add <arxiv_url|arxiv_id|pdf_path> [--tags ...] [--notes-dir PATH]`
- `paper-digester list`
- `paper-digester search <keyword>`

## Using Windows Drives with WSL

You can store notes on Windows drives mounted in WSL (for example `F:` as `/mnt/f`).

```bash
paper-digester init --notes-dir /mnt/f/paper-notes
paper-digester add https://arxiv.org/abs/1706.03762 --notes-dir /mnt/f/paper-notes --tags transformers
paper-digester list
```

Config is persisted to:

- `~/.paper-digester/config.json`

Example:

```json
{
  "notes_dir": "/mnt/f/paper-notes"
}
```

Safety: notes directories are only allowed under `/mnt/` or `~/openclaw/`.

## Development

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .[dev]
pytest -q
```

## Roadmap

1. Better PDF metadata extraction (title/authors/year inference)
2. Semantic search with local embeddings
3. BibTeX export + citation key generation
4. Obsidian-compatible backlinks and graph view metadata
5. Optional LLM summaries with user-provided API keys

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for setup, standards, and PR flow.

## Security

Please report vulnerabilities responsibly. See [SECURITY.md](./SECURITY.md).

## License

MIT — see [LICENSE](./LICENSE).

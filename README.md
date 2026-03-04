# paper-digester

> A tiny CLI that turns arXiv links or PDFs into structured Markdown notes + an index, perfect for grad students.

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](#install)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](./LICENSE)

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .[dev]

paper-digester init
paper-digester add https://arxiv.org/abs/1706.03762 --download-pdf --tags transformers
paper-digester list
```

## Directory Structure

All outputs are stored under your configured `<notes_dir>`:

```text
<notes_dir>/
  summary/
    INDEX.md
    <slug>.md
  pdfs/
    <slug>.pdf
  assets/
    <slug>/
      method.png
```

## Features

- Add from arXiv URL / arXiv ID / local PDF
- Auto-fill note sections (OpenAI if `OPENAI_API_KEY` is set, heuristic fallback otherwise)
- Optional PDF download to `<notes_dir>/pdfs/<slug>.pdf`
- Generated method diagram at `<notes_dir>/assets/<slug>/method.png`
- Auto-maintained `summary/INDEX.md` sorted newest-first
- Search across all summaries
- Local web dashboard (`paper-digester web`)
- Web PDF upload (drag/drop + form upload, max 50MB)

## Install

### Option A: pipx

```bash
pipx install .
```

### Option B: editable install

```bash
python -m pip install -e .
```

## CLI Commands

- `paper-digester init [--notes-dir PATH]`
- `paper-digester add <arxiv_url|arxiv_id|pdf_path> [--tags ...] [--notes-dir PATH] [--download-pdf]`
- `paper-digester add-pdf /path/to/file.pdf [--tags ...] [--notes-dir PATH]`
- `paper-digester list`
- `paper-digester search <keyword>`
- `paper-digester web [--notes-dir PATH] [--host 127.0.0.1] [--port 8017]`
- `paper-digester config show`
- `paper-digester config set notes_dir PATH`
- `paper-digester migrate [--notes-dir PATH]`

## Using Windows Drives with WSL

You can store notes on mounted Windows drives:

```bash
paper-digester init --notes-dir /mnt/f/paper-notes
paper-digester add 1706.03762 --notes-dir /mnt/f/paper-notes --download-pdf
```

Allowed notes directory roots:

- `/mnt/`
- `~/openclaw/`

Config file:

- `~/.paper-digester/config.json`

## Web Dashboard + PDF Upload

```bash
paper-digester web
```

Open: <http://127.0.0.1:8017>

Then drag-and-drop (or choose) a PDF in the upload box and click **Upload**.

- Upload limit: **50MB**
- After upload, you’re redirected to the generated note page.

## Example workflow

```bash
paper-digester config set notes_dir /mnt/f/paper-notes
paper-digester add-pdf ~/openclaw/projects/papers/my-paper.pdf --tags reading-group
paper-digester add https://arxiv.org/abs/2401.00001 --download-pdf --tags llm cv
paper-digester search ablation
paper-digester web
```

## Development

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .[dev]
pytest -q
```

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md).

## Security

See [SECURITY.md](./SECURITY.md).

## License

MIT — see [LICENSE](./LICENSE).

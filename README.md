# paper-digester

> A lightweight CLI and dashboard for turning arXiv papers into structured **academic paper reviews** in Markdown.

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](#install)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](./LICENSE)

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .[dev]

paper-digester init
paper-digester add https://arxiv.org/abs/1706.03762 --download-pdf --project-context "My project studies image segmentation under limited training data."
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
```

## Core Features

- arXiv ingestion (`paper-digester add <arxiv_url_or_id>`)
- Optional PDF download (`--download-pdf`)
- Coursework-ready review generation in this format:
  - Paper Reference
  - Goal of the Paper
  - Data
  - Algorithm
  - Statistical Results
  - Your Interpretation
- Optional project-aware interpretation via `--project-context`
- PDF body extraction reads available text and stops at back matter headings such as:
  - References / Bibliography
  - Acknowledgments / Acknowledgements
  - Appendix / Appendices
- OpenAI-powered review generation when `OPENAI_API_KEY` is set
- Deterministic heuristic fallback when no API key is present
- Notes index + list/search utilities
- Local web dashboard for browsing and search

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
- `paper-digester add <arxiv_url|arxiv_id> [--tags ...] [--notes-dir PATH] [--download-pdf] [--project-context "..."]`
- `paper-digester list`
- `paper-digester search <keyword>`
- `paper-digester web [--notes-dir PATH] [--host 127.0.0.1] [--port 8017]`
- `paper-digester config show`
- `paper-digester config set notes_dir PATH`
- `paper-digester migrate [--notes-dir PATH]`

## Web Dashboard

```bash
paper-digester web
```

Open: <http://127.0.0.1:8017>

Dashboard supports:
- review list
- keyword search
- markdown rendering
- PDF link (if downloaded)

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

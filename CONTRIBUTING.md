# Contributing

Thanks for considering a contribution to `paper-digester`.

## Local setup

```bash
git clone <repo-url>
cd paper-digester
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .[dev]
```

## Run checks

```bash
pytest -q
```

## Pull request guidelines

- Keep changes focused and small
- Add/update tests for behavior changes
- Update README or CHANGELOG when relevant
- Use clear commit messages

## Code style

- Prefer readable, testable functions
- Keep dependencies minimal
- Preserve path safety checks for local files

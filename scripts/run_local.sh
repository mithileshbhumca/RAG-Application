#!/usr/bin/env sh
set -eu

python3.12 -m pip install -e '.[dev]' >/dev/null
exec .venv312/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

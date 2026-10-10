test:
    uv run pytest -n 8 --dist loadfile

ty:
    ty check src recipes

ruff:
    ruff check src tests recipes

lint: ruff ty

format:
    ruff format

doclint:
    uv run python doc_src/doclint.py

cov:
    uv run pytest -n8 --dist loadfile --cov --cov-report=html

outdated:
    uv pip list --outdated

lock:
    uv self update
    uv lock -U

sync:
    uv sync

doc: sync doclint
    cd doc_src && python generate_doc.py

code: outdated lock sync lint test cov

all: code doc

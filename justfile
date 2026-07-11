test:
    uv run pytest -n 8 --dist loadfile

ty:
    ty check src recipes

ruff:
    ruff check src tests recipes

lint: ruff ty

doclint:
    uv run python doc_src/doclint.py

cov:
    uv run pytest -n8 --dist loadfile --cov --cov-report=html

lock:
    uv lock -U

sync:
    uv sync

doc: sync doclint
    cd doc_src && python generate_doc.py

code: lock sync lint test cov

all: code doc

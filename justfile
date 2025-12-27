test:
    uv run pytest -n 8 --dist loadfile

lint:
    ruff check src tests
    mypy

cov:
    uv run pytest -n8 --dist loadfile --cov --cov-report=html

lock:
    uv lock -U

sync:
    uv sync

doc: sync
    cd doc_src && python generate_doc.py

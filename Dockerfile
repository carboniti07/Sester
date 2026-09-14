# SESTER demo API — single image, isolated SQLite ledger inside.
# Build:  docker build -t sester-demo .
# Run:    docker run --rm -p 8402:8402 sester-demo
# Demo credentials are generated for THIS container only; do not point real
# money rails at this image — it is the evaluation surface, not production.
FROM python:3.12-slim

WORKDIR /app

# sdist/wheel context: build from the local tree (repo root)
COPY pyproject.toml README.md LICENSE ./
COPY sester ./sester

RUN pip install --no-cache-dir ".[demo]"

# Isolated demo state (override with -e SESTER_DEMO_LEDGER_DB=/data/... + -v)
ENV SESTER_DEMO_LEDGER_DB=/tmp/sester-demo.sqlite3 \
    SESTER_ESCALATION_DB=/tmp/sester-escalation.sqlite3 \
    PYTHONUNBUFFERED=1

EXPOSE 8402

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s \
  CMD python -c "import urllib.request,sys;sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8402/healthz',timeout=4).status==200 else 1)"

CMD ["uvicorn", "sester.demo_api:app", "--host", "0.0.0.0", "--port", "8402"]

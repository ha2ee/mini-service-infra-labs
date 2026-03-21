FROM python:3.12-slim

WORKDIR /app

COPY app/pyproject.toml app/uv.lock app/.python-version ./

RUN pip install uv && uv sync --frozen --no-dev

COPY app/ .

ENV PATH="/app/.venv/bin:$PATH"
ENV LAB_ENV=local

EXPOSE 8000

CMD [".venv/bin/uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

WORKDIR /app

# 依存関係のレイヤーを先に作り、アプリコードの変更時にキャッシュを再利用する
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-editable --no-install-project

COPY apps/ apps/
RUN uv sync --frozen --no-dev --no-editable

EXPOSE 8000

CMD ["uv", "run", "--no-sync", "uvicorn", "apps.main:app", "--host", "0.0.0.0", "--port", "8000"]

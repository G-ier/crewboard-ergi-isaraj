FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

ARG APP_HOME=/app
WORKDIR $APP_HOME
ENV PYTHONPATH=/app

RUN groupadd -r app && useradd -r -g app -d /app -s /usr/sbin/nologin app

COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev --frozen

COPY app ./app
COPY tests ./tests

EXPOSE 8001

CMD ["uv", "run", "python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]

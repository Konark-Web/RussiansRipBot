# Separate build image
FROM python:3.9-slim-bookworm as compile-image
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY requirements.txt .
RUN apt-get update && \
    apt-get -y install --no-install-recommends gcc && \
    rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# Final image
FROM python:3.9-slim-bookworm
COPY --from=compile-image /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
WORKDIR /app
COPY bot /app/bot
COPY alembic.ini /app/alembic.ini
COPY alembic /app/alembic
CMD ["sh", "-c", "alembic upgrade head && python -m bot"]

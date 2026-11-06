FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY pyproject.toml README.md LICENSE ./
COPY src ./src
COPY config ./config
COPY db ./db
RUN pip install --no-cache-dir -e .
RUN useradd --system --uid 10001 zonagris
USER zonagris
WORKDIR /app
ENTRYPOINT ["python", "-m", "zonagris.cli"]

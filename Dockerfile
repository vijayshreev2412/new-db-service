FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p migrations

ENV DD_SERVICE=news-db-service
ENV DD_ENV=prod
ENV DD_VERSION=1.0
ENV DB_PATH=/app/news.db

EXPOSE 5001

CMD ["ddtrace-run", "gunicorn", "--bind", "0.0.0.0:5001", "--workers", "2", "app:app"]

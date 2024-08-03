# Dockerfile
FROM python:3.8-slim

WORKDIR /news-sentiment-analysis

RUN apt-get update && apt-get install -y cron

COPY . .

RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev

COPY cronjob /etc/cron.d/scrape-cron

RUN chmod 0644 /etc/cron.d/scrape-cron
RUN crontab /etc/cron.d/scrape-cron

RUN mkdir -p /var/log/news-scraper
RUN touch /var/log/news-scraper/cron.log

CMD cron && tail -f /var/log/news-scraper/cron.log

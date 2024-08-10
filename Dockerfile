# Dockerfile
FROM python:3.8-slim

WORKDIR /news-scraper

# Install cron
RUN apt-get update && apt-get install -y cron

COPY . .

# Install dependencies
RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev

# Add the cron job
COPY cronjob /etc/cron.d/scrape-cron

# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/scrape-cron

# Apply cron job
RUN crontab /etc/cron.d/scrape-cron

# Changing timezone of docker to local time
RUN ln -sf /usr/share/zoneinfo/Asia/Kathmandu /etc/localtime

# Create the log file to be able to run tail
RUN mkdir -p /var/log/news-scraper
RUN touch /var/log/news-scraper/cron.log

# Run the command on container startup
CMD cron && tail -F /var/log/news-scraper/cron.log

FROM python:3.8-slim-buster

WORKDIR /app

RUN pip install requests beautifulsoup4

COPY . /app

CMD ["python", "-m", "scraper_tool"]
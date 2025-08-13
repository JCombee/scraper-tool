FROM python:3.8-slim-buster

WORKDIR /app

RUN pip install requests bs4

COPY . /app

RUN chmod +x scraper_tool.py

CMD ["python", "-m", "scraper_tool"]
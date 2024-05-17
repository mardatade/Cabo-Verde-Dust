FROM python:3.11-slim

ENV PYTHONUNBUFFERED True

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY ./app.py /app/app.py

ENTRYPOINT [ "python", "/app/app.py"]
FROM python:3.11-slim

ENV PYTHONUNBUFFERED True

ENV APP_HOME /app
WORKDIR $APP_HOME

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Run the web service on container startup. 
COPY app.py ./
CMD panel serve app.py --address 0.0.0.0 --port 8080 --allow-websocket-origin="*"
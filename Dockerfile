FROM python:alpine3.7

ENV FLASK_APP=app.py

COPY requirements.txt /
WORKDIR /
RUN pip install -r ./requirements.txt --no-cache-dir
COPY app/ /app/
WORKDIR /app

EXPOSE 5000

CMD flask db upgrade && flask run -h 0.0.0.0 -p 5000

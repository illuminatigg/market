FROM python:3.10
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
WORKDIR /opt/market
RUN apt-get update
RUN apt-get install -y python3-pip python3-dev libpq-dev postgresql postgresql-contrib gcc python3-dev musl-dev
RUN pip3 install --upgrade pip && pip3 install gunicorn
RUN apt-get -y install nano
ADD . .
RUN pip install -r requirements.txt
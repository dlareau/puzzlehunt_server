FROM python:3

ENV PYTHONUNBUFFERED 1

RUN mkdir /code
WORKDIR /code

COPY requirements.txt /code/

RUN pip install -r requirements.txt

COPY . /code/

# RUN apt-get install libmariadbclient-dev python3-mysqldb imagemagick unzip

RUN python3 manage.py migrate --noinput

EXPOSE 8000
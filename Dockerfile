FROM python:3.9

ENV PYTHONUNBUFFERED 1
ENV DJANGO_ENABLE_DEBUG False
ENV DJANGO_USE_SHIBBOLETH False
ENV DJANGO_SETTINGS_MODULE puzzlehunt_server.settings.env_settings

RUN mkdir /code
WORKDIR /code

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["gunicorn", "--workers=5", "--bind=0.0.0.0:8000", "puzzlehunt_server.wsgi:application"]

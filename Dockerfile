FROM python:3.5-onbuild

RUN python manage.py collectstatic --noinput

CMD ["uwsgi","--http", ":8000", "--wsgi-file", "dc/wsgi.py"]
FROM jsondash_base:latest
MAINTAINER Chris Tabor "dxdstudio@gmail.com"

WORKDIR /app/example_app

EXPOSE 8080
ENTRYPOINT ["gunicorn", "--bind", "0.0.0.0:8080", "app_wsgi:app"]

FROM jsondash_base:latest
MAINTAINER Chris Tabor "dxdstudio@gmail.com"

WORKDIR /app/example_app

RUN pip install flask-cors

EXPOSE 5004
ENTRYPOINT ["gunicorn", "--bind", "0.0.0.0:5004", "endpoints_wsgi:app"]

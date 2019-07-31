# bin/bash

# Installation details.
FROM python:3.7
RUN mkdir -p /opt/services/ancile/src
WORKDIR /opt/services/ancile/src
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . /opt/services/ancile/src
EXPOSE 8000
CMD ["gunicorn", "--bind", ":8000", "-w", "4", "--pid", ".pidfile", "ancile.web.ancile_web.wsgi:application"]

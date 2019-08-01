# bin/bash

# Installation details.
FROM python:3.7
RUN mkdir -p /opt/services/ancile/
WORKDIR /opt/services/ancile/
COPY . /opt/services/ancile/
RUN pip install -r requirements.txt
EXPOSE 8000
RUN rm -rf ancile/web/static
RUN python manage.py collectstatic --no-input
RUN chmod +x ./scripts/entrypoint.sh
ENTRYPOINT ./scripts/entrypoint.sh

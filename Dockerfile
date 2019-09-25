# bin/bash

# Installation details.
FROM python:3.7
RUN apt-get update || : && apt-get install nodejs npm -y && npm install npm@latest -g
RUN mkdir -p /opt/services/ancile/
WORKDIR /opt/services/ancile/
COPY .  /opt/services/ancile/
RUN pip install -r requirements.txt
EXPOSE 8000
RUN mkdir logs
RUN [ -f config/config.yaml ] || cp docker/config_example.yaml config/config.yaml
WORKDIR /opt/services/ancile/ancile/web/frontend
RUN npm i && npm run build
WORKDIR /opt/services/ancile/
RUN rm -rf ancile/web/static
RUN python manage.py collectstatic --no-input
RUN chmod +x ./docker/entrypoint.sh
ENTRYPOINT ./docker/entrypoint.sh

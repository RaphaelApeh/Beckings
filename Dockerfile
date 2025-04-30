
FROM python:3.12-slim-bookworm

RUN mkdir -p /apps

WORKDIR /apps

COPY .src/ apps/

RUN python -m venv opt/venv

RUN srouce opt/venv/bin/activate

COPY requirements.txt opt/requirements.txt

RUN pip install -r opt/requirements.txt

COPY .scripts/run.sh /opt/.scripts/run.sh

# Django

ARG DJANGO_SECRET_KEY="django_secret_key"
ARG DJANGO_DEBUG=0

ENV DJANGO_DEBUG ${DJANGO_DEBUG}

ENV DJANGO_SECRET_KEY ${DJANGO_SECRET_KEY}

# Running the application

RUN chmod +x /opt/.scripts/run.sh

CMD /opt/scripts/run.sh

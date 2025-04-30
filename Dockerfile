
FROM python:3.12-slim-bullseye

# Create a virtual environment
RUN python -m venv /opt/venv

# Set the virtual environment as the current location
ENV PATH=/opt/venv/bin:$PATH

# Upgrade pip
RUN pip install --upgrade pip

# Set Python-related environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# ubuntu linux os deps
# Install os dependencies for our mini vm
RUN apt-get update && apt-get install -y \
    # for postgres
    libpq-dev \
    # for Pillow
    libjpeg-dev \
    # for CairoSVG
    libcairo2 \
    # other
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Create the mini vm's code directory
RUN mkdir -p /app

# Set the working directory to that same code directory
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt /tmp/requirements.txt

# copy the project code into the container's working directory
COPY ./src /app

# Install the Python project requirements
RUN pip install -r /tmp/requirements.txt

ARG DJANGO_DEBUG=0
ARG DJANGO_SECRET_KEY=django_secret_key

ENV DJANGO_DEBUG=${DJANGO_DEBUG}
ENV DJANGO_SECRET_KEY=${DJANGO_DEBUG}

RUN mkdir -p app/static

# add our static files to container itself on build
RUN python manage.py collectstatic --noinput

COPY ./.scripts/run.sh /opt/run.sh

RUN chmod +x /opt/run.sh

# Clean up apt cache to reduce image size
RUN apt-get remove --purge -y \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

CMD ["/opt/run.sh"]

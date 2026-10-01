FROM ubuntu:24.04

# NOTE: This is an example Dockerfile for getting Indigo running in a simple way.
#       In production, you will probably want to use this as a template and make
#       your own changes.
#
#       For example, you probably want to use gunicorn to host the Django app,
#       rather than the built-in Django server.

ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Install some necessary dependencies.
RUN apt-get update && apt-get install -y wget git \
  # python
  python3 python3-pip libpq-dev python-is-python3 \
  # pdftotext and ps2pdf
  poppler-utils ghostscript \
  # for fop
  default-jre

# Download and install FOP
RUN wget -q -O fop.tgz 'http://www.apache.org/dyn/closer.cgi?filename=/xmlgraphics/fop/binaries/fop-2.4-bin.tar.gz&action=download' && \
    tar zxf fop.tgz && \
    rm -f fop.tgz && \
    mv fop-2.4 /usr/local/share

ENV PATH=/usr/local/share/fop-2.4/fop:$PATH

# NodeJS 24.x
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    gnupg \
    && curl -fsSL https://deb.nodesource.com/setup_24.x | bash - \
    && apt-get install -y nodejs

# install sass for compiling assets before deploying
RUN npm i -g sass

WORKDIR /app

# install runtime node dependencies
# copying this in first means Docker can cache this operation
COPY package*.json /app/
RUN npm ci --no-audit --ignore-scripts --omit=dev

# Ubuntu 24.04 marks the system Python as externally managed; this image is the only consumer,
# so install into it directly. Its bundled pip (24.0) is new enough.
ENV PIP_BREAK_SYSTEM_PACKAGES=1

# These are production-only dependencies
RUN pip install psycopg==3.2.12 gunicorn==23.0.0

# Copy the code
COPY . /app

# Install python requirements
RUN pip install -e .

# Compile static assets.
RUN python manage.py compilescss
# Note that we ignore 'docs' directories because some components have badly formed docs CSS.
RUN python manage.py collectstatic --noinput -i docs -i \*.scss 2>&1

# Runtime configuration shared by every deployment; per-environment values come from the
# environment at deploy time. Set after the asset build, which runs on Indigo's default settings.
# The AWS_* checksum flags stop boto3 sending checksum headers that GCS's S3-compatible API rejects.
ENV DJANGO_SETTINGS_MODULE=jurisphere_indigo.settings \
    DJANGO_DEBUG=false \
    AWS_REQUEST_CHECKSUM_CALCULATION=when_required \
    AWS_RESPONSE_CHECKSUM_VALIDATION=when_required

# Cloud Run sets $PORT. Document parsing can run for minutes, hence the long worker timeout.
CMD gunicorn indigo.wsgi --bind 0.0.0.0:${PORT:-8000} --timeout 300 --workers 2

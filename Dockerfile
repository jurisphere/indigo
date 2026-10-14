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

# Infisical CLI: jurisphere_indigo/entrypoint.sh pulls secrets with it at container start.
ARG INFISICAL_CLI_VERSION=0.43.119
ARG INFISICAL_CLI_SHA256=a83e68ebb980d90fd67a177e906dfd91408756e84799d0e81fe03ed35b9f1f9a
RUN curl -fsSL -o /tmp/infisical.deb \
      "https://github.com/Infisical/cli/releases/download/v${INFISICAL_CLI_VERSION}/infisical_${INFISICAL_CLI_VERSION}_linux_amd64.deb" \
    && echo "${INFISICAL_CLI_SHA256}  /tmp/infisical.deb" | sha256sum -c - \
    && dpkg -i /tmp/infisical.deb \
    && rm /tmp/infisical.deb

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
# These two must be real env vars (not settings in jurisphere_indigo/settings.py): DEBUG drives
# several if-DEBUG branches in indigo/settings.py at import time (storage backend, secure cookies,
# asset pipelining, Sentry logging), so it has to be correct before that module is even imported.
ENV DJANGO_SETTINGS_MODULE=jurisphere_indigo.settings \
    DJANGO_DEBUG=false

# Every command (the web server, and manage.py in the Cloud Run job) runs with the secrets from
# Infisical in its environment. Cloud Run jobs override CMD with `args` only, keeping the entrypoint.
ENTRYPOINT ["/app/jurisphere_indigo/entrypoint.sh"]

# Cloud Run sets $PORT. Document parsing can run for minutes, hence the long worker timeout.
CMD gunicorn indigo.wsgi --bind 0.0.0.0:${PORT:-8000} --timeout 300 --workers 2

#!/bin/sh
# Runs the container command with this deployment's secrets from Infisical in its environment.
# Authenticates as the Cloud Run service account (GCP ID token from the metadata server) through
# the machine identity INFISICAL_MACHINE_IDENTITY_ID, then reads INFISICAL_PROJECT_ID /
# INFISICAL_ENVIRONMENT at INFISICAL_SECRET_PATH.
set -eu

: "${INFISICAL_MACHINE_IDENTITY_ID:?INFISICAL_MACHINE_IDENTITY_ID is required}"
: "${INFISICAL_PROJECT_ID:?INFISICAL_PROJECT_ID is required}"
: "${INFISICAL_ENVIRONMENT:?INFISICAL_ENVIRONMENT is required}"
: "${INFISICAL_SECRET_PATH:?INFISICAL_SECRET_PATH is required}"

INFISICAL_TOKEN=$(infisical login --method=gcp-id-token \
  --machine-identity-id="$INFISICAL_MACHINE_IDENTITY_ID" --silent --plain)
export INFISICAL_TOKEN

exec infisical run --projectId="$INFISICAL_PROJECT_ID" --env="$INFISICAL_ENVIRONMENT" --path="$INFISICAL_SECRET_PATH" \
  --silent -- "$@"

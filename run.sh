#!/bin/bash

set +ex

CLEAR='\033[0m'
RED='\033[0;31m'

function usage() {
  if [ -n "$1" ]; then
    echo -e "${RED} 👉 $1${CLEAR}\n";
  fi
  echo "Usage: $0 [-fr rebuild]"
  echo "  -fr, --rebuild             Build docker images (Optional argument)(Default Value: false)"
  echo ""
  echo "Example: $0 --rebuild true"
  exit 1
}

# parse params
while [[ "$#" -gt 0 ]]; do
  case $1 in
    -fr|--rebuild) FORCE_BUILD="$2"; shift; shift;;
    *) usage "Unknown parameter passed: $1"; shift; shift;;
  esac
done

# verify params
if [ -z "$FORCE_BUILD" ]; then FORCE_BUILD=false; fi;

export PROJECT_ROOT="${PWD}"

# Read the APP_ENV variable from .env.secrets
if [ -f "$PROJECT_ROOT/.env.secrets" ]; then
  read -r env_line < "$PROJECT_ROOT/.env.secrets"
  APP_ENV=${env_line#*=}
  export APP_ENV
  echo "Found '$env_line' in $PROJECT_ROOT/.env.secrets"
else
  echo "Error: .env.secrets file not found."
  exit 1
fi

if "$FORCE_BUILD"; then
  echo "Recreating and running docker images of veylan backend..."
  docker compose --env-file "${APP_ENV}.env" up -d --build --force-recreate
else
  echo "Running docker images of veylan backend..."
  docker compose --env-file "${APP_ENV}.env" up -d
fi

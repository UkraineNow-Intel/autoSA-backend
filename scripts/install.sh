#!/usr/bin/env bash
set -ex

POSTGRES_VERSION="${POSTGRES_VERSION:-13.4}"

# install geospatial libraries
case $(uname | tr '[:upper:]' '[:lower:]') in
  linux*)
    sudo apt-get install postgresql-"POSTGRES_VERSION", postgresql-"POSTGRES_VERSION"-postgis, postgresql-server-dev-"POSTGRES_VERSION", python-psycopg2
    sudo apt-get install binutils libproj-dev gdal-bin
    ;;
  darwin*)
    brew install postgresql
    brew install postgis
    brew install gdal
    brew install libgeoip
    ;;
  msys*)
    echo "Don't know how to install on '$uname'!"
    exit 1
    ;;
  *)
    echo "Don't know how to install on '$uname'!"
    exit 1
    ;;
esac

# install project requirements
pip install -r requirements.txt -r requirements-dev.txt -U --upgrade-strategy only-if-needed

# run migrations
python manage.py migrate

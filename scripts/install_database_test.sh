#!/usr/bin/env bash
set -x

# TODO: This is a code snippet from install_database.sh. Ideally, can be deduplicated
# this is for unit tests testing
psql -U autosa -c "CREATE DATABASE test_autosa;"
psql -U autosa -c "grant all privileges on database test_autosa to autosa;"
psql -U autosa -d test_autosa -c "create extension postgis;"

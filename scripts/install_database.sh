#!/usr/bin/env bash
set -x

psql -U postgres -c "CREATE DATABASE autosa;"
psql -U postgres -c "CREATE ROLE autosa WITH LOGIN ENCRYPTED PASSWORD 'autosa';"
psql -U postgres -c "alter user autosa with encrypted password 'autosa';"
psql -U postgres -c "grant all privileges on database autosa to  autosa;"
psql -U postgres -d autosa -c "create extension postgis;"

# this is for unit tests testing
psql -U postgres -c "CREATE DATABASE test_autosa;"
psql -U postgres -c "grant all privileges on database test_autosa to  autosa;"
psql -U postgres -d test_autosa -c "create extension postgis;"

#!/usr/bin/env bash
set -ex

createdb autosa
createuser autosa
psql -U postgres -c "alter user autosa with encrypted password 'autosa';"
psql -U postgres -c "grant all privileges on database autosa to  autosa;"
psql -U postgres -d autosa -c "create extension postgis;"

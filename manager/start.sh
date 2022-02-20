#!/bin/sh

TEAM_ID=$1
PORT=$2

cd /service/
COMPOSE_PROJECT_NAME=TEAM$TEAM_ID PORT=$PORT TEAM_ID=$TEAM_ID docker-compose up --build -V --force-recreate -d >> /logs/start-$TEAM_ID.log 2>&1

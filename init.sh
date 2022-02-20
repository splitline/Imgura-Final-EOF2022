#!/bin/sh
rm -f /var/run/docker.pid
dockerd &
sleep 5

rm -rf /logs/*
# rm /manager/public/scoreboard.json
python3 scripts/init.py

crond -f &

npm install -g nodemon
npm install express body-parser axios
NODE_ENV=production nodemon --ignore rounds/ --ignore teams/ ./app.js

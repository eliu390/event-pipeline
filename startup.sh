#!/bin/bash
D="/w205/w205-project3"
echo "Starting up containers"
docker-compose up -d mids > /dev/null
sleep 15
echo "Installing pip depedencies"
docker-compose exec mids pip install -r ${D}/app/requirements.txt > /dev/null


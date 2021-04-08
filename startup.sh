#!/bin/bash
D="/w205/w205-project3"

echo "Starting up containers"
docker-compose down
rm -f ../sqllight.db
docker-compose up -d > /dev/null
sleep 60

echo "Installing pip depedencies"
docker-compose exec mids pip install -r ${D}/app/requirements.txt > /dev/null

echo "Starting flask app"
docker-compose exec -d mids env FLASK_APP=${D}/app/game_api.py flask run --host 0.0.0.0 > /dev/null

echo "Creating kafka topic"
docker-compose exec kafka kafka-topics --create --topic events --partitions 1 --replication-factor 1 --if-not-exists --zookeeper zookeeper:32181 > /dev/null
sleep 20

echo "Submitting spark jobs"
EVENT_TYPES=(
    "add_guild"
    "add_player"
    "add_sword"
    "join_guild"
    "purchase_sword"
)
for event_type in "${EVENT_TYPES[@]}"; do
    docker-compose exec -d spark spark-submit "${D}/stream/${event_type}.py"
    sleep 5
done

echo "Running api calls"
API_CALLS=(
    "add_player?name=batman&money=9999999"
    "add_player?name=robin&money=1"
    "add_guild?name=batman_and_robin"
    "add_sword?cost=1"
    "join_guild?player_id=1&guild_id=1&join=1"
    "join_guild?player_id=2&guild_id=1"
    "purchase_sword?buyer_id=1&sword_id=1"
    "purchase_sword?buyer_id=2&sword_id=1"
    "join_guild?player_id=2&guild_id=1&join=0"
)
for api_call in "${API_CALLS[@]}"; do
    docker-compose exec mids curl "http://localhost:5000/${api_call}"
done

#docker-compose exec mids kafkacat -C -b kafka:29092 -t events -o beginning
for event_type in "${EVENT_TYPES[@]}"; do
    docker-compose exec cloudera hadoop fs -ls "/tmp/${event_type}"
done
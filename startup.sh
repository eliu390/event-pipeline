#!/bin/bash
D="/w205/w205-project3"

echo "Stopping currently running containers..."
docker-compose down
rm -f ../sqllight.db
echo "Starting up containers..."
docker-compose up -d > /dev/null
sleep 60

echo "Installing pip dependencies..."
docker-compose exec mids pip install -r ${D}/app/requirements.txt > /dev/null
echo "Starting Flask app..."
docker-compose exec -d mids env FLASK_APP=${D}/app/game_api.py flask run --host 0.0.0.0 > /dev/null

echo "Creating Kafka topic..."
docker-compose exec kafka kafka-topics --create --topic events --partitions 1 --replication-factor 1 --if-not-exists --zookeeper zookeeper:32181 > /dev/null
sleep 20


echo "Running initial API calls..."
API_CALLS=(
    "add_player?name=Batman&money=9999999"
    "add_player?name=Robin&money=1"
    "add_guild?name=Batman_and_Robin"
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

echo "Submitting Spark jobs..."
EVENT_TYPES=(
    "add_guild"
    "add_player"
    "add_sword"
    "join_guild"
    "purchase_sword"
)
for event_type in "${EVENT_TYPES[@]}"; do
    docker-compose exec -d spark spark-submit "${D}/stream/${event_type}.py"
    sleep 20
done

echo "Generating random events..."
docker-compose exec mids python ${D}/app/events.py > /dev/null

sleep 20
echo "Creating Hive tables..." #hard-coded, since changing the table names for querying purposes.
docker-compose exec cloudera hive -e "create external table if not exists default.swords (event_body string) stored as parquet location '/tmp/add_sword'  tblproperties ('parquet.compress'='SNAPPY');"
sleep 5
docker-compose exec cloudera hive -e "create external table if not exists default.guilds (event_body string) stored as parquet location '/tmp/add_guild'  tblproperties ('parquet.compress"="SNAPPY');"
sleep 5
docker-compose exec cloudera hive -e "create external table if not exists default.players (event_body string) stored as parquet location '/tmp/add_player'  tblproperties ('parquet.compress"="SNAPPY');"
sleep 5
docker-compose exec cloudera hive -e "create external table if not exists default.guild_membership (event_body string) stored as parquet location '/tmp/join_guild'  tblproperties ('parquet.compress"="SNAPPY');"
sleep 5
docker-compose exec cloudera hive -e "create external table if not exists default.sword_transactions (event_body string) stored as parquet location '/tmp/purchase_sword'  tblproperties ('parquet.compress"="SNAPPY');"

echo "Ready to open Kafka observer and query Hive tables."
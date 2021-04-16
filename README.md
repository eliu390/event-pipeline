# W205 - Project 3

## Primary files:
- `startup.sh`: Shell script that sets up data pipeline and exposes hive tables for querying.
- `docker-compose.yml`: contains the docker container information to set up the data pipline.
- `app` directory: contains the .py and requirement files responsible for setting up the Sqllite tables, Flask game API, and generation of random events.
- `stream` directory: contains the .py files for creating the streaming pipeline.


## Directions:
1. Execute `startup.sh` to set up data pipeline. Wait for pipeline components to load and prompt indicating readiness for next steps.


```
./startup.sh
```
2. Open a Kafka queue observer (in a new terminal).


```
docker-compose exec mids kafkacat -C -b kafka:29092 -t events -o beginning
```
3. If you want, create more random events (in a new terminal).


```
docker-compose exec mids python /w205/w205-project3/app/events.py
```
4. Open Presto (in a new terminal) to query Hive tables (see the [Analytics Report](analytics_report.ipynb) for example queries).


```
docker-compose exec presto presto --server presto:8080 --catalog hive --schema default
```
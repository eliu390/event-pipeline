# w205-project3

## Primary files:
- "startup.sh": Shell script that sets up data pipeline and exposes hive tables for querying.
- "docker-compose.yml"
- 'app' directory: contains the .py and requirements files responsible for setting up the base tables and flask game API, and generation of random events stream.
- 'stream' directory: contains the .py files for creating the streaming data pipeline.



## Directions:
1. Execute "startup.sh" to set up data pipeline. Wait for pipeline components to load and prompt indicating readiness for next steps.
2. Open a kafka queue observer (in a new terminal).
3. Create events (in a new terminal):
    - manual event creation: run an API call from the terminal, tbd
    - automated event creation: run the random event generator, tbd
4. Open Presto (in a new terminal) to query hive tables for data analysis. See below for sample queries.



## Sample Preso Queries to answer simple business questions:
docker-compose exec presto presto --server presto:8080 --catalog hive --schema default

### Who are my players?
SELECT
    distinct regexp_extract(event_body,'(?<=name\": \")(.*?)(?="}})') as distinct_players
FROM
    players;


### How many guilds are there?
SELECT
    count(distinct regexp_extract(event_body,'(?<=name\": \")(.*?)(?="}})') ) as number_of_guilds
FROM
    guilds;


### Which sword is exhanged the most?
TBD


### Which guild has the best retention?
TBD
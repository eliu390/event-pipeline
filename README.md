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
    - manual event creation: run an API call from the terminal, e.g. docker-compose exec mids curl "http://localhost:5000/add_sword?cost=1"
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
SELECT
    regexp_extract(event_body,'(?<=sword_id\": )(.*?)(?=, \"trans)') as sword_id, 
    count( regexp_extract(event_body,'(?<=sword_id\": )(.*?)(?=, \"trans)') ) as count_of_transactions
FROM
    sword_transactions
GROUP BY
    regexp_extract(event_body,'(?<=sword_id\": )(.*?)(?=, \"trans)')
ORDER BY 
    count( regexp_extract(event_body,'(?<=sword_id\": )(.*?)(?=, \"trans)') ) DESC;


### Which guild has the longest membership?
SELECT c.guild_id, c.player_id, sum(duration) as membership_length
FROM (
    SELECT b.guild_id, b.player_id,
        CASE
            WHEN b.action = 'true' THEN date_diff('minute', b.timestamp, current_timestamp)
            WHEN b.action = 'false' THEN -date_diff('minute', b.timestamp, current_timestamp)
            END as duration
    FROM(
        SELECT *
        FROM (
            SELECT * , rank() over (
                PARTITION BY a.guild_id, a.player_id
                ORDER BY a.timestamp DESC) as rank
            FROM (
                SELECT
                    regexp_extract(event_body,'(?<=guild_id\": )(.*?)(?=}})') as guild_id,
                    regexp_extract(event_body,'(?<=player_id\": )(.*?)(?=, \"timestamp)') as player_id, 
                    regexp_extract(event_body,'(?<=join\": )(.*?)(?=, \"player)') as action,
                    date_add('year', 100, date_parse(regexp_extract(event_body,'(?<=timestamp\": \")(.*?)(?=\", \"guild)'), '%m/%d/%Y %T')) as timestamp
                FROM
                    guild_membership) a )
        WHERE rank = 1 OR rank = 2 ) b ) c
GROUP BY
    c.guild_id, c.player_id
ORDER BY 
    sum(duration) DESC;

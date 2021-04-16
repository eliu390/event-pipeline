# w205-project3

## Primary files:
- "startup.sh": Shell script that sets up data pipeline and exposes hive tables for querying.
- "docker-compose.yml": contains the docker container information to set up the data pipline.
- 'app' directory: contains the .py and requirements files responsible for setting up the base tables and flask game API, and generation of random events stream.
- 'stream' directory: contains the .py files for creating the streaming data pipeline.


## Directions:
1. Execute "startup.sh" to set up data pipeline. Wait for pipeline components to load and prompt indicating readiness for next steps.
2. Open a kafka queue observer (in a new terminal).
3. Create events (in a new terminal).
4. Open Presto (in a new terminal) to query hive tables for data analysis.
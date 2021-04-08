#!/usr/bin/env python
import json
from pyspark.sql.functions import udf
from pyspark.sql.types import IntegerType, StringType, StructType, StructField

from template import main


EVENT_TYPE = "add_sword"
EVENT_BODY_SCHEMA = StructType([
    StructField("timestamp", StringType(), False),
    StructField("sword_id", IntegerType(), False),
    StructField("cost", IntegerType(), False),
])

@udf('boolean')
def event_filter(event_as_json):
    """udf for filtering events
    """
    event = json.loads(event_as_json)
    if event['event_type'] == EVENT_TYPE:
        return True
    return False

if __name__ == "__main__":
    main(EVENT_BODY_SCHEMA, EVENT_TYPE, event_filter)

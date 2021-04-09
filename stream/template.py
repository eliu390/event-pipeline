#!/usr/bin/env python
"""Extract events from kafka and write them to hdfs
"""
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json
from pyspark.sql.types import StructType, StructField, StringType

from pyspark.sql.types import IntegerType

def main(event_body_schema, event_type, event_filter):
    """main
    """
    spark = SparkSession \
        .builder \
        .appName("{}_job".format(event_type)) \
        .getOrCreate()

    raw_events = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "kafka:29092") \
        .option("subscribe", "events") \
        .load()

    schema = StructType([
        StructField("timestamp", StringType(), False),
        StructField("event_type", StringType(), False),
        StructField("event_body", event_body_schema, False),
    ])
    filtered_events = raw_events \
        .filter(
            event_filter(raw_events.value.cast('string'))
        ) \
        .select(
            raw_events.value.cast('string').alias('raw_event'),
            raw_events.timestamp.cast('string'),
            from_json(
                raw_events.value.cast('string'),
                schema,
            ).alias('json'),
        ) \
        .select('raw_event', 'timestamp', 'json.*')

    sink = filtered_events \
        .writeStream \
        .format("parquet") \
        .option(
            "checkpointLocation",
            "/tmp/checkpoints_for_{}".format(event_type),
        ) \
        .option("path", "/tmp/{}".format(event_type)) \
        .trigger(processingTime="10 seconds") \
        .start()

    sink.awaitTermination()

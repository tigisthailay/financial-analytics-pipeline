# Directory: spark/spark_stream.py

import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, expr, explode, expr, avg, sum as _sum, max as _max, collect_list
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, LongType, MapType,ArrayType
from dotenv import load_dotenv

load_dotenv()


kafka_topic_name = os.getenv("CURRENCIES_EXCHANGE_RATE_TOPIC")
kafka_bootstrap_server = os.getenv("KAFKA_BOOTSTRAP_SERVER")

postgres_url = os.getenv("POSTGRES_URL")
postgres_properties = {
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
    "driver": "org.postgresql.Driver"
}

spark = SparkSession.builder \
    .appName("KafkaSparkPostgres") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")
spark.sparkContext.setLogLevel("ERROR")

# Define schemas
schema = StructType([
    StructField("source", StringType(), True),
    StructField("timestamp", LongType(), True),
    StructField(
        "rates_by_base",
        MapType(
            StringType(),  # base currency (e.g., "USD", "BITCOIN")
            MapType(
                StringType(),  # target currency (e.g., "EUR")
                DoubleType()   # exchange rate (e.g., 0.86)
            )
        ),
        True
    )
])
# Read from Kafka
df_raw = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", kafka_bootstrap_server) \
    .option("subscribe", kafka_topic_name) \
    .option("startingOffsets", "latest") \
    .load()

# Parse the JSON messages
df_parsed = df_raw.selectExpr("CAST(value AS STRING) as json") \
    .select(from_json(col("json"), schema).alias("data")) \
    .select("data.*")

# Flatten the nested structure
df_flat = df_parsed \
    .select("source", "timestamp", explode("rates_by_base").alias("base_currency", "rate_map")) \
    .select("source", "timestamp", "base_currency", explode("rate_map").alias("target_currency", "rate"))

# # Output to console
# query = df_flat.writeStream \
#     .format("console") \
#     .outputMode("append") \
#     .option("truncate", False) \
#     .start()

# query.awaitTermination()
def write_to_postgres(batch_df, batch_id):
    if batch_df.rdd.isEmpty():#batch_df.isEmpty():
        print("Skipping empty batch", batch_id)
        return
    # print("Writing batch" , batch_id, " to PostgreSQL with ", batch_df.count(), " rows")
    batch_df.write.jdbc(
        url=postgres_url,
        table="rate.exchange_rates",
        mode="append",
        properties=postgres_properties
    )

df_flat.writeStream \
    .foreachBatch(write_to_postgres) \
    .outputMode("append") \
    .start() \
    .awaitTermination()

# df_flat.writeStream \
#     .foreachBatch(lambda batch_df, batch_id: (
#         batch_df.write
#         .jdbc(url=postgres_url,
#               table="exchange_rates",
#               mode="append",
#               properties=postgres_properties)
#     )) \
#     .outputMode("append") \
#     .start() \
#     .awaitTermination()
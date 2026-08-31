"""Shared Spark session. Local mode, plain files on disk -- no cloud services."""
from pyspark.sql import SparkSession

DATA = "/work/data"
OUT = "/work/out"


def build(app_name: str) -> SparkSession:
    return (
        SparkSession.builder.appName(app_name)
        .config("spark.sql.shuffle.partitions", "16")
        .config("spark.driver.memory", "3g")
        .getOrCreate()
    )

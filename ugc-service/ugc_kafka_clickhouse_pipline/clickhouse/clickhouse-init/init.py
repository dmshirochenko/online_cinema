import os
import time
import logging
from glob import glob
from clickhouse_driver import Client

logging.basicConfig(level=logging.INFO)

nodes = ["clickhouse-node1", "clickhouse-node2", "clickhouse-node3", "clickhouse-node4"]

default_password = os.getenv("DEFAULT_USER_PASSWORD")
admin_password = os.getenv("ADMIN_PASSWORD")

user = "default"
password = default_password if default_password else ""

node_sql = {
    "clickhouse-node1": [
        "CREATE DATABASE shard;",
        (
            "CREATE TABLE shard.movies (id Int64, id_user Int64, progress UInt8, event_name String, "
            "event_time DateTime) Engine=ReplicatedMergeTree('/clickhouse/tables/shard1/movies', 'replica_1') "
            "PARTITION BY toYYYYMMDD(event_time) ORDER BY id;"
        ),
        (
            "CREATE TABLE default.movies (id Int64, id_user Int64, progress UInt8, event_name String, "
            "event_time DateTime) ENGINE = Distributed('company_cluster', '', movies, rand());"
        ),
    ],
    "clickhouse-node2": [
        "CREATE DATABASE replica;",
        (
            "CREATE TABLE replica.movies (id Int64, id_user Int64, progress UInt8, event_name String, "
            "event_time DateTime) Engine=ReplicatedMergeTree('/clickhouse/tables/shard1/movies', 'replica_2') "
            "PARTITION BY toYYYYMMDD(event_time) ORDER BY id;"
        ),
    ],
    "clickhouse-node3": [
        "CREATE DATABASE shard;",
        (
            "CREATE TABLE shard.movies (id Int64, id_user Int64, progress UInt8, event_name String, "
            "event_time DateTime) Engine=ReplicatedMergeTree('/clickhouse/tables/shard2/movies', 'replica_1') "
            "PARTITION BY toYYYYMMDD(event_time) ORDER BY id;"
        ),
        (
            "CREATE TABLE default.movies (id Int64, id_user Int64, progress UInt8, event_name String, "
            "event_time DateTime) ENGINE = Distributed('company_cluster', '', movies, rand());"
        ),
    ],
    "clickhouse-node4": [
        "CREATE DATABASE replica;",
        (
            "CREATE TABLE replica.movies (id Int64, id_user Int64, progress UInt8, event_name String, "
            "event_time DateTime) Engine=ReplicatedMergeTree('/clickhouse/tables/shard2/movies', 'replica_2') "
            "PARTITION BY toYYYYMMDD(event_time) ORDER BY id;"
        ),
    ],
}


def main():
    for node in nodes:
        logging.info(f"Waiting for node {node} to start...")
        client = Client(host=node, user=user, password=password)
        while True:
            try:
                client.execute("SELECT 1")
                break
            except Exception:
                time.sleep(1)
        logging.info(f"Node {node} is up.")

        for sql in node_sql[node]:
            try:
                client.execute(sql)
                logging.info(f"Executed successfully on {node}: {sql}")
            except Exception as e:
                logging.error(f"Failed on {node}: {sql}. Error: {str(e)}")


if __name__ == "__main__":
    main()

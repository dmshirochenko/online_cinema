## ETL Kafka -> ClickHouse

### Setup

Setup virtualenv
```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Generate test data in Kafka: `python kafka_datagen.py`

Prepare ClickHouse Cluster. Either run `ugc_sprint/clickhouse/create_table.py` for creating a simple ClickHouse server or follow the instruction in https://github.com/torwards/ugc_sprint_1/blob/main/research_dbms/clickhouse/readme.md to create a distributed replicated setup.

### How to run ETL

```
python main.py
```

The script above will produce the simple ETL procedure that loads existing data from Kafka to ClickHouse cluster.

Sample stdout for successfull ETL process:
```
INFO:kafka.coordinator:Successfully joined group etl with generation 5
INFO:kafka.consumer.subscription_state:Updated partition assignment: [TopicPartition(topic='ugc', partition=0)]
INFO:kafka.coordinator.consumer:Setting newly assigned partitions {TopicPartition(topic='ugc', partition=0)} for group etl
INFO:root:: Pausing for 5 secs...
INFO:root:ClickHouse saved records 0...50...
INFO:root:: Pausing for 5 secs...
INFO:root:ETL process is exhausted: Pausing for 5 secs...
INFO:root:ClickHouse saved records 50...100...
INFO:root:: Pausing for 5 secs...
INFO:root:ETL process is exhausted: Pausing for 5 secs...
```

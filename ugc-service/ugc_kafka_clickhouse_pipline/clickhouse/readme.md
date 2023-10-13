## ClickHouse Cluster Setup Example

Run docker-compose: `docker-compose -f docker-compose.yml up`

Configure shards and replication on each node:

__node 1__
```
CREATE DATABASE shard;
CREATE TABLE shard.movies (id Int64, id_user Int64, progress UInt8, event_name String, event_time DateTime) Engine=ReplicatedMergeTree('/clickhouse/tables/shard1/movies', 'replica_1') PARTITION BY toYYYYMMDD(event_time) ORDER BY id;
CREATE TABLE default.movies (id Int64, id_user Int64, progress UInt8, event_name String, event_time DateTime) ENGINE = Distributed('company_cluster', '', movies, rand());
```

__node 2__
```
CREATE DATABASE replica;
CREATE TABLE replica.movies (id Int64, id_user Int64, progress UInt8, event_name String, event_time DateTime) Engine=ReplicatedMergeTree('/clickhouse/tables/shard1/movies', 'replica_2') PARTITION BY toYYYYMMDD(event_time) ORDER BY id;
```

__node 3__
```
CREATE DATABASE shard;
CREATE TABLE shard.movies (id Int64, id_user Int64, progress UInt8, event_name String, event_time DateTime) Engine=ReplicatedMergeTree('/clickhouse/tables/shard2/movies', 'replica_1') PARTITION BY toYYYYMMDD(event_time) ORDER BY id;
CREATE TABLE default.movies (id Int64, id_user Int64, progress UInt8, event_name String, event_time DateTime) ENGINE = Distributed('company_cluster', '', movies, rand());
```

__node 4__
```
CREATE DATABASE replica;
CREATE TABLE replica.movies (id Int64, id_user Int64, progress UInt8, event_name String, event_time DateTime) Engine=ReplicatedMergeTree('/clickhouse/tables/shard2/movies', 'replica_2') PARTITION BY toYYYYMMDD(event_time) ORDER BY id;
```


Setup python environment

```
pip install -r requirements.txt
```

## Python Usage example

```
python create_table.py
```

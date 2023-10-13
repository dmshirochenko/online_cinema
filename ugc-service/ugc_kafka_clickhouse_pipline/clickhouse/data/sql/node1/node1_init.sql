CREATE DATABASE shard;
CREATE TABLE shard.movies (
    id Int64, 
    id_user Int64, 
    progress UInt8, 
    event_name String, 
    event_time DateTime
) Engine=ReplicatedMergeTree('/clickhouse/tables/shard1/movies', 'replica_1') 
PARTITION BY toYYYYMMDD(event_time) 
ORDER BY id;

CREATE TABLE default.movies (
    id Int64, 
    id_user Int64, 
    progress UInt8, 
    event_name String, 
    event_time DateTime
) ENGINE = Distributed('company_cluster', '', movies, rand());

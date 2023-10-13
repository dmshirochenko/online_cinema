CREATE DATABASE replica;
CREATE TABLE replica.movies (
    id Int64, 
    id_user Int64, 
    progress UInt8, 
    event_name String, 
    event_time DateTime
) Engine=ReplicatedMergeTree('/clickhouse/tables/shard1/movies', 'replica_2') 
PARTITION BY toYYYYMMDD(event_time) 
ORDER BY id;

CREATE DATABASE replica;

CREATE TABLE replica.views (
    id Int64,
    user_id Int64,
    movie_id Int64,
    movie_progress Float64,
    movie_length Int32
) Engine=ReplicatedMergeTree('/clickhouse/tables/shard1/ugc_views', 'replica_2')
ORDER BY id;

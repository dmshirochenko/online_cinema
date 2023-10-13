CREATE DATABASE ugc;

CREATE TABLE ugc.views (
    id Int64,
    user_id Int64,
    movie_id Int64,
    movie_progress Float64,
    movie_length Int32
) Engine=ReplicatedMergeTree('/clickhouse/tables/shard1/ugc_views', 'replica_1')
ORDER BY id;

CREATE DATABASE default;

CREATE TABLE default.views (
    id Int64,
    user_id Int64,
    movie_id Int64,
    movie_progress Float64,
    movie_length Int32
) ENGINE = Distributed('company_cluster', '', ugc_views, rand());

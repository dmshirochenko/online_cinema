from clickhouse_driver import Client

client = Client(host="localhost")

client.execute("SHOW DATABASES")
client.execute("CREATE DATABASE IF NOT EXISTS ugc ON CLUSTER company_cluster")
client.execute(
    """CREATE TABLE ugc.views ON CLUSTER company_cluster (
                   id TEXT, 
                   user_id TEXT,
                   movie_id TEXT,
                   movie_progress FLOAT,
                   movie_length Int32,
                   time_created datetime,
                   ) 
                   Engine=MergeTree() ORDER BY id"""
)

# client.execute('INSERT INTO example.regular_table (id, x) VALUES (1, 10), (2, 20)')
# client.execute('SELECT * FROM example.regular_table')

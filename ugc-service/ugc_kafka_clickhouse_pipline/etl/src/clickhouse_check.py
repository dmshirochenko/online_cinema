from clickhouse_driver import Client

# Connect to ClickHouse
client = Client(host="localhost", port=9000, user="default", password="test")

# Execute a SELECT query
query = "SELECT COUNT(*) FROM ugc.views"
result = client.execute(query)

# Process the query result
for row in result:
    print(row)

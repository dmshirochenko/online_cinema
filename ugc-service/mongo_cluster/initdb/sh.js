// Set up sharded collections

sh.enableSharding("movies")
db.adminCommand({shardCollection: "movies.Bookmarks", key: {user_id: 1}})
db.adminCommand({shardCollection: "movies.Likes", key: {user_id: 1}})
db.adminCommand({shardCollection: "movies.ReviewLikes", key: {user_id: 1}})
db.adminCommand({shardCollection: "movies.Reviews", key: {user_id: 1}})
db.adminCommand({shardCollection: "movies.WatchedMovies", key: {user_id: 1}})


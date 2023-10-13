"""Basic opportunities."""

import uuid
from datetime import datetime
from uuid import UUID


import motor.motor_asyncio
from bson.binary import Binary
from bson.objectid import ObjectId
from pymongo.collection import ReturnDocument
from bson import SON


class RatingManager:
    """Adding reactions to the movies - rating, like & dislike."""

    def __init__(self, mongo_url: str, db_name: str, collection_name: str):
        """Do setup basic variables.

        Args:
            mongo_url (str): url of mongo
            db_name (str): data base name
            collection_name (str): name of collection
        """
        self.client = motor.motor_asyncio.AsyncIOMotorClient(mongo_url)  # pymongo.MongoClient(mongo_url)
        self.collection = self.client[db_name][collection_name]

    async def add_like(self, movie_id: uuid.UUID, user_id: uuid.UUID) -> ObjectId:
        """Do setup basic variables.

        Args:
            movie_id (uuid.UUID): id of movie
            user_id (uuid.UUID): id of user

        Returns:
            id (ObjectId): id of new like
        """
        _movie_id = Binary.from_uuid(movie_id)
        _user_id = Binary.from_uuid(user_id)
        doc = await self.collection.find_one_and_update(
            {"movie_id": _movie_id, "user_id": _user_id},
            {"$set": {"like": datetime.now()}},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )
        return doc["_id"]

    async def add_dislike(self, movie_id: uuid.UUID, user_id: uuid.UUID) -> ObjectId:
        """Do setup basic variables.

        Args:
            movie_id (uuid.UUID): id of movie
            user_id (uuid.UUID): id of user

        Returns:
            id (ObjectId): id of old like
        """
        _movie_id = Binary.from_uuid(movie_id)
        _user_id = Binary.from_uuid(user_id)
        doc = await self.collection.find_one_and_update(
            {"movie_id": _movie_id, "user_id": _user_id},
            {"$set": {"dislike": datetime.now()}},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )
        return doc["_id"]

    async def get_avg_rating(self, movie_id: uuid.UUID) -> float:
        _movie_id = Binary.from_uuid(movie_id)
        cnt = 0
        sum_rating = 0
        movies = await self.collection.find({"movie_id": _movie_id})
        for doc in movies:
            cnt += 1
            if doc.get("rating") is not None:
                sum_rating += doc["rating"]
        return sum_rating / cnt

    async def get_num_likes(self, movie_id: uuid.UUID) -> int:
        _movie_id = Binary.from_uuid(movie_id)
        return await self.collection.count_documents({"like": {"$exists": True}, "movie_id": _movie_id})

    async def get_liked_movies(self, user_id: uuid.UUID):
        """Get all movies liked by a specific user.

        Args:
            user_id (uuid.UUID): The ID of the user.

        Returns:
            list: A list of movie IDs liked by the user.
        """
        _user_id = Binary.from_uuid(user_id)
        cursor = self.collection.find({"user_id": _user_id, "like": {"$exists": True}})
        liked_movies = []
        async for document in cursor:
            movie_id_uuid = uuid.UUID(bytes=document["movie_id"])
            liked_movies.append(str(movie_id_uuid))
        return liked_movies


class BookmarkManager:
    """Adding and removing user bookmarks for the movies."""

    def __init__(self, mongo_url: str, db_name: str, collection_name: str):
        """Do setup basic variables.

        Args:
            mongo_url (str): url of mongo
            db_name (str): data base name
            collection_name (str): name of collection
        """
        self.client = motor.motor_asyncio.AsyncIOMotorClient(mongo_url)  # pymongo.MongoClient(mongo_url)
        self.collection = self.client[db_name][collection_name]

    async def add_bookmark(self, user_id: uuid.UUID, movie_id: uuid.UUID):
        """Do setup basic variables.

        Args:
            movie_id (uuid.UUID): id of movie
            user_id (uuid.UUID): id of user

        Returns:
            id (Mapping[str, Any]): id of new bookmark
        """
        _user_id = Binary.from_uuid(user_id)
        _movie_id = Binary.from_uuid(movie_id)
        doc = await self.collection.find_one_and_update(
            {"user_id": _user_id},
            {"$push": {"bookmarks": _movie_id}},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )
        return doc["_id"]

    async def remove_bookmark(self, user_id: uuid.UUID, movie_id: uuid.UUID):
        """Do setup basic variables.

        Args:
            movie_id (uuid.UUID): id of movie
            user_id (uuid.UUID): id of user

        Returns:
            id (Mapping[str, Any]): id of new bookmark
        """
        _user_id = Binary.from_uuid(user_id)
        _movie_id = Binary.from_uuid(movie_id)

        doc = await self.collection.find_one_and_update(
            {"user_id": _user_id},
            {"$pull": {"bookmarks": _movie_id}},
            return_document=ReturnDocument.AFTER,
        )
        return doc["_id"]


class ReviewManager:
    """Adding reviews for the movies and reactions to them."""

    def __init__(self, mongo_url: str, db_name: str, collection_name: str):
        """Do setup basic variables.

        Args:
            mongo_url (str): url of mongo
            db_name (str): data base name
            collection_name (str): name of collection
        """
        self.client = motor.motor_asyncio.AsyncIOMotorClient(mongo_url)  # pymongo.MongoClient(mongo_url)
        self.collection = self.client[db_name][collection_name]

    async def add_review(
        self,
        movie_id: uuid.UUID,
        user_id: uuid.UUID,
        review_text: str,
        review_rating: int = 0,
    ) -> ObjectId:
        """Do setup basic variables.

        Args:
            movie_id (uuid.UUID): id of movie
            user_id (uuid.UUID): id of user
            review_text (str): text
            review_rating (int): rating

        Returns:
            id (Mapping[str, Any]): id of new review
        """
        _user_id = Binary.from_uuid(user_id)
        _movie_id = Binary.from_uuid(movie_id)

        doc = await self.collection.find_one_and_update(
            {"movie_id": _movie_id, "user_id": _user_id},
            {"$set": {"rating": review_rating, "text": review_text}},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )
        return doc["_id"]

    async def add_like(self, review_id: str, user_id: uuid.UUID) -> None:
        """Do setup basic variables.

        Args:
            review_id (ObjectId): id of review
            user_id (uuid.UUID): id of user

        """

        await self.collection.find_one_and_update(
            {"_id": review_id},
            {"$push": {"likes": user_id}},
        )

    async def add_dislike(self, review_id: str, user_id: uuid.UUID) -> None:
        """Do setup basic variables.

        Args:
            review_id (ObjectId): id of review
            user_id (uuid.UUID): id of user

        """

        await self.collection.find_one_and_update(
            {"_id": review_id},
            {"$push": {"dislikes": user_id}},
        )


class WatchedMoviesManager:
    """Adding and tracking watched movies for a user."""

    def __init__(self, mongo_url: str, db_name: str, collection_name: str):
        """Do setup basic variables.

        Args:
            mongo_url (str): url of mongo
            db_name (str): data base name
            collection_name (str): name of collection
        """
        self.client = motor.motor_asyncio.AsyncIOMotorClient(mongo_url)
        self.collection = self.client[db_name][collection_name]

    async def add_watched_movie(self, user_id: uuid.UUID, movie_id: uuid.UUID):
        """Mark a movie as watched for a user.

        Args:
            movie_id (uuid.UUID): id of movie
            user_id (uuid.UUID): id of user

        Returns:
            id (Mapping[str, Any]): id of new record
        """
        _user_id = Binary.from_uuid(user_id)
        _movie_id = Binary.from_uuid(movie_id)
        doc = await self.collection.find_one_and_update(
            {"user_id": _user_id},
            {"$addToSet": {"watched_movies": _movie_id}},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )
        return doc["_id"]

    async def is_movie_watched(self, user_id: uuid.UUID, movie_id: uuid.UUID):
        """Check if a movie has been watched by a user.

        Args:
            user_id (uuid.UUID): id of user
            movie_id (uuid.UUID): id of movie

        Returns:
            bool: True if movie has been watched by user, False otherwise
        """
        _user_id = Binary.from_uuid(user_id)
        _movie_id = Binary.from_uuid(movie_id)

        doc = await self.collection.find_one({"user_id": _user_id, "watched_movies": {"$in": [_movie_id]}})

        return doc is not None

    async def get_watched_movies_count(self, user_id: uuid.UUID):
        """Get the count of watched movies for a user.

        Args:
            user_id (uuid.UUID): id of user

        Returns:
            int: count of watched movies
        """
        _user_id = Binary.from_uuid(user_id)
        doc = await self.collection.find_one({"user_id": _user_id})
        return len(set(doc.get("watched_movies", []))) if doc else 0

    async def get_most_watched_movies(self, limit: int = 100):
        """Get the most watched movies.

        Args:
            limit (int, optional): Number of movies to return. Defaults to 10.

        Returns:
            List[Dict]: List of most watched movies with watch count
        """
        pipeline = [
            {"$unwind": "$watched_movies"},
            {"$group": {"_id": "$watched_movies", "count": {"$sum": 1}}},
            {"$sort": SON([("count", -1), ("_id", -1)])},
            {"$limit": limit},
        ]
        results = await self.collection.aggregate(pipeline).to_list(None)
        return [{"movie_id": str(UUID(bytes=result["_id"])), "count": result["count"]} for result in results]

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pymongo import MongoClient
from pymongo.collection import Collection

from app.core.config import settings


class ImageRepository:
    def __init__(self, client: Optional[MongoClient] = None) -> None:
        self._client = client or MongoClient(settings.mongodb_uri)
        self._collection: Collection = self._client[settings.mongodb_db][
            settings.mongodb_collection
        ]
        # self._collection.create_index("user_id")
        # self._collection.create_index("content_type")
        # self._collection.create_index("created_at")

    def insert_image(self, doc: Dict[str, Any]) -> str:
        doc = {**doc, "created_at": doc.get("created_at") or datetime.utcnow()}
        result = self._collection.insert_one(doc)
        return str(result.inserted_id)

    def list_images(
        self,
        user_id: Optional[str] = None,
        content_type: Optional[str] = None,
        limit: int = 50,
        skip: int = 0,
    ) -> List[Dict[str, Any]]:
        query: Dict[str, Any] = {}
        if user_id:
            query["user_id"] = user_id
        if content_type:
            query["content_type"] = content_type
        cursor = (
            self._collection.find(query).sort("created_at", -1).skip(skip).limit(limit)
        )
        return [self._serialize(doc) for doc in cursor]

    def get_image_by_key(self, key: str) -> Optional[Dict[str, Any]]:
        doc = self._collection.find_one({"s3_key": key})
        return self._serialize(doc) if doc else None

    def delete_by_key(self, key: str) -> bool:
        result = self._collection.delete_one({"s3_key": key})
        return result.deleted_count > 0

    @staticmethod
    def _serialize(doc: Dict[str, Any]) -> Dict[str, Any]:
        if not doc:
            return {}
        doc = dict(doc)
        if "_id" in doc:
            doc["id"] = str(doc.pop("_id"))
        return doc



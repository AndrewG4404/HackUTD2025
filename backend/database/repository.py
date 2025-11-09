"""
MongoDB repository for evaluations.
CRUD operations for evaluation documents.
"""
from datetime import datetime
from typing import List, Optional

from bson import ObjectId
from database import client as mongo_client  # noqa: F401
from database.connection import get_database
from database.models import Evaluation, Vendor


def create_evaluation(evaluation: Evaluation) -> str:
    """
    Create a new evaluation document in MongoDB.
    Returns the evaluation ID.
    """
    db = get_database()
    collection = db.evaluations
    
    # Convert Pydantic model to dict
    eval_dict = evaluation.model_dump(exclude={"_id"})
    eval_dict["created_at"] = datetime.utcnow()
    
    result = collection.insert_one(eval_dict)
    return str(result.inserted_id)


def get_evaluation(evaluation_id: str) -> Optional[dict]:
    """Get evaluation by ID"""
    db = get_database()
    collection = db.evaluations
    
    try:
        evaluation = collection.find_one({"_id": ObjectId(evaluation_id)})
        if evaluation:
            evaluation["id"] = str(evaluation["_id"])
            del evaluation["_id"]
        return evaluation
    except Exception:
        return None


def update_evaluation(evaluation_id: str, update_data: dict) -> bool:
    """Update evaluation document"""
    db = get_database()
    collection = db.evaluations
    
    try:
        result = collection.update_one(
            {"_id": ObjectId(evaluation_id)},
            {"$set": update_data}
        )
        return result.modified_count > 0
    except Exception:
        return False


def list_evaluations(limit: int = 100, skip: int = 0) -> List[dict]:
    """List all evaluations with pagination"""
    db = get_database()
    collection = db.evaluations
    
    evaluations = collection.find().sort("created_at", -1).skip(skip).limit(limit)
    
    result = []
    for eval in evaluations:
        eval["id"] = str(eval["_id"])
        del eval["_id"]
        result.append(eval)
    
    return result


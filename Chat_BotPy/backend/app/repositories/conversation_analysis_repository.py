"""
ConversationAnalysis Repository
Handles database operations for ConversationAnalysis
"""
from typing import List, Optional
from bson import ObjectId
from pymongo.collection import Collection

from app.models.conversation_analysis import ConversationAnalysis


class ConversationAnalysisRepository:
    """Repository for ConversationAnalysis operations"""

    def __init__(self, collection: Collection):
        self.collection = collection

    def create(self, analysis: ConversationAnalysis) -> ConversationAnalysis:
        """Create a new analysis"""
        data = analysis.to_dict()
        # Remove _id if exists (let MongoDB generate)
        if '_id' in data:
            del data['_id']
        result = self.collection.insert_one(data)
        analysis._id = result.inserted_id
        return analysis

    def find_by_id(self, analysis_id: str) -> Optional[ConversationAnalysis]:
        """Find analysis by ID"""
        try:
            doc = self.collection.find_one({'_id': ObjectId(analysis_id)})
            if doc:
                return ConversationAnalysis.from_dict(doc)
            return None
        except Exception:
            return None

    def find_by_conversation_id(self, conversation_id: str) -> Optional[ConversationAnalysis]:
        """Find analysis by conversation ID"""
        try:
            doc = self.collection.find_one({
                'conversation_id': str(conversation_id)
            })
            if doc:
                return ConversationAnalysis.from_dict(doc)
            return None
        except Exception:
            return None

    def find_by_user_id(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 20
    ) -> List[ConversationAnalysis]:
        """Find analyses by user ID with pagination"""
        cursor = self.collection.find({'user_id': user_id})\
            .sort('created_at', -1)\
            .skip(skip)\
            .limit(limit)
        return [ConversationAnalysis.from_dict(doc) for doc in cursor]

    def update(self, analysis_id: str, analysis: ConversationAnalysis) -> bool:
        """Update an existing analysis"""
        try:
            data = analysis.to_dict()
            # Keep original _id
            data['_id'] = ObjectId(analysis_id)
            result = self.collection.replace_one(
                {'_id': ObjectId(analysis_id)},
                data
            )
            return result.modified_count > 0
        except Exception:
            return False

    def delete(self, analysis_id: str) -> bool:
        """Delete an analysis"""
        try:
            result = self.collection.delete_one({'_id': ObjectId(analysis_id)})
            return result.deleted_count > 0
        except Exception:
            return False







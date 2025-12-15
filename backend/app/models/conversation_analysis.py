"""
ConversationAnalysis model - stores detailed analysis results for a conversation
Separate from Conversation to allow multiple analyses over time
"""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Dict, Any
from bson import ObjectId

from .base import Entity
from .enums import JLPTLevel


@dataclass
class AnalysisScores:
    """Detailed scores for conversation analysis"""
    grammar: float = 0.0
    vocabulary: float = 0.0
    fluency: float = 0.0
    naturalness: float = 0.0

    def to_dict(self) -> dict:
        return {
            'grammar': self.grammar,
            'vocabulary': self.vocabulary,
            'fluency': self.fluency,
            'naturalness': self.naturalness,
        }

    @staticmethod
    def from_dict(data: Optional[dict]) -> AnalysisScores:
        if not data:
            return AnalysisScores()
        return AnalysisScores(
            grammar=float(data.get('grammar', 0.0) or 0.0),
            vocabulary=float(data.get('vocabulary', 0.0) or 0.0),
            fluency=float(data.get('fluency', 0.0) or 0.0),
            naturalness=float(data.get('naturalness', 0.0) or 0.0),
        )


@dataclass
class AnalysisErrors:
    """Error details from conversation analysis"""
    grammar: List[str] = None
    particles: List[str] = None

    def __post_init__(self):
        if self.grammar is None:
            self.grammar = []
        if self.particles is None:
            self.particles = []

    def to_dict(self) -> dict:
        return {
            'grammar': self.grammar,
            'particles': self.particles,
        }

    @staticmethod
    def from_dict(data: Optional[dict]) -> AnalysisErrors:
        if not data:
            return AnalysisErrors()
        return AnalysisErrors(
            grammar=data.get('grammar', []) or [],
            particles=data.get('particles', []) or [],
        )


class ConversationAnalysis(Entity):
    """
    Detailed analysis of a conversation session
    Separate model to allow multiple analyses and historical tracking
    """
    def __init__(
        self,
        conversation_id: str,
        user_id: str,
        jlpt_estimation: Optional[str] = None,
        scores: Optional[AnalysisScores] = None,
        errors: Optional[AnalysisErrors] = None,
        common_mistakes: Optional[List[str]] = None,
        keigo_usage: Optional[Dict[str, Any]] = None,
        created_at: Optional[datetime] = None,
    ):
        super().__init__()
        self.conversation_id = conversation_id
        self.user_id = user_id
        self.jlpt_estimation = jlpt_estimation
        self.scores = scores or AnalysisScores()
        self.errors = errors or AnalysisErrors()
        self.common_mistakes = common_mistakes or []
        self.keigo_usage = keigo_usage or {}
        self.created_at = created_at or datetime.utcnow()

    def to_dict(self) -> dict:
        base = super().to_dict()
        base.update({
            'conversation_id': str(self.conversation_id),
            'user_id': self.user_id,
            'jlpt_estimation': self.jlpt_estimation,
            'scores': self.scores.to_dict(),
            'errors': self.errors.to_dict(),
            'common_mistakes': self.common_mistakes,
            'keigo_usage': self.keigo_usage,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        })
        return base

    @classmethod
    def from_dict(cls, data: dict) -> ConversationAnalysis:
        instance = cls(
            conversation_id=str(data.get('conversation_id', '')),
            user_id=data.get('user_id', ''),
            jlpt_estimation=data.get('jlpt_estimation'),
            scores=AnalysisScores.from_dict(data.get('scores')),
            errors=AnalysisErrors.from_dict(data.get('errors')),
            common_mistakes=data.get('common_mistakes', []) or [],
            keigo_usage=data.get('keigo_usage', {}) or {},
        )
        
        if data.get('_id'):
            instance._id = data['_id'] if isinstance(data['_id'], ObjectId) else ObjectId(str(data['_id']))
        
        if 'created_at' in data:
            created_at_value = data['created_at']
            if isinstance(created_at_value, str):
                try:
                    instance.created_at = datetime.fromisoformat(created_at_value)
                except ValueError:
                    instance.created_at = datetime.utcnow()
            elif isinstance(created_at_value, datetime):
                instance.created_at = created_at_value
        
        return instance






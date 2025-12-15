"""
Enums for conversation modes and JLPT levels
"""
from enum import Enum


class ConversationMode(str, Enum):
    """Conversation modes for AI practice"""
    SPEAKING_PRACTICE = "speaking_practice"
    ROLE_PLAY = "role_play"
    JLPT_EXAM = "jlpt_exam"
    FREE_CONVERSATION = "free_conversation"


class JLPTLevel(str, Enum):
    """JLPT levels"""
    N5 = "N5"
    N4 = "N4"
    N3 = "N3"
    N2 = "N2"
    N1 = "N1"


class UserRole(str, Enum):
    """User roles in the system"""
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"







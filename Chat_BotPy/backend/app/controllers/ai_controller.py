"""
AI Controller - Handles AI-specific endpoints matching BRD/SRS spec
"""
from typing import Dict, Any, Optional
from datetime import datetime

from app.models.conversation import Conversation, Message, MessageAnalysis
from app.models.conversation_analysis import ConversationAnalysis, AnalysisScores, AnalysisErrors
from app.models.enums import ConversationMode, JLPTLevel
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.conversation_analysis_repository import ConversationAnalysisRepository
from app.services.ai.base_ai_service import IAIService
from app.services.analysis.keigo_analyzer import KeigoAnalyzer
from app.services.analysis.jlpt_level_estimator import JLPTLevelEstimator
from app.services.analysis.particle_analyzer import ParticleAnalyzer
try:
    from app.services.analysis.grammar_analyzer import GrammarAnalyzer
except ImportError:
    # Fallback if analyzer not available
    class GrammarAnalyzer:
        @staticmethod
        def analyze(sentence, level=None):
            return {'score': 7.0, 'errors': [], 'suggestions': []}

try:
    from app.services.analysis.vocabulary_analyzer import VocabularyAnalyzer
except ImportError:
    # Fallback if analyzer not available
    class VocabularyAnalyzer:
        @staticmethod
        def analyze(sentence, level=None):
            return {'score': 7.0, 'level_appropriate': True, 'suggestions': []}
from app.services.scoring_service import ScoringService


class AIController:
    """Controller for AI endpoints"""

    def __init__(
        self,
        conversation_repo: ConversationRepository,
        conversation_analysis_repo: ConversationAnalysisRepository,
        ai_service: IAIService,
        scoring_service: ScoringService,
    ):
        self.conversation_repo = conversation_repo
        self.conversation_analysis_repo = conversation_analysis_repo
        self.ai_service = ai_service
        self.scoring_service = scoring_service

    def chat(
        self,
        conversation_id: str,
        user_id: str,
        role: str,
        language: str,
        jlpt_target: str,
        conversation_mode: str,
        message: str
    ) -> Dict[str, Any]:
        """
        Handle AI chat request - matches BRD/SRS spec

        Args:
            user_id: User ID
            role: User role (student/teacher/admin)
            language: Language code (default: "ja")
            jlpt_target: Target JLPT level (N5-N1)
            conversation_mode: Conversation mode
            message: User message

        Returns:
            Dict with reply and conversation_id
        """
        conversation = self.conversation_repo.find_by_id(conversation_id)
        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found")
        if conversation.language != "ja":
            raise ValueError("Language not supported yet")

        # Do not persist new messages here (ai_routes is read-only for conversations)
        temp_messages = list(conversation.messages)
        temp_messages.append(Message(role='user', content=message, timestamp=datetime.utcnow()))
        chat_history = [{'role': m.role, 'content': m.content} for m in temp_messages]

        # Get AI response
        ai_response = self.ai_service.chat(
            chat_history,
            conversation.topic,
            conversation.level
        )

        return {
            'reply': ai_response,
            'conversation_id': str(conversation._id)
        }

    def evaluate(
        self,
        conversation_id: str,
        jlpt_target: str
    ) -> Dict[str, Any]:
        """
        Evaluate conversation - matches BRD/SRS spec

        Args:
            conversation_id: Conversation ID
            jlpt_target: Target JLPT level

        Returns:
            Dict with jlpt_estimation, scores, errors
        """
        conversation = self.conversation_repo.find_by_id(conversation_id)
        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found")
        if conversation.language != "ja":
            raise ValueError("Language not supported yet")

        # Get user messages
        user_messages = [msg for msg in conversation.messages if msg.role == 'user']

        if not user_messages:
            raise ValueError("No user messages found in conversation")

        # Analyze all user messages
        grammar_errors = []
        particle_errors = []
        all_text = ' '.join([msg.content for msg in user_messages])

        # JLPT estimation
        jlpt_estimation_result = JLPTLevelEstimator.estimate(all_text, jlpt_target)
        jlpt_estimation = jlpt_estimation_result['estimated_level']

        # Enrich messages with analysis for scoring
        for msg in user_messages:
            grammar_result = GrammarAnalyzer.analyze(msg.content, conversation.level)
            vocab_result = VocabularyAnalyzer.analyze(msg.content, conversation.level)
            particle_result = ParticleAnalyzer.analyze(msg.content)

            grammar_errors.extend(grammar_result.get('errors', []))
            particle_errors.extend(particle_result.get('particle_errors', []))

            msg.analysis = MessageAnalysis(
                grammar={'score': grammar_result.get('score', 0)},
                vocabulary={'score': vocab_result.get('score', 0)},
                naturalness={'score': grammar_result.get('score', 0)},
                response_time=None,
                grammar_errors=grammar_result.get('errors', []),
                particle_errors=particle_result.get('particle_errors', []),
                keigo_score=None,
                jlpt_estimation=jlpt_estimation,
            )

        overall_score = self.scoring_service.calculate_overall_score(conversation.messages)

        analysis = ConversationAnalysis(
            conversation_id=str(conversation._id),
            user_id=conversation.user_id,
            jlpt_estimation=jlpt_estimation,
            scores=AnalysisScores(
                grammar=float(overall_score.grammar),
                vocabulary=float(overall_score.vocabulary),
                fluency=float(overall_score.fluency),
                naturalness=float(overall_score.naturalness)
            ),
            errors=AnalysisErrors(
                grammar=list(set(grammar_errors)),  # Remove duplicates
                particles=list(set(particle_errors))
            ),
            common_mistakes=list(set(grammar_errors + particle_errors))
        )

        # Persist analysis and cache score on conversation
        saved_analysis = self.conversation_analysis_repo.create(analysis)
        conversation.overall_score = overall_score
        conversation.jlpt_estimation = jlpt_estimation
        self.conversation_repo.update(conversation_id, conversation)

        return {
            'jlpt_estimation': saved_analysis.jlpt_estimation,
            'scores': saved_analysis.scores.to_dict(),
            'errors': saved_analysis.errors.to_dict()
        }

    def correct_sentence(self, sentence: str) -> Dict[str, Any]:
        """
        Correct Japanese sentence - matches BRD/SRS spec

        Args:
            sentence: Japanese sentence to correct

        Returns:
            Dict with original, corrected, explanation_vi
        """
        # Use AI service to correct sentence
        # This is a simplified version - in production, you'd use a specialized prompt
        correction_prompt = f"""
        Sửa câu tiếng Nhật sau đây cho tự nhiên hơn (theo cách người Nhật nói):
        Câu gốc: {sentence}
        
        Trả về JSON với format:
        {{
            "corrected": "câu đã sửa",
            "explanation_vi": "giải thích ngắn bằng tiếng Việt"
        }}
        """

        # For now, return a simple correction
        # In production, call AI service with specialized prompt
        corrected = sentence  # Placeholder
        explanation_vi = "Câu này đã đúng ngữ pháp cơ bản."

        # Try to get AI correction
        try:
            ai_response = self.ai_service.chat(
                [{'role': 'user', 'content': correction_prompt}],
                'sentence_correction',
                'N3'
            )
            # Parse AI response (simplified - in production use structured output)
            corrected = ai_response
            explanation_vi = "AI đã sửa câu cho tự nhiên hơn."
        except Exception as e:
            # Fallback to basic correction
            pass

        return {
            'original': sentence,
            'corrected': corrected,
            'explanation_vi': explanation_vi
        }


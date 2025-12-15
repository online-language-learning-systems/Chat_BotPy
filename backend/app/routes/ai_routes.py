
from flask import Blueprint, request, jsonify, g
from app.controllers.ai_controller import AIController
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.conversation_analysis_repository import ConversationAnalysisRepository
from app.services.ai.ai_factory import create_service
from app.services.scoring_service import ScoringService
from app.utils.decorators import handle_errors, validate_json, require_auth
from app.schemas.ai_schema import (
    AIChatRequestSchema,
    AIEvaluateRequestSchema,
    AICorrectSentenceRequestSchema,
)
from app import mongo


bp = Blueprint('ai', __name__)


def _get_ai_controller() -> AIController:
    """Get AI controller with dependencies"""
    conversation_repo = ConversationRepository(mongo.db.conversations)
    analysis_repo = ConversationAnalysisRepository(mongo.db.conversation_analyses)
    ai_service = create_service()
    scoring_service = ScoringService()
    return AIController(
        conversation_repo=conversation_repo,
        conversation_analysis_repo=analysis_repo,
        ai_service=ai_service,
        scoring_service=scoring_service,
    )


chat_schema = AIChatRequestSchema()
evaluate_schema = AIEvaluateRequestSchema()
correct_sentence_schema = AICorrectSentenceRequestSchema()


@bp.route('/chat', methods=['POST'])
@handle_errors
# @require_auth
@validate_json(chat_schema)
def ai_chat():
    """
    POST /api/v1/ai/chat
    Handle AI chat request - matches BRD/SRS spec
    ---
    tags:
      - AI
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            conversation_id:
              type: string
            user_id:
              type: string
            role:
              type: string
              enum: [student, teacher, admin]
            language:
              type: string
              default: ja
            jlpt_target:
              type: string
              enum: [N5, N4, N3, N2, N1]
            conversation_mode:
              type: string
              enum: [speaking_practice, role_play, jlpt_exam, free_conversation]
            message:
              type: string
          required: [conversation_id, user_id, role, jlpt_target, conversation_mode, message]
    responses:
      200:
        description: AI response
        schema:
          type: object
          properties:
            reply:
              type: string
            conversation_id:
              type: string
      400:
        description: Validation or routing error
    """
    data = request.get_json()
    controller = _get_ai_controller()
    
    if not data.get('conversation_id'):
        return jsonify({"error": "conversation_id is required"}), 400

    try:
        result = controller.chat(
            conversation_id=data['conversation_id'],
            user_id=data['user_id'],
            role=data['role'],
            language=data.get('language', 'ja'),
            jlpt_target=data['jlpt_target'],
            conversation_mode=data['conversation_mode'],
            message=data['message']
        )
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    
    return jsonify(result), 200


@bp.route('/evaluate', methods=['POST'])
@handle_errors
# @require_auth
@validate_json(evaluate_schema)
def ai_evaluate():
    """
    POST /api/v1/ai/evaluate
    ---
    tags:
      - AI
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            conversation_id:
              type: string
            jlpt_target:
              type: string
              enum: [N5, N4, N3, N2, N1]
          required: [conversation_id, jlpt_target]
    responses:
      200:
        description: Evaluation result
        schema:
          type: object
          properties:
            jlpt_estimation:
              type: string
            scores:
              type: object
            errors:
              type: object
      400:
        description: Validation or language error
      404:
        description: Conversation not found
    """
    data = request.get_json()
    controller = _get_ai_controller()
    
    try:
        result = controller.evaluate(
            conversation_id=data['conversation_id'],
            jlpt_target=data['jlpt_target']
        )
        return jsonify(result), 200
    except ValueError as e:
        message = str(e)
        if "not found" in message:
            return jsonify({'error': message}), 404
        return jsonify({'error': message}), 400


@bp.route('/correct-sentence', methods=['POST'])
@handle_errors
# @require_auth
@validate_json(correct_sentence_schema)
def ai_correct_sentence():
    """
    POST /api/v1/ai/correct-sentence
    ---
    tags:
      - AI
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            sentence:
              type: string
          required: [sentence]
    responses:
      200:
        description: Correction result
        schema:
          type: object
          properties:
            original:
              type: string
            corrected:
              type: string
            explanation_vi:
              type: string
      400:
        description: Validation error
    """
    data = request.get_json()
    controller = _get_ai_controller()
    
    result = controller.correct_sentence(
        sentence=data['sentence']
    )
    
    return jsonify(result), 200






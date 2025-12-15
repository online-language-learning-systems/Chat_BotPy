"""
Schemas for AI endpoints matching BRD/SRS specification
"""
from marshmallow import Schema, fields, validate, validates, ValidationError


class AIChatRequestSchema(Schema):
    """Schema for POST /api/v1/ai/chat"""
    conversation_id = fields.Str(required=True)
    user_id = fields.Str(required=True)
    role = fields.Str(
        required=True,
        validate=validate.OneOf(['student', 'teacher', 'admin'])
    )
    language = fields.Str(
        required=False,
        default='ja',
        validate=validate.OneOf(['ja'])
    )
    jlpt_target = fields.Str(
        required=True,
        validate=validate.OneOf(['N5', 'N4', 'N3', 'N2', 'N1'])
    )
    conversation_mode = fields.Str(
        required=True,
        validate=validate.OneOf([
            'speaking_practice',
            'role_play',
            'jlpt_exam',
            'free_conversation'
        ])
    )
    message = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=1000)
    )


class AIEvaluateRequestSchema(Schema):
    """Schema for POST /api/v1/ai/evaluate"""
    conversation_id = fields.Str(required=True)
    jlpt_target = fields.Str(
        required=True,
        validate=validate.OneOf(['N5', 'N4', 'N3', 'N2', 'N1'])
    )


class AICorrectSentenceRequestSchema(Schema):
    """Schema for POST /api/v1/ai/correct-sentence"""
    sentence = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=500)
    )

    @validates('sentence')
    def validate_sentence(self, value):
        if not value.strip():
            raise ValidationError("Sentence cannot be empty or whitespace")


class AIChatResponseSchema(Schema):
    """Response schema for /api/v1/ai/chat"""
    reply = fields.Str(required=True)
    conversation_id = fields.Str(required=True)


class AIEvaluateResponseSchema(Schema):
    """Response schema for /api/v1/ai/evaluate"""
    jlpt_estimation = fields.Str(required=True)
    scores = fields.Dict(required=True)
    errors = fields.Dict(required=True)


class AICorrectSentenceResponseSchema(Schema):
    """Response schema for /api/v1/ai/correct-sentence"""
    original = fields.Str(required=True)
    corrected = fields.Str(required=True)
    explanation_vi = fields.Str(required=True)






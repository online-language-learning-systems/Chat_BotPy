"""
Keigo (敬語) Analyzer
Detects and analyzes keigo usage in Japanese sentences
"""
from typing import Dict, Any, List, Optional
import re


class KeigoAnalyzer:
    """Analyzer for Japanese keigo (honorific language)"""

    # Common keigo patterns
    KEIGO_PATTERNS = {
        'sonkeigo': [
            r'いらっしゃる', r'おっしゃる', r'なさる', r'くださる',
            r'召し上がる', r'ご覧になる', r'おいでになる'
        ],
        'kenjougo': [
            r'いたす', r'申し上げる', r'いただく', r'拝見する',
            r'お目にかかる', r'存じる', r'参る'
        ],
        'teineigo': [
            r'です', r'ます', r'ございます', r'でございます'
        ]
    }

    # Common keigo mistakes
    COMMON_MISTAKES = [
        ('です', 'でございます'),  # Wrong teineigo level
        ('ます', 'いたします'),  # Wrong kenjougo usage
    ]

    @staticmethod
    def analyze(sentence: str, context: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze keigo usage in a sentence

        Args:
            sentence: Japanese sentence to analyze
            context: Optional context (e.g., "formal", "casual")

        Returns:
            Dict with keigo analysis results
        """
        if not sentence:
            return {
                'has_keigo': False,
                'keigo_types': [],
                'score': 0.0,
                'suggestions': [],
                'errors': []
            }

        sentence = sentence.strip()
        keigo_types = []
        errors = []
        suggestions = []

        # Detect keigo types
        for keigo_type, patterns in KeigoAnalyzer.KEIGO_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, sentence):
                    if keigo_type not in keigo_types:
                        keigo_types.append(keigo_type)
                    break

        # Check for common mistakes
        for wrong, correct in KeigoAnalyzer.COMMON_MISTAKES:
            if wrong in sentence and context == 'formal':
                errors.append(f"Consider using '{correct}' instead of '{wrong}' in formal context")
                suggestions.append(f"Replace '{wrong}' with '{correct}'")

        # Calculate score
        has_keigo = len(keigo_types) > 0
        score = 0.0

        if has_keigo:
            # Base score for using keigo
            score = 7.0
            
            # Bonus for using multiple types correctly
            if len(keigo_types) > 1:
                score += 1.0
            
            # Penalty for errors
            score -= len(errors) * 0.5
            
            # Context appropriateness
            if context == 'formal' and 'sonkeigo' in keigo_types:
                score += 1.0
            elif context == 'casual' and 'sonkeigo' in keigo_types:
                score -= 1.0
        else:
            # Check if keigo should be used
            if context == 'formal':
                errors.append("Formal context may require keigo")
                suggestions.append("Consider using です/ます form or honorific language")
                score = 5.0
            else:
                score = 8.0  # Casual context, no keigo is fine

        score = max(0.0, min(10.0, score))  # Clamp between 0-10

        return {
            'has_keigo': has_keigo,
            'keigo_types': keigo_types,
            'score': round(score, 1),
            'suggestions': suggestions,
            'errors': errors,
            'context': context
        }

    @staticmethod
    def detect_keigo_level(sentence: str) -> str:
        """
        Detect keigo level: 'none', 'teineigo', 'kenjougo', 'sonkeigo'

        Args:
            sentence: Japanese sentence

        Returns:
            Keigo level string
        """
        analysis = KeigoAnalyzer.analyze(sentence)
        keigo_types = analysis['keigo_types']

        if 'sonkeigo' in keigo_types:
            return 'sonkeigo'
        elif 'kenjougo' in keigo_types:
            return 'kenjougo'
        elif 'teineigo' in keigo_types:
            return 'teineigo'
        else:
            return 'none'






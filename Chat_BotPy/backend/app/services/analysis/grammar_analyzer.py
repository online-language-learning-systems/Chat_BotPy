"""
Grammar Analyzer
Analyzes Japanese grammar in sentences
"""
from typing import Dict, Any, List, Optional


class GrammarAnalyzer:
    """Analyzer for Japanese grammar"""

    @staticmethod
    def analyze(sentence: str, level: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze grammar in a sentence

        Args:
            sentence: Japanese sentence to analyze
            level: Optional JLPT level (N5-N1)

        Returns:
            Dict with grammar analysis results
        """
        if not sentence:
            return {
                'score': 0.0,
                'errors': [],
                'suggestions': []
            }

        # Basic grammar check
        errors = []
        suggestions = []
        score = 7.0  # Default score

        # Check for basic grammar patterns
        # This is a simplified version - in production, use AI or NLP library
        if 'です' in sentence or 'ます' in sentence:
            score += 1.0  # Has polite form
        else:
            # Check if polite form should be used
            if level and level in ['N5', 'N4']:
                suggestions.append("Consider using です/ます form for polite speech")

        # Check for common grammar mistakes
        if 'はは' in sentence or 'がが' in sentence:
            errors.append("Double particle detected")
            score -= 2.0

        # Check verb conjugation
        if '行く' in sentence and '行きます' not in sentence and '行った' not in sentence:
            # Basic check - in production, use proper NLP
            pass

        score = max(0.0, min(10.0, score))

        return {
            'score': round(score, 1),
            'errors': errors,
            'suggestions': suggestions,
            'level': level
        }

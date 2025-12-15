"""
Vocabulary Analyzer
Analyzes Japanese vocabulary usage
"""
from typing import Dict, Any, List, Optional


class VocabularyAnalyzer:
    """Analyzer for Japanese vocabulary"""

    @staticmethod
    def analyze(sentence: str, level: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze vocabulary in a sentence

        Args:
            sentence: Japanese sentence to analyze
            level: Optional JLPT level (N5-N1)

        Returns:
            Dict with vocabulary analysis results
        """
        if not sentence:
            return {
                'score': 0.0,
                'level_appropriate': True,
                'suggestions': []
            }

        # Basic vocabulary check
        score = 7.0  # Default score
        suggestions = []

        # Count kanji (more kanji = higher level vocabulary)
        kanji_count = len([c for c in sentence if '\u4e00' <= c <= '\u9faf'])
        total_chars = len(sentence)

        if total_chars > 0:
            kanji_ratio = kanji_count / total_chars

            # Adjust score based on kanji usage
            if kanji_ratio > 0.3:
                score += 1.0  # Good kanji usage
            elif kanji_ratio < 0.1 and level and level in ['N2', 'N1']:
                suggestions.append("Consider using more kanji for higher level")
                score -= 1.0

        # Check for appropriate vocabulary level
        level_appropriate = True
        if level:
            # Basic check - in production, use vocabulary database
            if level in ['N5', 'N4'] and kanji_ratio > 0.5:
                level_appropriate = False
                suggestions.append("Vocabulary may be too advanced for target level")

        score = max(0.0, min(10.0, score))

        return {
            'score': round(score, 1),
            'level_appropriate': level_appropriate,
            'kanji_ratio': round(kanji_ratio, 2) if total_chars > 0 else 0.0,
            'suggestions': suggestions
        }

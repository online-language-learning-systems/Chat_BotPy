"""
Fluency Analyzer
Analyzes fluency based on response time and speech patterns
"""
from typing import Dict, Any, Optional


class FluencyAnalyzer:
    """Analyzer for Japanese speaking fluency"""

    @staticmethod
    def analyze(response_time_ms: Optional[int] = None, sentence_length: Optional[int] = None) -> Dict[str, Any]:
        """
        Analyze fluency based on response time

        Args:
            response_time_ms: Response time in milliseconds
            sentence_length: Length of sentence (optional)

        Returns:
            Dict with fluency analysis results
        """
        if response_time_ms is None:
            return {
                'score': 7.0,
                'level': 'medium',
                'suggestions': []
            }

        # Convert to seconds
        response_time_s = response_time_ms / 1000.0

        # Calculate score based on response time
        # Faster response = higher fluency
        if response_time_s < 5:
            score = 10.0
            level = 'excellent'
        elif response_time_s < 10:
            score = 9.0
            level = 'very_good'
        elif response_time_s < 20:
            score = 8.0
            level = 'good'
        elif response_time_s < 30:
            score = 7.0
            level = 'medium'
        elif response_time_s < 45:
            score = 6.0
            level = 'needs_improvement'
        else:
            score = 5.0
            level = 'slow'

        suggestions = []
        if response_time_s > 30:
            suggestions.append("Try to respond more quickly to improve fluency")
        if sentence_length and response_time_s / sentence_length > 2:
            suggestions.append("Practice speaking shorter sentences first")

        return {
            'score': round(score, 1),
            'level': level,
            'response_time_s': round(response_time_s, 2),
            'suggestions': suggestions
        }

"""
JLPT Level Estimator
Estimates JLPT level (N5-N1) based on grammar, vocabulary, and sentence complexity
"""
from typing import Dict, Any, List, Optional
import re


class JLPTLevelEstimator:
    """Estimates JLPT level from Japanese text"""

    # JLPT grammar patterns by level (simplified)
    JLPT_GRAMMAR_PATTERNS = {
        'N5': [
            r'です', r'ます', r'だ', r'である',
            r'〜は', r'〜が', r'〜を', r'〜に', r'〜で',
            r'〜たい', r'〜ない', r'〜た', r'〜ている'
        ],
        'N4': [
            r'〜てください', r'〜てもいい', r'〜てはいけない',
            r'〜なければならない', r'〜ほうがいい',
            r'〜ので', r'〜から', r'〜が', r'〜けど',
            r'〜ようだ', r'〜そうだ', r'〜らしい'
        ],
        'N3': [
            r'〜ば', r'〜なら', r'〜たら',
            r'〜ところ', r'〜ばかり', r'〜だけ',
            r'〜によって', r'〜について', r'〜に対して',
            r'〜ように', r'〜ために', r'〜のに'
        ],
        'N2': [
            r'〜ばかりか', r'〜どころか', r'〜ばかりでなく',
            r'〜に限らず', r'〜に応じて', r'〜に伴って',
            r'〜に加えて', r'〜に代わって', r'〜に基づいて',
            r'〜に従って', r'〜に沿って', r'〜に反して'
        ],
        'N1': [
            r'〜を余儀なくされる', r'〜を禁じ得ない',
            r'〜に越したことはない', r'〜に足る',
            r'〜をものともせず', r'〜をよそに',
            r'〜を皮切りに', r'〜を機に',
            r'〜を問わず', r'〜を抜きにして'
        ]
    }

    # Vocabulary complexity indicators
    VOCABULARY_INDICATORS = {
        'N5': ['私', 'あなた', 'これ', 'それ', 'あれ', '食べる', '飲む', '行く', '来る'],
        'N4': ['準備', '練習', '説明', '経験', '約束', '心配', '大切'],
        'N3': ['影響', '関係', '状況', '条件', '理由', '方法', '目的'],
        'N2': ['実施', '促進', '改善', '対応', '検討', '確認', '調整'],
        'N1': ['実施', '促進', '改善', '対応', '検討', '確認', '調整', '抽象的', '具体的']
    }

    @staticmethod
    def estimate(text: str, target_level: Optional[str] = None) -> Dict[str, Any]:
        """
        Estimate JLPT level from text

        Args:
            text: Japanese text to analyze
            target_level: Optional target level (N5-N1)

        Returns:
            Dict with estimated level and confidence
        """
        if not text:
            return {
                'estimated_level': 'N5',
                'confidence': 0.0,
                'indicators': {}
            }

        text = text.strip()
        level_scores = {
            'N5': 0,
            'N4': 0,
            'N3': 0,
            'N2': 0,
            'N1': 0
        }

        # Check grammar patterns
        for level, patterns in JLPTLevelEstimator.JLPT_GRAMMAR_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    level_scores[level] += 1

        # Check vocabulary
        for level, vocab_list in JLPTLevelEstimator.VOCABULARY_INDICATORS.items():
            for vocab in vocab_list:
                if vocab in text:
                    level_scores[level] += 0.5

        # Sentence complexity (length, kanji ratio)
        sentence_length = len(text)
        kanji_count = len(re.findall(r'[\u4e00-\u9faf]', text))
        kanji_ratio = kanji_count / sentence_length if sentence_length > 0 else 0

        # Adjust scores based on complexity
        if sentence_length > 50:
            level_scores['N3'] += 1
            level_scores['N2'] += 1
        if kanji_ratio > 0.3:
            level_scores['N2'] += 1
            level_scores['N1'] += 1
        if kanji_ratio > 0.5:
            level_scores['N1'] += 2

        # Determine estimated level
        max_score = max(level_scores.values())
        estimated_level = 'N5'  # Default

        # Find highest scoring level
        for level in ['N1', 'N2', 'N3', 'N4', 'N5']:
            if level_scores[level] == max_score:
                estimated_level = level
                break

        # Calculate confidence (0-1)
        total_score = sum(level_scores.values())
        confidence = max_score / total_score if total_score > 0 else 0.0
        confidence = min(1.0, confidence)

        # Compare with target level if provided
        matches_target = False
        if target_level:
            matches_target = estimated_level == target_level

        return {
            'estimated_level': estimated_level,
            'confidence': round(confidence, 2),
            'level_scores': level_scores,
            'matches_target': matches_target,
            'indicators': {
                'sentence_length': sentence_length,
                'kanji_ratio': round(kanji_ratio, 2),
                'has_complex_grammar': max_score > 2
            }
        }

    @staticmethod
    def get_level_from_estimation(estimation: Dict[str, Any]) -> str:
        """Extract level string from estimation dict"""
        return estimation.get('estimated_level', 'N5')







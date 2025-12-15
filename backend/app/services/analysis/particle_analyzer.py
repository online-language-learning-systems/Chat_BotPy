"""
Particle Analyzer
Detects particle errors in Japanese sentences (は/が, に/で, etc.)
"""
from typing import Dict, Any, List, Optional
import re


class ParticleAnalyzer:
    """Analyzer for Japanese particles (助詞)"""

    # Common particle pairs that are often confused
    PARTICLE_PAIRS = {
        'は/が': {
            'は': r'は',
            'が': r'が',
            'rule': 'は for topic, が for subject/emphasis',
            'common_mistake': 'Using は when が is needed for emphasis'
        },
        'に/で': {
            'に': r'に',
            'で': r'で',
            'rule': 'に for location of existence/destination, で for action location',
            'common_mistake': 'Using に when で is needed for action location'
        },
        'を/が': {
            'を': r'を',
            'が': r'が',
            'rule': 'を for direct object, が for potential/desire verbs',
            'common_mistake': 'Using を with potential form verbs (should use が)'
        },
        'に/へ': {
            'に': r'に',
            'へ': r'へ',
            'rule': 'に for specific destination, へ for direction',
            'common_mistake': 'Interchangeable but に is more common for destination'
        },
        'と/や': {
            'と': r'と',
            'や': r'や',
            'rule': 'と for complete list, や for incomplete list',
            'common_mistake': 'Using と when や is needed for incomplete list'
        }
    }

    # Particle usage patterns
    PARTICLE_PATTERNS = {
        'は': {
            'correct': [
                r'[^は]は[^は]',  # Not double は
                r'[はが]は',  # After は or が (topic marker)
            ],
            'incorrect': [
                r'はは',  # Double は
            ]
        },
        'が': {
            'correct': [
                r'[^が]が[^が]',  # Not double が
            ],
            'incorrect': [
                r'がが',  # Double が
            ]
        }
    }

    @staticmethod
    def analyze(sentence: str, context: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze particle usage in a sentence

        Args:
            sentence: Japanese sentence to analyze
            context: Optional context for better analysis

        Returns:
            Dict with particle analysis results
        """
        if not sentence:
            return {
                'particle_errors': [],
                'score': 0.0,
                'suggestions': [],
                'detected_particles': []
            }

        sentence = sentence.strip()
        errors = []
        suggestions = []
        detected_particles = []

        # Detect all particles
        all_particles = re.findall(r'[はがをにでへとやからまでより]', sentence)
        detected_particles = list(set(all_particles))

        # Check for common particle mistakes
        # は/が confusion
        if 'は' in sentence and 'が' in sentence:
            # Check if both are used correctly
            wa_count = sentence.count('は')
            ga_count = sentence.count('が')
            if wa_count > 2 or ga_count > 2:
                errors.append('は/が: Multiple uses may indicate confusion')
                suggestions.append('Review は (topic) vs が (subject/emphasis) usage')

        # に/で confusion
        if 'に' in sentence and 'で' in sentence:
            # Check for location-related particles
            location_patterns = [
                r'[場所]に', r'[場所]で',
                r'[場所]へ', r'[場所]を'
            ]
            for pattern in location_patterns:
                matches = re.findall(pattern, sentence)
                if len(matches) > 1:
                    errors.append('に/で: Multiple location particles may indicate confusion')
                    suggestions.append('に for existence/destination, で for action location')
                    break

        # Check for double particles (common mistake)
        double_particles = re.findall(r'([はがをにでへとやからまでより])\1', sentence)
        if double_particles:
            for particle in set(double_particles):
                errors.append(f'Double particle "{particle}{particle}" detected')
                suggestions.append(f'Remove duplicate "{particle}"')

        # Check particle with potential form verbs
        potential_pattern = r'[見聞読書話]ける'
        if re.search(potential_pattern, sentence) and 'を' in sentence:
            # Potential form verbs should use が, not を
            if 'を' in sentence and 'が' not in sentence:
                errors.append('を/が: Potential form verbs should use が instead of を')
                suggestions.append('Use が with potential form verbs (e.g., 日本語が話せます)')

        # Calculate score
        base_score = 10.0
        score = base_score - (len(errors) * 2.0)
        score = max(0.0, min(10.0, score))

        return {
            'particle_errors': errors,
            'score': round(score, 1),
            'suggestions': suggestions,
            'detected_particles': detected_particles,
            'particle_count': len(detected_particles)
        }

    @staticmethod
    def get_particle_errors(analysis: Dict[str, Any]) -> List[str]:
        """Extract particle errors list from analysis"""
        return analysis.get('particle_errors', [])






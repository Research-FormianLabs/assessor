import re
from typing import Dict, Any

class IAIAnalyzer:
    """
    Analyzes Input Alignment Index (IAI) for user prompts.
    Measures clarity, specificity, and structure of user input.
    """

    def __init__(self):
        self.scoring_rules = {
            'context_completeness': {
                'keywords': ['for', 'about', 'context', 'because', 'since', 'given'],
                'weight': 0.20
            },
            'specificity_level': {
                'concrete_words': ['specific', 'exact', 'precise', 'concrete', 'detailed'],
                'parameters': ['number', 'count', 'length', 'size', 'time', 'budget'],
                'weight': 0.25
            },
            'language_quality': {
                'readability_threshold': 60,  # Flesch Reading Ease (simplified)
                'weight': 0.20
            },
            'structure_quality': {
                'organizers': ['first', 'second', 'then', 'finally', 'step'],
                'weight': 0.15
            },
            'information_sufficiency': {
                'optimal_word_count': (20, 150),  # min, max words
                'weight': 0.10
            },
            'tone_sentiment': {
                'clarity_indicators': ['please', 'clearly', 'specifically'],
                'weight': 0.10
            }
        }

    def analyze(self, prompt: str) -> Dict[str, Any]:
        """Analyze a user prompt and return IAI score and components."""

        word_count = len(prompt.split())
        sentence_count = len([s for s in re.split(r'[.!?]+', prompt) if s.strip()])

        # Component scores (0-1 scale)
        components = {
            'context_completeness': self._score_context_completeness(prompt),
            'specificity_level': self._score_specificity(prompt, word_count),
            'language_quality': self._score_language_quality(prompt, sentence_count, word_count),
            'structure_quality': self._score_structure(prompt),
            'information_sufficiency': self._score_sufficiency(word_count),
            'tone_sentiment': self._score_tone(prompt)
        }

        # Calculate weighted IAI score
        iai_score = sum(components[comp] * self.scoring_rules[comp]['weight']
                       for comp in components)

        return {
            'iai_score': min(iai_score, 1.0),  # Cap at 1.0
            'components': components,
            'word_count': word_count,
            'sentence_count': sentence_count,
            'interpretation': self._generate_interpretation(iai_score, components)
        }

    def _score_context_completeness(self, prompt: str) -> float:
        """Score based on presence of contextual information."""
        context_markers = sum(1 for keyword in self.scoring_rules['context_completeness']['keywords']
                             if keyword in prompt.lower())
        return min(context_markers / 3, 1.0)  # 0-1 scale

    def _score_specificity(self, prompt: str, word_count: int) -> float:
        """Score based on specificity and concrete language."""
        prompt_lower = prompt.lower()

        # Check for concrete language
        concrete_score = sum(1 for word in self.scoring_rules['specificity_level']['concrete_words']
                           if word in prompt_lower)

        # Check for measurable parameters
        param_score = sum(1 for param in self.scoring_rules['specificity_level']['parameters']
                        if param in prompt_lower)

        # Combine scores (more weight to concrete language)
        specificity = (concrete_score * 0.7 + param_score * 0.3) / 5  # Normalize
        return min(specificity, 1.0)

    def _score_language_quality(self, prompt: str, sentence_count: int, word_count: int) -> float:
        """Score based on language clarity and readability."""
        if word_count == 0:
            return 0.0

        # Simple readability heuristic (words per sentence)
        avg_sentence_length = word_count / max(sentence_count, 1)

        # Optimal range: 10-20 words per sentence
        if avg_sentence_length < 5:
            return 0.3  # Too fragmented
        elif avg_sentence_length <= 20:
            return 0.8  # Good readability
        elif avg_sentence_length <= 30:
            return 0.5  # Getting long
        else:
            return 0.2  # Too verbose

    def _score_structure(self, prompt: str) -> float:
        """Score based on structural organization."""
        prompt_lower = prompt.lower()
        organizers = sum(1 for organizer in self.scoring_rules['structure_quality']['organizers']
                       if organizer in prompt_lower)

        # Also check for question marks (structured questions)
        has_question = '?' in prompt
        question_bonus = 0.2 if has_question else 0

        structure_score = min(organizers / 3, 0.8) + question_bonus
        return min(structure_score, 1.0)

    def _score_sufficiency(self, word_count: int) -> float:
        """Score based on information sufficiency (word count)."""
        optimal_min, optimal_max = self.scoring_rules['information_sufficiency']['optimal_word_count']

        if word_count < 5:
            return 0.1  # Severely insufficient
        elif word_count < optimal_min:
            return 0.3 + (word_count / optimal_min) * 0.3  # 0.3-0.6
        elif word_count <= optimal_max:
            return 0.6 + ((word_count - optimal_min) / (optimal_max - optimal_min)) * 0.3  # 0.6-0.9
        else:
            return 0.9  # Very detailed (could be verbose)

    def _score_tone(self, prompt: str) -> float:
        """Score based on tone and clarity indicators."""
        prompt_lower = prompt.lower()
        clarity_indicators = sum(1 for indicator in self.scoring_rules['tone_sentiment']['clarity_indicators']
                               if indicator in prompt_lower)

        # Base score with bonus for clear communication
        base_score = 0.6
        clarity_bonus = min(clarity_indicators * 0.2, 0.4)

        return min(base_score + clarity_bonus, 1.0)

    def _generate_interpretation(self, score: float, components: Dict) -> str:
        """Generate human-readable interpretation of IAI score."""
        if score >= 0.8:
            return "Excellent input alignment - highly specific and well-structured"
        elif score >= 0.6:
            return "Good input alignment - clear with sufficient context"
        elif score >= 0.4:
            return "Moderate input alignment - could benefit from more specificity"
        else:
            return "Poor input alignment - vague or insufficient context"

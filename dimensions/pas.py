import re
from typing import Dict, Any

class PASAnalyzer:
    """
    Analyzes Process Alignment Score (PAS) for AI responses.
    Measures the naturalness, rhythm, and collaborative quality of the interaction process.
    """

    def __init__(self):
        # Scoring weights for different PAS components
        self.weights = {
            'chunking': 0.30,      # Information organization
            'structure': 0.25,      # Use of lists, headings, etc.
            'collaboration': 0.25,  # Partnership language
            'rhythm': 0.20         # Natural flow and pacing
        }

        # Patterns for detection
        self.patterns = {
            'chunking_indicators': [
                r'\n\n',  # Paragraph breaks
                r'\n- ', r'\n\* ', r'\n\d+\.',  # List indicators
                r'first', r'next', r'then', r'finally',  # Sequencing words
            ],
            'structure_indicators': [
                r'^#+', r'^[A-Z][^.!?]*:',  # Headings
                r'\d+\.\s+', r'-\s+', r'\*\s+',  # Numbered/bulleted lists
                r'table:', r'chart:', r'diagram:',  # Structural elements
            ],
            'collaboration_indicators': [
                r"let's", r"we can", r"we should", r"our",
                r"what do you think", r"how about", r"your thoughts",
                r"together", r"collaborate", r"partner", r"build with",
                r"does this make sense", r"shall we", r"would you like"
            ],
            'rhythm_indicators': [
                r'\?',  # Questions (indicating turn-taking)
                r'...', r'—',  # Pauses/breaks in thought
                r'briefly', r'in summary', r'to recap',  # Pacing markers
            ]
        }

    def analyze(self, response: str) -> Dict[str, Any]:
        """Analyze response for process alignment and return PAS score."""

        scores = {}

        # 1. Chunking Analysis
        chunking_score = self._analyze_chunking(response)
        scores['chunking'] = chunking_score

        # 2. Structure Analysis
        structure_score = self._analyze_structure(response)
        scores['structure'] = structure_score

        # 3. Collaboration Analysis
        collaboration_score = self._analyze_collaboration(response)
        scores['collaboration'] = collaboration_score

        # 4. Rhythm Analysis
        rhythm_score = self._analyze_rhythm(response)
        scores['rhythm'] = rhythm_score

        # Calculate weighted PAS score
        pas_score = (
            scores['chunking'] * self.weights['chunking'] +
            scores['structure'] * self.weights['structure'] +
            scores['collaboration'] * self.weights['collaboration'] +
            scores['rhythm'] * self.weights['rhythm']
        )

        return {
            'pas_score': round(pas_score, 3),
            'component_scores': scores,
            'interpretation': self._generate_interpretation(pas_score, scores)
        }

    def _analyze_chunking(self, text: str) -> float:
        """Analyze how well information is chunked/organized."""
        score = 0.0

        # Check for paragraph breaks (good chunking)
        paragraphs = re.split(r'\n\n+', text)
        if len(paragraphs) > 1:
            score += 0.3

        # Check for sequencing words
        sequencing_words = ['first', 'next', 'then', 'finally', 'step', 'phase']
        seq_count = sum(1 for word in sequencing_words if word in text.lower())
        score += min(seq_count * 0.15, 0.3)

        # Check for list indicators
        list_patterns = [r'\n- ', r'\n\* ', r'\n\d+\.']
        list_count = sum(len(re.findall(pattern, text)) for pattern in list_patterns)
        score += min(list_count * 0.1, 0.4)

        return min(score, 1.0)

    def _analyze_structure(self, text: str) -> float:
        """Analyze use of structural elements."""
        score = 0.0

        # Check for headings/major sections
        heading_patterns = [r'^#+', r'^[A-Z][^.!?]*:']
        has_headings = any(re.search(pattern, text, re.MULTILINE) for pattern in heading_patterns)
        if has_headings:
            score += 0.4

        # Check for lists
        list_count = len(re.findall(r'\n\d+\.|\n- |\n\* ', text))
        if list_count >= 2:
            score += 0.4
        elif list_count == 1:
            score += 0.2

        # Check for other structural elements
        structural_elements = ['table:', 'chart:', 'diagram:', 'summary:']
        has_elements = any(element in text.lower() for element in structural_elements)
        if has_elements:
            score += 0.2

        return min(score, 1.0)

    def _analyze_collaboration(self, text: str) -> float:
        """Analyze use of collaborative language."""
        score = 0.0

        collaboration_phrases = [
            "let's", "we can", "we should", "our", "together", "collaborate",
            "what do you think", "how about", "your thoughts", "partner",
            "does this make sense", "shall we", "would you like", "build with"
        ]

        # Count collaborative phrases
        text_lower = text.lower()
        collab_count = sum(1 for phrase in collaboration_phrases if phrase in text_lower)

        if collab_count >= 3:
            score = 1.0
        elif collab_count == 2:
            score = 0.7
        elif collab_count == 1:
            score = 0.4
        else:
            score = 0.1  # Base score for neutral responses

        return score

    def _analyze_rhythm(self, text: str) -> float:
        """Analyze conversational rhythm and pacing."""
        score = 0.0

        # Check for questions (indicating turn-taking)
        question_count = text.count('?')
        score += min(question_count * 0.2, 0.4)

        # Check for pauses/breaks
        pause_indicators = ['...', '—', 'briefly', 'in summary', 'to recap']
        pause_count = sum(text.count(indicator) for indicator in pause_indicators)
        score += min(pause_count * 0.15, 0.3)

        # Check sentence length variation (good rhythm)
        sentences = re.split(r'[.!?]+', text)
        if len(sentences) >= 3:
            sentence_lengths = [len(sent.strip()) for sent in sentences if sent.strip()]
            if sentence_lengths:
                variation = max(sentence_lengths) / min(sentence_lengths) if min(sentence_lengths) > 0 else 1
                if 2 <= variation <= 5:  # Good variation range
                    score += 0.3

        return min(score, 1.0)

    def _generate_interpretation(self, score: float, components: Dict) -> str:
        """Generate interpretation based on PAS score."""
        if score >= 0.8:
            return "Excellent process alignment - natural, collaborative flow"
        elif score >= 0.6:
            return "Good process alignment - structured and engaging"
        elif score >= 0.4:
            return "Moderate process alignment - functional but could be smoother"
        elif score >= 0.2:
            return "Poor process alignment - disjointed or inefficient"
        else:
            return "Very poor process alignment - jarring and difficult to follow"

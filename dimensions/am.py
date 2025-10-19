import re
from typing import Dict, Any

class AMAnalyzer:
    """
    Analyzes Alignment Modulator (AM) - how well AI response matches user intent.
    AM is a multiplier (0.8-1.2) that adjusts the final RI score.
    """

    def __init__(self):
        # Simple UIP (User Intent Pattern) detection patterns
        self.uip_patterns = {
            'precision_seeker': {
                'keywords': ['exact', 'define', 'list', 'specifically', 'no fluff', 'correct', 'only', 'step-by-step'],
                'preferred_response_style': ['concise', 'structured', 'bounded', 'bullet points']
            },
            'strategic_explorer': {
                'keywords': ['framework', 'model', 'system', 'big picture', 'how does this fit', 'map', 'concept'],
                'preferred_response_style': ['framework', 'analogy', 'structured', 'overview']
            },
            'co_creation_partner': {
                'keywords': ["let's", 'build', 'together', 'collaborate', 'your input', 'what do you think'],
                'preferred_response_style': ['interactive', 'iterative', 'suggestive', 'questioning']
            }
        }

        # Response style analysis patterns
        self.response_styles = {
            'concise': {
                'indicators': ['short sentences', 'bullet points', 'direct answers', 'minimal explanation'],
                'max_words': 150
            },
            'structured': {
                'indicators': ['numbered lists', 'headings', 'sections', 'first/then/next'],
                'patterns': [r'\n\d+\.', r'\n- ', r'first', 'next', 'finally']
            },
            'interactive': {
                'indicators': ['questions', 'your thoughts', 'what do you think', 'shall we'],
                'patterns': [r'\?', 'your input', 'collaborate']
            },
            'framework': {
                'indicators': ['analogies', 'models', 'systems', 'like a', 'similar to'],
                'patterns': [r'like a', r'similar to', r'framework', r'model']
            }
        }

    def analyze(self, user_prompt: str, ai_response: str) -> Dict[str, Any]:
        """
        Analyze alignment between user intent and AI response style.
        Returns AM score (0.8-1.2) and UIP detection.
        """
        # Step 1: Detect User Intent Pattern (UIP)
        detected_uip, uip_confidence = self._detect_uip(user_prompt)

        # Step 2: Analyze AI response style
        ai_style = self._analyze_ai_style(ai_response)

        # Step 3: Calculate Alignment Modulator (AM)
        am_score = self._calculate_am(detected_uip, ai_style, ai_response)

        return {
            'am_score': round(am_score, 3),
            'user_intent_pattern': {
                'detected': detected_uip,
                'confidence': uip_confidence
            },
            'ai_response_style': ai_style,
            'interpretation': self._generate_interpretation(am_score, detected_uip)
        }

    def _detect_uip(self, prompt: str) -> tuple[str, float]:
        """Detect User Intent Pattern from prompt."""
        prompt_lower = prompt.lower()
        best_uip = 'precision_seeker'  # Default
        best_score = 0

        for uip_name, uip_data in self.uip_patterns.items():
            score = 0
            for keyword in uip_data['keywords']:
                if re.search(rf'\b{re.escape(keyword)}\b', prompt_lower):
                    score += 1

            if score > best_score:
                best_score = score
                best_uip = uip_name

        # Calculate confidence (0.0-1.0)
        confidence = min(best_score / 3.0, 1.0)  # Max 3 keywords = full confidence

        return best_uip, confidence

    def _analyze_ai_style(self, response: str) -> Dict[str, float]:
        """Analyze the style of AI response."""
        response_lower = response.lower()
        style_scores = {}

        for style_name, style_data in self.response_styles.items():
            score = 0.0

            # Check word count for concise style
            if style_name == 'concise':
                word_count = len(response.split())
                if word_count <= style_data['max_words']:
                    score += 0.5

            # Check patterns for other styles
            if 'patterns' in style_data:
                for pattern in style_data['patterns']:
                    if re.search(pattern, response_lower) if isinstance(pattern, str) else pattern in response_lower:
                        score += 0.3

            style_scores[style_name] = min(score, 1.0)

        return style_scores

    def _calculate_am(self, detected_uip: str, ai_style: Dict, ai_response: str) -> float:
        """Calculate Alignment Modulator score (0.8-1.2)."""
        am_score = 1.0  # Neutral starting point

        # Get preferred styles for detected UIP
        preferred_styles = self.uip_patterns[detected_uip]['preferred_response_style']

        # Check if AI used preferred styles
        style_match_score = 0.0
        for preferred_style in preferred_styles:
            style_match_score += ai_style.get(preferred_style, 0.0)

        # Normalize style match score
        style_match_score = min(style_match_score / len(preferred_styles), 1.0)

        # Calculate AM based on style matching
        if style_match_score >= 0.8:
            am_score = 1.2  # Excellent alignment
        elif style_match_score >= 0.6:
            am_score = 1.1  # Good alignment
        elif style_match_score >= 0.4:
            am_score = 1.0  # Neutral alignment
        elif style_match_score >= 0.2:
            am_score = 0.9  # Slight misalignment
        else:
            am_score = 0.8  # Significant misalignment

        # Additional checks for response quality
        word_count = len(ai_response.split())

        # Penalty for extremely long responses to precision seekers
        if detected_uip == 'precision_seeker' and word_count > 300:
            am_score -= 0.1

        # Bonus for interactive elements with co-creation partners
        if detected_uip == 'co_creation_partner' and ai_style.get('interactive', 0) > 0.5:
            am_score += 0.1

        return max(0.8, min(am_score, 1.2))

    def _generate_interpretation(self, am_score: float, uip: str) -> str:
        """Generate interpretation based on AM score."""
        if am_score >= 1.15:
            return f"AM: Excellent alignment - AI perfectly matched {uip} intent"
        elif am_score >= 1.05:
            return f"AM: Good alignment - AI understood {uip} requirements"
        elif am_score >= 0.95:
            return f"AM: Neutral alignment - Basic {uip} understanding"
        elif am_score >= 0.85:
            return f"AM: Slight misalignment - Some {uip} style mismatches"
        else:
            return f"AM: Significant misalignment - Poor {uip} style matching"

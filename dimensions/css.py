import re
from typing import Dict, Any, List
from datetime import datetime

class CSSAnalyzer:
    """
    Analyzes Cognitive Safety Scale (CSS) for AI responses.
    Measures the user's state of trust, comfort, and psychological safety.
    """

    def __init__(self):
        # CSS Levels with descriptions and indicators
        self.levels = {
            1: {
                'name': 'Cognitive Lockdown',
                'description': 'User feels overwhelmed or unable to proceed',
                'indicators': {
                    'ai_signals': ['complex jargon', 'overwhelming detail', 'no clarification offered'],
                    'user_signals': ['confusion', 'frustration', 'abandonment']
                }
            },
            2: {
                'name': 'Safety Testing',
                'description': 'User is cautious but willing to engage',
                'indicators': {
                    'ai_signals': ['basic instructions', 'minimal guidance', 'neutral tone'],
                    'user_signals': ['tentative engagement', 'simple questions', 'testing boundaries']
                }
            },
            3: {
                'name': 'Consequence-Free Scrutiny',
                'description': 'User feels comfortable exploring without fear',
                'indicators': {
                    'ai_signals': ['encouraging questions', 'patient explanations', 'validation'],
                    'user_signals': ['curious exploration', 'follow-up questions', 'comfortable disagreement']
                }
            },
            4: {
                'name': 'Co-Creative Partnership',
                'description': 'Active collaboration with shared ownership',
                'indicators': {
                    'ai_signals': ["we language", 'inviting feedback', 'shared decision-making'],
                    'user_signals': ['collaborative language', 'building on ideas', 'shared ownership']
                }
            },
            5: {
                'name': 'Cognitive Expansion',
                'description': 'User feels empowered to apply learning broadly',
                'indicators': {
                    'ai_signals': ['encouraging generalization', 'future applications', 'empowerment language'],
                    'user_signals': ['creative applications', 'broad thinking', 'confidence in transfer']
                }
            }
        }

        # Safety signals and patterns
        self.safety_patterns = {
            'positive_signals': [
                r"does this make sense", r"please clarify", r"let me know",
                r"your thoughts", r"what do you think", r"feel free to ask",
                r"i want to ensure", r"correct me if I'm wrong", r"am I understanding",
                r"we can adjust", r"your feedback", r"how does that sound",
                r"comfortable with", r"happy to explain", r"take your time"
            ],
            'negative_signals': [
                r"obviously", r"clearly", r"everyone knows",
                r"you should know", r"basic knowledge", r"simple concept",
                r"easy to understand", r"no excuse for not knowing",
                r"if you can't understand this", r"even a child could"
            ],
            'collaborative_language': [
                r"let's", r"we can", r"we should", r"our", r"together",
                r"collaborate", r"partner", r"jointly", r"build with",
                r"work together", r"team effort"
            ],
            'empowerment_signals': [
                r"you can", r"you have the ability", r"your expertise",
                r"build on your knowledge", r"apply this to", r"generalize",
                r"expand this concept", r"future applications"
            ]
        }

    def analyze(self, user_prompt: str, ai_response: str, interaction_data: Dict = None) -> Dict[str, Any]:
        """
        Analyze cognitive safety level based on AI response and interaction context.
        """
        if interaction_data is None:
            interaction_data = {}

        # Analyze AI response for safety signals
        ai_safety_score = self._analyze_ai_safety(ai_response)

        # Analyze user prompt for comfort indicators
        user_comfort_level = self._analyze_user_comfort(user_prompt)

        # Consider interaction context (response time, length, etc.)
        context_score = self._analyze_context(interaction_data)

        # Determine CSS level based on combined analysis
        css_level = self._determine_css_level(ai_safety_score, user_comfort_level, context_score)

        # Calculate CSS score (0-1 scale)
        css_score = css_level / 5.0

        return {
            'css_score': round(css_score, 3),
            'css_level': css_level,
            'level_name': self.levels[css_level]['name'],
            'interpretation': self._generate_interpretation(css_level, css_score),
            'safety_analysis': {
                'ai_safety_score': ai_safety_score,
                'user_comfort_level': user_comfort_level,
                'context_score': context_score,
                'positive_signals_found': self._find_safety_signals(ai_response, 'positive'),
                'negative_signals_found': self._find_safety_signals(ai_response, 'negative')
            }
        }

    def _analyze_ai_safety(self, response: str) -> float:
        """Analyze AI response for safety-promoting signals."""
        response_lower = response.lower()
        safety_score = 0.5  # Neutral starting point

        # Positive safety signals
        positive_count = 0
        for pattern in self.safety_patterns['positive_signals']:
            if re.search(pattern, response_lower):
                positive_count += 1

        # Collaborative language
        collaborative_count = 0
        for pattern in self.safety_patterns['collaborative_language']:
            if re.search(pattern, response_lower):
                collaborative_count += 1

        # Empowerment signals
        empowerment_count = 0
        for pattern in self.safety_patterns['empowerment_signals']:
            if re.search(pattern, response_lower):
                empowerment_count += 1

        # Negative safety signals (penalties)
        negative_count = 0
        for pattern in self.safety_patterns['negative_signals']:
            if re.search(pattern, response_lower):
                negative_count += 1

        # Calculate composite safety score
        safety_score += (positive_count * 0.1)
        safety_score += (collaborative_count * 0.08)
        safety_score += (empowerment_count * 0.07)
        safety_score -= (negative_count * 0.15)

        return max(0.0, min(safety_score, 1.0))  # FIXED: Added missing parenthesis

    def _analyze_user_comfort(self, prompt: str) -> float:
        """Analyze user prompt for comfort indicators."""
        prompt_lower = prompt.lower()
        comfort_score = 0.5

        # Signs of user comfort
        comfortable_signals = [
            'confident', 'comfortable', 'clear', 'understand',
            'excited', 'interested', 'curious', 'ready'
        ]

        # Signs of user discomfort
        uncomfortable_signals = [
            'confused', 'frustrated', 'overwhelmed', 'lost',
            'complicated', 'difficult', 'hard', 'struggling'
        ]

        comfortable_count = sum(1 for signal in comfortable_signals if signal in prompt_lower)
        uncomfortable_count = sum(1 for signal in uncomfortable_signals if signal in prompt_lower)

        comfort_score += (comfortable_count * 0.1)
        comfort_score -= (uncomfortable_count * 0.15)

        return max(0.0, min(comfort_score, 1.0))

    def _analyze_context(self, interaction_data: Dict) -> float:
        """Analyze interaction context for safety indicators."""
        context_score = 0.7  # Base context score

        # Consider response length appropriateness
        response_length = interaction_data.get('response_length', 0)
        prompt_length = interaction_data.get('user_prompt_length', 0)

        # If AI response is much longer than user prompt, might be overwhelming
        if prompt_length > 0 and response_length > 0:
            ratio = response_length / prompt_length
            if ratio > 5:  # Response is 5x longer than prompt
                context_score -= 0.2
            elif ratio < 0.5:  # Response is half the length of prompt
                context_score += 0.1  # Concise can be good

        return max(0.0, min(context_score, 1.0))

    def _determine_css_level(self, ai_safety: float, user_comfort: float, context: float) -> int:
        """Determine CSS level based on combined scores."""
        combined_score = (ai_safety * 0.6 + user_comfort * 0.3 + context * 0.1)

        if combined_score >= 0.8:
            return 5  # Cognitive Expansion
        elif combined_score >= 0.7:
            return 4  # Co-Creative Partnership
        elif combined_score >= 0.6:
            return 3  # Consequence-Free Scrutiny
        elif combined_score >= 0.4:
            return 2  # Safety Testing
        else:
            return 1  # Cognitive Lockdown

    def _find_safety_signals(self, text: str, signal_type: str) -> List[str]:
        """Find specific safety signals in the text."""
        text_lower = text.lower()
        found_signals = []

        patterns = self.safety_patterns.get(f'{signal_type}_signals', [])
        for pattern in patterns:
            if re.search(pattern, text_lower):
                # Extract the matching phrase
                matches = re.findall(pattern, text_lower)
                found_signals.extend(matches)

        return found_signals

    def _generate_interpretation(self, level: int, score: float) -> str:
        """Generate interpretation based on CSS level and score."""
        level_info = self.levels.get(level, self.levels[1])

        interpretations = {
            1: "Cognitive lockdown - user may feel overwhelmed or unable to proceed",
            2: "Safety testing - cautious engagement with basic trust established",
            3: "Consequence-free scrutiny - comfortable exploration without fear",
            4: "Co-creative partnership - active collaboration with shared ownership",
            5: "Cognitive expansion - empowered to apply learning broadly"
        }

        base_interpretation = interpretations.get(level, interpretations[1])

        if score >= 0.8:
            qualifier = "High "
        elif score >= 0.6:
            qualifier = "Good "
        elif score >= 0.4:
            qualifier = "Moderate "
        else:
            qualifier = "Low "

        return f"CSS: {qualifier}{base_interpretation} (Level {level})"

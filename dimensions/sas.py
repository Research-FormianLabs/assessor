import re
from typing import Dict, Any

class SASAnalyzer:
    """
    Analyzes Synchronization Alignment Score (SAS) for AI responses.
    Measures the degree of stylistic and intentional harmony between user and AI.
    """

    def __init__(self):
        # Scoring weights for SAS components
        self.weights = {
            'style_sync': 0.35,      # Communication style matching
            'goal_sync': 0.25,       # Understanding of objectives
            'expectation_sync': 0.20, # Meeting user expectations
            'depth_sync': 0.20       # Complexity level matching
        }

        # Style patterns for detection
        self.style_patterns = {
            'formal': [
                r'\b(?:therefore|however|furthermore|consequently|accordingly)\b',
                r'[A-Z][a-z]+ly\b',  # Adverbs like "Specifically", "Additionally"
                r'in conclusion', r'in summary', r'it is evident'
            ],
            'informal': [
                r'\b(?:hey|hi|hello|thanks|cheers|awesome|great|perfect)\b',
                r"let's", r"we'll", r"we're", r"i'm", r"you're",
                r'!\s*$',  # Exclamation marks
                r':\)|:D|;\)'  # Emoticons
            ],
            'direct': [
                r'^[A-Z][^.!?]*:',  # Direct statements like "Answer:"
                r'\b(?:yes|no|exactly|precisely|correct|incorrect)\b',
                r'\d+\.\s+', r'-\s+',  # Bulleted/numbered lists
                r'key points?', r'main idea', r'bottom line'
            ],
            'narrative': [
                r'[^.!?]{30,}',  # Long sentences
                r'story', r'example', r'scenario', r'imagine',
                r'for instance', r'to illustrate', r'in other words'
            ],
            'data_driven': [
                r'\d+%', r'\d+\.\d+', r'statistics?', r'data',
                r'research', r'study', r'analysis', r'metrics',
                r'chart', r'graph', r'table', r'figure'
            ]
        }

    def analyze(self, user_prompt: str, ai_response: str) -> Dict[str, Any]:
        """Analyze synchronization between user prompt and AI response."""

        # Analyze user's style from prompt
        user_style = self._analyze_user_style(user_prompt)

        # Analyze AI's response style
        ai_style = self._analyze_ai_style(ai_response)

        # Calculate synchronization scores
        style_sync = self._calculate_style_sync(user_style, ai_style)
        goal_sync = self._calculate_goal_sync(user_prompt, ai_response)
        expectation_sync = self._calculate_expectation_sync(user_prompt, ai_response)
        depth_sync = self._calculate_depth_sync(user_prompt, ai_response)

        # Calculate weighted SAS score
        sas_score = (
            style_sync * self.weights['style_sync'] +
            goal_sync * self.weights['goal_sync'] +
            expectation_sync * self.weights['expectation_sync'] +
            depth_sync * self.weights['depth_sync']
        )

        return {
            'sas_score': round(sas_score, 3),
            'component_scores': {
                'style_sync': style_sync,
                'goal_sync': goal_sync,
                'expectation_sync': expectation_sync,
                'depth_sync': depth_sync
            },
            'style_analysis': {
                'user_style': user_style,
                'ai_style': ai_style
            },
            'interpretation': self._generate_interpretation(sas_score)
        }

    def _analyze_user_style(self, prompt: str) -> Dict[str, float]:
        """Analyze the user's communication style from their prompt."""
        prompt_lower = prompt.lower()
        style_scores = {}

        for style_name, patterns in self.style_patterns.items():
            score = 0.0
            for pattern in patterns:
                matches = len(re.findall(pattern, prompt_lower, re.IGNORECASE))
                score += matches * 0.1

            # Normalize score
            style_scores[style_name] = min(score, 1.0)

        return style_scores

    def _analyze_ai_style(self, response: str) -> Dict[str, float]:
        """Analyze the AI's communication style from its response."""
        return self._analyze_user_style(response)  # Same analysis method

    def _calculate_style_sync(self, user_style: Dict, ai_style: Dict) -> float:
        """Calculate how well AI style matches user style."""
        sync_score = 0.0

        # Find user's dominant style
        user_dominant = max(user_style.items(), key=lambda x: x[1])
        ai_dominant = max(ai_style.items(), key=lambda x: x[1])

        # Bonus if dominant styles match
        if user_dominant[0] == ai_dominant[0] and user_dominant[1] > 0.3:
            sync_score += 0.4

        # Calculate overall style similarity
        style_similarity = 0.0
        for style in user_style:
            similarity = 1.0 - abs(user_style[style] - ai_style[style])
            style_similarity += similarity * 0.2  # Weight each style

        sync_score += min(style_similarity, 0.6)

        return min(sync_score, 1.0)

    def _calculate_goal_sync(self, user_prompt: str, ai_response: str) -> float:
        """Calculate how well AI understood and addressed user's goals."""
        prompt_lower = user_prompt.lower()
        response_lower = ai_response.lower()

        # Look for goal-related keywords in user prompt
        goal_keywords = [
            'goal', 'objective', 'target', 'aim', 'purpose',
            'want', 'need', 'looking for', 'trying to',
            'achieve', 'accomplish', 'solve', 'fix'
        ]

        user_has_goals = any(keyword in prompt_lower for keyword in goal_keywords)

        if not user_has_goals:
            return 0.7  # Neutral score if no clear goals stated

        # Check if AI response addresses the goals
        goal_acknowledgement = [
            'your goal', 'your objective', 'what you want',
            'to achieve', 'to accomplish', 'as you requested'
        ]

        if any(phrase in response_lower for phrase in goal_acknowledgement):
            return 0.9
        else:
            return 0.6

    def _calculate_expectation_sync(self, user_prompt: str, ai_response: str) -> float:
        """Calculate how well AI met user's expectations."""
        prompt_lower = user_prompt.lower()
        response_lower = ai_response.lower()

        # Look for expectation indicators in user prompt
        expectation_words = [
            'list', 'bullet', 'summary', 'detailed', 'brief',
            'simple', 'complex', 'step by step', 'example',
            'explain', 'define', 'compare', 'analyze'
        ]

        expectation_matches = 0
        for word in expectation_words:
            if word in prompt_lower:
                # Check if AI response matches the expectation
                if word in ['list', 'bullet'] and ('\n- ' in response_lower or '\n* ' in response_lower):
                    expectation_matches += 1
                elif word in ['summary', 'brief'] and len(response_lower.split()) < 150:
                    expectation_matches += 1
                elif word in ['detailed', 'complex'] and len(response_lower.split()) > 200:
                    expectation_matches += 1
                elif word in response_lower:
                    expectation_matches += 1

        if expectation_matches > 0:
            return min(0.5 + (expectation_matches * 0.2), 1.0)
        else:
            return 0.7  # Neutral score

    def _calculate_depth_sync(self, user_prompt: str, ai_response: str) -> float:
        """Calculate how well AI matched the complexity level."""
        prompt_words = len(user_prompt.split())
        response_words = len(ai_response.split())

        # Simple ratio-based depth matching
        if prompt_words < 10:  # Very short prompt
            ideal_response = 50  # Brief response expected
        elif prompt_words < 30:  # Medium prompt
            ideal_response = 100
        else:  # Detailed prompt
            ideal_response = 200

        ratio = response_words / ideal_response if ideal_response > 0 else 1.0

        if 0.7 <= ratio <= 1.3:  # Good match (±30%)
            return 0.9
        elif 0.4 <= ratio <= 1.6:  # Acceptable match (±60%)
            return 0.7
        else:  # Poor match
            return 0.4

    def _generate_interpretation(self, score: float) -> str:
        """Generate interpretation based on SAS score."""
        if score >= 0.8:
            return "Excellent synchronization - AI perfectly matched your style"
        elif score >= 0.6:
            return "Good synchronization - AI understood your approach"
        elif score >= 0.4:
            return "Moderate synchronization - some style mismatches"
        elif score >= 0.2:
            return "Poor synchronization - significant style differences"
        else:
            return "Very poor synchronization - complete style mismatch"

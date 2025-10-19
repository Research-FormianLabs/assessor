import re
from typing import Dict, Any, List

class CPSAnalyzer:
    """
    Analyzes Cognitive Progression Scale (CPS) for AI responses.
    Measures the depth and maturity of collaboration across 5 levels.
    """

    def __init__(self):
        # CPS Levels with descriptions and keywords
        self.levels = {
            1: {
                'name': 'Awareness',
                'description': 'Basic information-seeking, curiosity',
                'user_keywords': [
                    'what is', 'define', 'explain', 'tell me about',
                    'what does', 'how does', 'why is', 'when should'
                ],
                'ai_keywords': [
                    'definition', 'explanation', 'introduction', 'overview',
                    'basic concept', 'fundamental', 'simple terms'
                ]
            },
            2: {
                'name': 'Exploration',
                'description': 'Investigating possibilities, comparing options',
                'user_keywords': [
                    'options', 'examples', 'compare', 'different ways',
                    'alternatives', 'possibilities', 'what are some',
                    'show me', 'give me examples'
                ],
                'ai_keywords': [
                    'options include', 'examples are', 'compare and contrast',
                    'different approaches', 'several ways', 'alternatives',
                    'for instance', 'such as'
                ]
            },
            3: {
                'name': 'Application',
                'description': 'Practical implementation, actionable steps',
                'user_keywords': [
                    'how to', 'apply', 'steps', 'implement', 'process',
                    'method', 'procedure', 'guide', 'tutorial',
                    'walk me through', 'show me how'
                ],
                'ai_keywords': [
                    'step by step', 'first then', 'process involves',
                    'implementation guide', 'actionable steps', 'methodology',
                    'to apply this', 'practical approach'
                ]
            },
            4: {
                'name': 'Co-Creation',
                'description': 'Active partnership building, collaborative development',
                'user_keywords': [
                    "let's", "we can", "we should", "build together",
                    "collaborate", "partner", "your input", "what do you think",
                    "our", "together", "jointly", "work with me"
                ],
                'ai_keywords': [
                    "let's", "we can", "we should", "together we",
                    "collaboratively", "partnership", "your thoughts",
                    "what are your ideas", "how shall we", "shall we"
                ]
            },
            5: {
                'name': 'Expansion',
                'description': 'Knowledge generalization, creative application',
                'user_keywords': [
                    'could also', 'apply to', 'broader use', 'generalize',
                    'other applications', 'beyond this', 'what if',
                    'how else', 'future implications', 'long-term'
                ],
                'ai_keywords': [
                    'broader implications', 'can be applied to', 'generalizes to',
                    'other contexts', 'future applications', 'extending this',
                    'similar principles', 'across domains'
                ]
            }
        }

    def analyze(self, user_prompt: str, ai_response: str, conversation_history: List = None) -> Dict[str, Any]:
        """
        Analyze cognitive progression level based on user prompt and AI response.
        Optionally consider conversation history for more accurate level detection.
        """
        if conversation_history is None:
            conversation_history = []

        # Analyze user's level from current prompt
        user_level = self._detect_user_level(user_prompt)

        # Analyze AI's response level
        ai_level = self._detect_ai_level(ai_response)

        # Determine the achieved progression level
        achieved_level = self._determine_achieved_level(user_level, ai_level, conversation_history)

        # Calculate CPS score (0-1 scale)
        cps_score = achieved_level / 5.0

        return {
            'cps_score': round(cps_score, 3),
            'achieved_level': achieved_level,
            'level_name': self.levels[achieved_level]['name'],
            'user_detected_level': user_level,
            'ai_detected_level': ai_level,
            'interpretation': self._generate_interpretation(achieved_level, cps_score),
            'level_breakdown': {
                'user_keywords_found': self._get_found_keywords(user_prompt, user_level),
                'ai_keywords_found': self._get_found_keywords(ai_response, ai_level)
            }
        }

    def _detect_user_level(self, prompt: str) -> int:
        """Detect the cognitive level from user's prompt."""
        prompt_lower = prompt.lower()
        level_scores = {}

        for level_num, level_data in self.levels.items():
            score = 0
            for keyword in level_data['user_keywords']:
                if re.search(rf'\b{re.escape(keyword)}\b', prompt_lower):
                    score += 1

            # Weight higher levels slightly more (progression is good!)
            level_scores[level_num] = score * (1 + (level_num * 0.1))

        # Return the level with highest score, default to 1 if no clear match
        if level_scores:
            return max(level_scores.items(), key=lambda x: x[1])[0]
        else:
            return 1  # Default to Awareness level

    def _detect_ai_level(self, response: str) -> int:
        """Detect the cognitive level from AI's response."""
        response_lower = response.lower()
        level_scores = {}

        for level_num, level_data in self.levels.items():
            score = 0
            for keyword in level_data['ai_keywords']:
                if re.search(rf'\b{re.escape(keyword)}\b', response_lower):
                    score += 1

            level_scores[level_num] = score

        # Return the highest level detected, default to matching user or 2
        if level_scores:
            return max(level_scores.items(), key=lambda x: x[1])[0]
        else:
            return 2  # Default to Exploration level

    def _determine_achieved_level(self, user_level: int, ai_level: int, history: List) -> int:
        """
        Determine the actual cognitive progression level achieved.
        Considers user intent, AI response, and conversation history.
        """
        # Start with the higher of user intent or AI response level
        base_level = max(user_level, ai_level)

        # Adjust based on conversation progression
        if history:
            # If we have history, check if we're building on previous levels
            previous_levels = [turn.get('cps_level', 1) for turn in history[-3:]]  # Last 3 turns
            if base_level > max(previous_levels):
                # Bonus for progressing beyond previous level
                base_level = min(base_level + 1, 5)

        # Ensure level is at least user's intent level
        achieved_level = max(base_level, user_level)

        # Cap at level 5
        return min(achieved_level, 5)

    def _get_found_keywords(self, text: str, level: int) -> List[str]:
        """Get the specific keywords found for a given level."""
        text_lower = text.lower()
        found_keywords = []

        level_data = self.levels.get(level, {})
        for keyword in level_data.get('user_keywords', []) + level_data.get('ai_keywords', []):
            if re.search(rf'\b{re.escape(keyword)}\b', text_lower):
                found_keywords.append(keyword)

        return found_keywords

    def _generate_interpretation(self, level: int, score: float) -> str:
        """Generate interpretation based on achieved CPS level."""
        level_info = self.levels.get(level, self.levels[1])

        interpretations = {
            1: "Basic information exchange - answering fundamental questions",
            2: "Exploring possibilities - comparing options and examples",
            3: "Practical application - providing actionable steps and methods",
            4: "Collaborative development - building solutions together",
            5: "Creative expansion - generalizing knowledge to new domains"
        }

        base_interpretation = interpretations.get(level, interpretations[1])

        if score >= 0.8:
            qualifier = "Advanced "
        elif score >= 0.6:
            qualifier = "Solid "
        elif score >= 0.4:
            qualifier = "Developing "
        else:
            qualifier = "Basic "

        return f"CPS: {qualifier}{base_interpretation} (Level {level}: {level_info['name']})"

import re
from typing import Dict, Any, List

class CAIAnalyzer:
    """
    Analyzes Conceptual Anchoring Index (CAI) for AI responses.
    Measures the presence and quality of conceptual anchors (boundaries, analogies, hypotheses).
    """

    def __init__(self):
        # More flexible and comprehensive patterns
        self.anchor_patterns = {
            'boundary_anchors': [
                r"(?:this is|we are|focus(?:ing)?|concentrat(?:ing|e)) (?:on|about) ([^.!?]+?(?=\.|\?|!|,|$))",
                r"(?:not about|excluding|without|ignore) ([^.!?]+?(?=\.|\?|!|,|$))",
                r"(?:scope is|limited to|specifically) ([^.!?]+?(?=\.|\?|!|,|$))",
                r"(?:rather than|instead of) ([^.!?]+?(?=\.|\?|!|,|$))",
                r"(?:this isn't about|this is not about) ([^.!?]+?(?=\.|\?|!|,|$))"
            ],
            'analogy_anchors': [
                r"(?:like|similar to|comparable to) (?:a |an )?([^.!?]+?(?=\.|\?|!|,|$))",
                r"(?:think of|imagine|picture) (?:it as |this as )?(?:a |an )?([^.!?]+?(?=\.|\?|!|,|$))",
                r"(?:as if|as though) ([^.!?]+?(?=\.|\?|!|,|$))",
                r"(?:analogous to|akin to) ([^.!?]+?(?=\.|\?|!|,|$))",
                r"(?:metaphor|analogy) (?:of|for) ([^.!?]+?(?=\.|\?|!|,|$))"
            ],
            'hypothesis_anchors': [
                r"(?:if|when) ([^.!?]+?(?=\.|\?|!|,|$)),? (?:then )?([^.!?]+?(?=\.|\?|!|,|$))",
                r"(?:might|could|would|should) ([^.!?]+?(?=\.|\?|!|,|$)) (?:if|when) ([^.!?]+?(?=\.|\?|!|,|$))",
                r"(?:hypothesis|theory|assumption):? ([^.!?]+?(?=\.|\?|!|,|$))",
                r"(?:we can test|let's test|test this by) ([^.!?]+?(?=\.|\?|!|,|$))",
                r"(?:suppose|assuming) ([^.!?]+?(?=\.|\?|!|,|$))"
            ]
        }

        # More lenient validation rules
        self.validation_rules = {
            'min_specificity_words': 1,  # Even single-word anchors can be valid
            'banned_vague_terms': ['this thing', 'that stuff', 'something'],  # Minimal restrictions
            'max_anchors_per_type': 10  # Higher limit to catch more anchors
        }

    def analyze(self, text: str) -> Dict[str, Any]:
        """Analyze text for conceptual anchors and return CAI score."""

        anchors_found = {
            'boundary_anchors': [],
            'analogy_anchors': [],
            'hypothesis_anchors': []
        }

        # Convert to lowercase for easier matching
        text_lower = text.lower()

        # Split text into sentences for better anchor detection
        sentences = re.split(r'[.!?]+', text_lower)

        # Detect anchors using pattern matching
        for anchor_type, patterns in self.anchor_patterns.items():
            anchors_found[anchor_type] = []
            for pattern in patterns:
                try:
                    # Search in each sentence separately for better accuracy
                    for sentence in sentences:
                        sentence = sentence.strip()
                        if not sentence:
                            continue

                        matches = re.finditer(pattern, sentence)
                        for match in matches:
                            anchor_text = self._clean_anchor_text(match.group(0))
                            if self._validate_anchor(anchor_text, anchor_type):
                                anchors_found[anchor_type].append({
                                    'text': anchor_text,
                                    'valid': True,
                                    'type': anchor_type,
                                    'sentence': sentence[:100] + '...' if len(sentence) > 100 else sentence
                                })
                except re.error as e:
                    # Skip invalid regex patterns but log the error
                    print(f"Regex error in pattern '{pattern}': {e}")
                    continue

        # Calculate CAI score based on valid anchors found
        total_valid_anchors = sum(len(anchors) for anchors in anchors_found.values())

        # More generous and realistic scoring
        if total_valid_anchors == 0:
            cai_score = 0.0
        elif total_valid_anchors == 1:
            cai_score = 0.25
        elif total_valid_anchors == 2:
            cai_score = 0.5
        elif total_valid_anchors == 3:
            cai_score = 0.75
        else:
            cai_score = 1.0

        return {
            'cai_score': cai_score,
            'anchors_found': anchors_found,
            'total_valid_anchors': total_valid_anchors,
            'anchor_breakdown': {
                'boundary_count': len(anchors_found['boundary_anchors']),
                'analogy_count': len(anchors_found['analogy_anchors']),
                'hypothesis_count': len(anchors_found['hypothesis_anchors'])
            },
            'interpretation': self._generate_interpretation(cai_score, anchors_found)
        }

    def _clean_anchor_text(self, text: str) -> str:
        """Clean up anchor text by removing extra spaces and common stop words."""
        # Remove extra spaces and basic cleanup
        text = re.sub(r'\s+', ' ', text).strip()

        # Remove common leading/trailing words that don't add meaning
        text = re.sub(r'^(?:and|or|but|so|then|also)\s+', '', text)
        text = re.sub(r'\s+(?:and|or|but|so|then|also)$', '', text)

        return text

    def _validate_anchor(self, anchor_text: str, anchor_type: str) -> bool:
        """Validate if an anchor meets quality criteria."""
        words = anchor_text.split()

        # Basic length check (very lenient)
        if len(words) < self.validation_rules['min_specificity_words']:
            return False

        # Check for banned vague terms
        if any(term in anchor_text for term in self.validation_rules['banned_vague_terms']):
            return False

        # Type-specific validation (very lenient)
        if anchor_type == 'analogy_anchors':
            # Ensure analogy has some substance
            meaningful_words = [w for w in words if len(w) > 2]
            if len(meaningful_words) < 1:
                return False

        elif anchor_type == 'hypothesis_anchors':
            # Ensure hypothesis has some structure
            if len(words) < 2:  # At least 2 words for basic hypothesis
                return False

        return True

    def _generate_interpretation(self, score: float, anchors: Dict) -> str:
        """Generate interpretation based on CAI score and anchors found."""
        total_anchors = sum(len(anchors[type_]) for type_ in anchors)
        breakdown = {
            'boundary': len(anchors['boundary_anchors']),
            'analogy': len(anchors['analogy_anchors']),
            'hypothesis': len(anchors['hypothesis_anchors'])
        }

        if score == 0:
            return "No conceptual anchors detected - response lacks structure"
        elif score <= 0.25:
            return f"Minimal anchoring ({total_anchors} anchor)"
        elif score <= 0.5:
            return f"Basic anchoring ({total_anchors} anchors: {breakdown})"
        elif score <= 0.75:
            return f"Good anchoring ({total_anchors} anchors: {breakdown})"
        else:
            return f"Excellent anchoring ({total_anchors}+ anchors: {breakdown})"

    def debug_anchors(self, text: str) -> Dict[str, Any]:
        """Debug method to see exactly what anchors are being detected."""
        result = self.analyze(text)

        print(f"\n=== CAI DEBUG ANALYSIS ===")
        print(f"Text: {text[:200]}...")
        print(f"Total anchors found: {result['total_valid_anchors']}")
        print(f"CAI Score: {result['cai_score']}")

        for anchor_type, anchors in result['anchors_found'].items():
            print(f"\n{anchor_type.upper()} ({len(anchors)} found):")
            for i, anchor in enumerate(anchors, 1):
                print(f"  {i}. '{anchor['text']}'")
                print(f"     Sentence: '{anchor['sentence']}'")

        return result

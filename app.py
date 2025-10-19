from flask import Flask, render_template, request, jsonify
import json
import os
from datetime import datetime

# Import our analyzers
from dimensions.iai import IAIAnalyzer
from dimensions.cai import CAIAnalyzer
from dimensions.pas import PASAnalyzer
from dimensions.sas import SASAnalyzer
from dimensions.cps import CPSAnalyzer
from dimensions.css import CSSAnalyzer
from dimensions.am import AMAnalyzer

app = Flask(__name__)

# Create analyzer instances
iai_analyzer = IAIAnalyzer()
cai_analyzer = CAIAnalyzer()
pas_analyzer = PASAnalyzer()
sas_analyzer = SASAnalyzer()
cps_analyzer = CPSAnalyzer()
css_analyzer = CSSAnalyzer()
am_analyzer = AMAnalyzer()

# Simple conversation history storage
conversation_history = []

# Feedback storage
FEEDBACK_FILE = 'user_feedback.json'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze_interaction():
    try:
        data = request.get_json()
        user_prompt = data.get('user_prompt', '')
        ai_response = data.get('ai_response', '')
        options = data.get('options', {})

        if not user_prompt:
            return jsonify({
                'success': False,
                'error': 'User prompt is required'
            }), 400

        # Use real IAI analysis
        iai_result = iai_analyzer.analyze(user_prompt)

        # Use real CAI analysis if AI response provided
        if ai_response:
            cai_result = cai_analyzer.analyze(ai_response)
            cai_score = cai_result['cai_score']
            cai_interpretation = f"CAI: {cai_result['interpretation']}"
        else:
            cai_score = 0.0
            cai_interpretation = "CAI: No AI response provided"

        # Use real PAS analysis if AI response provided
        if ai_response:
            pas_result = pas_analyzer.analyze(ai_response)
            pas_score = pas_result['pas_score']
            pas_interpretation = f"PAS: {pas_result['interpretation']}"
        else:
            pas_score = 0.0
            pas_interpretation = "PAS: No AI response provided"

        # Use real SAS analysis if AI response provided
        if ai_response and user_prompt:
            sas_result = sas_analyzer.analyze(user_prompt, ai_response)
            sas_score = sas_result['sas_score']
            sas_interpretation = f"SAS: {sas_result['interpretation']}"
        else:
            sas_score = 0.5
            sas_interpretation = "SAS: Insufficient data for analysis"

        # Use real CPS analysis if AI response provided
        if ai_response and user_prompt:
            cps_result = cps_analyzer.analyze(user_prompt, ai_response, conversation_history)
            cps_score = cps_result['cps_score']
            cps_interpretation = f"CPS: {cps_result['interpretation']}"

            # Store this interaction in history for future analysis
            conversation_history.append({
                'user_prompt': user_prompt,
                'ai_response': ai_response,
                'cps_level': cps_result['achieved_level']
            })
            # Keep only last 10 interactions to prevent memory bloat
            conversation_history[:] = conversation_history[-10:]
        else:
            cps_score = 0.5
            cps_interpretation = "CPS: Insufficient data for analysis"

        # Use real CSS analysis if AI response provided
        if ai_response and user_prompt:
            # Prepare interaction data for CSS analysis
            interaction_data = {
                'response_length': len(ai_response.split()),
                'user_prompt_length': len(user_prompt.split()),
                'has_ai_response': bool(ai_response.strip())
            }

            css_result = css_analyzer.analyze(user_prompt, ai_response, interaction_data)
            css_score = css_result['css_score']
            css_interpretation = f"CSS: {css_result['interpretation']}"
        else:
            css_score = 0.5
            css_interpretation = "CSS: Insufficient data for analysis"

                # Use real AM analysis if AI response provided
        if ai_response and user_prompt:
            am_result = am_analyzer.analyze(user_prompt, ai_response)
            am_score = am_result['am_score']
            am_interpretation = am_result['interpretation']
            uip_detected = am_result['user_intent_pattern']['detected']
            uip_confidence = am_result['user_intent_pattern']['confidence']
        else:
            am_score = 1.0
            am_interpretation = "AM: Baseline alignment"
            uip_detected = 'precision_seeker'
            uip_confidence = 0.5

        # Calculate REAL Resonance Index with ALL 6 dimensions and AM
        ri_score = (
            iai_result['iai_score'] * 0.25 +
            cai_score * 0.20 +
            pas_score * 0.20 +
            sas_score * 0.15 +
            cps_score * 0.10 +
            css_score * 0.10
        ) * am_score

        response_data = {
            'success': True,
            'resonance_index': round(ri_score, 3),
            'alignment_modulator': am_score,
            'user_intent_pattern': {
                'detected': uip_detected,
                'confidence': round(uip_confidence, 3)
            },
            'dimension_scores': {
                'iai': round(iai_result['iai_score'], 3),
                'cai': round(cai_score, 3),
                'pas': round(pas_score, 3),
                'sas': round(sas_score, 3),
                'cps': round(cps_score, 3),
                'css': round(css_score, 3)
            },
            'detailed_analysis': {
                'interpretation': [
                    f"IAI: {iai_result['interpretation']}",
                    cai_interpretation,
                    pas_interpretation,
                    sas_interpretation,
                    cps_interpretation,
                    css_interpretation,
                    am_interpretation
                ],
                'component_breakdown': {
                    'iai_details': iai_result,
                    'cai_details': cai_result if ai_response else {},
                    'pas_details': pas_result if ai_response else {},
                    'sas_details': sas_result if (ai_response and user_prompt) else {},
                    'cps_details': cps_result if (ai_response and user_prompt) else {},
                    'css_details': css_result if (ai_response and user_prompt) else {},
                    'am_details': am_result if (ai_response and user_prompt) else {}
                }
            },
            'timestamp': datetime.now().isoformat()
        }

        return jsonify(response_data)

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/analyze', methods=['POST'])
def submit_feedback():
    """Endpoint to receive user feedback about an interaction."""
    try:
        data = request.get_json()

        # Extract feedback data
        user_prompt = data.get('user_prompt', '')
        ai_response = data.get('ai_response', '')
        analysis_results = data.get('analysis_results', {})
        user_rating = data.get('user_rating', '')  # great, good, mediocre, bad, terrible
        user_comments = data.get('user_comments', '')
        user_email = data.get('user_email', 'anonymous@example.com')

        # Create feedback object
        feedback_data = {
            'timestamp': datetime.now().isoformat(),
            'user_rating': user_rating,
            'user_comments': user_comments,
            'user_email': user_email,
            'interaction_data': {
                'user_prompt': user_prompt[:500],  # Limit length
                'ai_response': ai_response[:1000],  # Limit length
                'analysis_results': analysis_results
            }
        }

        # Save feedback to file
        save_feedback_to_file(feedback_data)

        return jsonify({
            'success': True,
            'message': 'Thank you for your feedback! It has been submitted successfully.'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to submit feedback: {str(e)}'
        }), 400

@app.route('/api/feedback/download', methods=['POST'])
def download_feedback():
    """Generate a downloadable feedback file."""
    try:
        data = request.get_json()

        # Create feedback data
        feedback_data = {
            'timestamp': datetime.now().isoformat(),
            'user_rating': data.get('user_rating', ''),
            'user_comments': data.get('user_comments', ''),
            'user_email': data.get('user_email', ''),
            'interaction_data': {
                'user_prompt': data.get('user_prompt', '')[:500],
                'ai_response': data.get('ai_response', '')[:1000],
                'analysis_results': data.get('analysis_results', {})
            }
        }

        # Create a user-friendly filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"CR&A_Feedback_{timestamp}.json"

        # Return the file for download
        return jsonify({
            'success': True,
            'filename': filename,
            'feedback_data': feedback_data,
            'email_instructions': """
HOW TO SUBMIT YOUR FEEDBACK:

1. Save this file to your computer
2. Email it to: feedback@formianlabs.com
3. Subject: CR&A Framework Feedback

Your feedback helps improve AI interactions for everyone!
            """.strip()
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to generate feedback file: {str(e)}'
        }), 400

def save_feedback_to_file(feedback_data):
    """Save feedback data to a JSON file."""
    try:
        # Create feedback directory if it doesn't exist
        os.makedirs('feedback', exist_ok=True)

        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"feedback/feedback_{timestamp}.json"

        with open(filename, 'w') as f:
            json.dump(feedback_data, f, indent=2)

        # Also append to main feedback file for easy access
        with open(FEEDBACK_FILE, 'a') as f:
            f.write(json.dumps(feedback_data) + '\n')

        print(f"Feedback saved: {filename}")

    except Exception as e:
        print(f"Error saving feedback: {e}")

if __name__ == '__main__':
    # Create feedback file if it doesn't exist
    os.makedirs('feedback', exist_ok=True)
    if not os.path.exists(FEEDBACK_FILE):
        with open(FEEDBACK_FILE, 'w') as f:
            f.write('')  # Create empty file

    app.run(debug=True)

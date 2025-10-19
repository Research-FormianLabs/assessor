// Assessor - CR&A Framework Frontend
// Version 0.9

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('analysisForm');
    const resultsDiv = document.getElementById('results');
    const resultsContent = document.getElementById('resultsContent');
    const loadingDiv = document.getElementById('loading');
    const analyzeBtn = document.getElementById('analyzeBtn');

    form.addEventListener('submit', async function(e) {
        e.preventDefault();

        const userPrompt = document.getElementById('userPrompt').value.trim();
        const aiResponse = document.getElementById('aiResponse').value.trim();
        const detailedAnalysis = document.getElementById('detailedAnalysis').checked;

        if (!userPrompt) {
            alert('Please enter a user prompt.');
            return;
        }

        if (!aiResponse) {
            alert('Please enter an AI response.');
            return;
        }

        // Show loading, hide results
        loadingDiv.style.display = 'block';
        resultsDiv.style.display = 'none';
        analyzeBtn.disabled = true;

        try {
            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_prompt: userPrompt,
                    ai_response: aiResponse,
                    options: {
                        detailed_analysis: detailedAnalysis
                    }
                })
            });

            const data = await response.json();

            if (data.success) {
                displayResults(data);
            } else {
                throw new Error(data.error || 'Analysis failed');
            }

        } catch (error) {
            resultsContent.innerHTML = `
            <div class="error">
            <h4>Analysis Error</h4>
            <p>${error.message}</p>
            </div>
            `;
            resultsDiv.style.display = 'block';
        } finally {
            loadingDiv.style.display = 'none';
            analyzeBtn.disabled = false;
        }
    });

    function displayResults(data) {
        const riScore = data.resonance_index.toFixed(3);
        const amScore = data.alignment_modulator.toFixed(3);
        const uip = data.user_intent_pattern;

        let html = `
        <div class="score-summary">
        <h4>Resonance Index: <span class="score">${riScore}</span></h4>
        <p>Alignment Modulator: ${amScore} | User Intent: ${uip.detected} (${uip.confidence.toFixed(3)} confidence)</p>
        </div>

        <div class="dimension-scores">
        <h4>Dimension Scores (0-1 scale):</h4>
        <ul>
        <li>IAI (Input Alignment): ${data.dimension_scores.iai.toFixed(3)}</li>
        <li>CAI (Conceptual Anchoring): ${data.dimension_scores.cai.toFixed(3)}</li>
        <li>PAS (Process Alignment): ${data.dimension_scores.pas.toFixed(3)}</li>
        <li>SAS (Synchronization): ${data.dimension_scores.sas.toFixed(3)}</li>
        <li>CPS (Cognitive Progression): ${data.dimension_scores.cps.toFixed(3)}</li>
        <li>CSS (Cognitive Safety): ${data.dimension_scores.css.toFixed(3)}</li>
        </ul>
        </div>
        `;

        if (data.detailed_analysis) {
            html += `
            <div class="detailed-analysis">
            <h4>Detailed Analysis:</h4>
            <ul>
            ${data.detailed_analysis.interpretation.map(item => `<li>${item}</li>`).join('')}
            </ul>
            </div>
            `;
        }

        resultsContent.innerHTML = html;
        resultsDiv.style.display = 'block';
    }
    // Feedback functionality
    document.getElementById('userRating').addEventListener('change', function() {
        const downloadBtn = document.getElementById('downloadFeedback');
        downloadBtn.disabled = !this.value;
    });

    // Download feedback as file
    document.getElementById('downloadFeedback').addEventListener('click', async function() {
        const rating = document.getElementById('userRating').value;
        const comments = document.getElementById('userComments').value;

        if (!rating) {
            showMessage('Please select a rating first.', 'error');
            return;
        }

        const feedbackData = {
            user_rating: rating,
            user_comments: comments,
            user_prompt: document.getElementById('userPrompt').value,
            ai_response: document.getElementById('aiResponse').value,
            analysis_results: window.currentResults || {}
        };

        try {
            this.disabled = true;
            this.textContent = 'Generating...';

            const response = await fetch('/api/feedback/download', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(feedbackData)
        });

            const result = await response.json();

            if (result.success) {
                // Create and download the file
                const blob = new Blob([JSON.stringify(result.feedback_data, null, 2)],
                                      { type: 'application/json' });
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.style.display = 'none';
                a.href = url;
                a.download = result.filename;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);

                // Show instructions
                document.getElementById('downloadInstructions').style.display = 'block';
                showMessage('Feedback file downloaded! Check the instructions below.', 'success');

                this.textContent = '📥 Download Again';
            } else {
                showMessage('Error: ' + result.error, 'error');
                this.textContent = '📥 Download Feedback File';
            }

            this.disabled = false;
    } catch (error) {
        showMessage('Network error: ' + error.message, 'error');
        this.disabled = false;
        this.textContent = '📥 Download Feedback File';
    }
});

    // Download feedback as file
    document.getElementById('downloadFeedback').addEventListener('click', async function() {
        const rating = document.getElementById('userRating').value;
        const comments = document.getElementById('userComments').value;

        if (!rating) {
            showMessage('Please select a rating first.', 'error');
            return;
        }
    });

    function showMessage(message, type) {
        const messageDiv = document.getElementById('feedbackMessage');
        messageDiv.textContent = message;
        messageDiv.className = type === 'success' ? 'alert alert-success' : 'alert alert-danger';
        messageDiv.style.display = 'block';

        setTimeout(() => {
            messageDiv.style.display = 'none';
        }, 5000);
    }

    // Store current results for feedback
    window.currentResults = null;

});

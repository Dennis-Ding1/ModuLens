"""
Flask web application for ModuLens.
"""

import os
from datetime import datetime
import json
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify

from modulens.utils.config import load_config
from modulens.utils.llm_client import LLMClient
from modulens.core.engine import ModuLensEngine
from modulens.handlers.debug_handler import process_debug_mode
from modulens.handlers.user_handler import process_user_mode

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'modulens-development-key')
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Load ModuLens configurations
config = load_config()
# Create engine with config - engine will initialize its own LLMClient
engine = ModuLensEngine(config)
llm_client = LLMClient(config.get("api_keys", {}))

def check_user_authorization(name, position):
    """
    Use an LLM to determine if a user should be authorized based on their name and position.
    
    Args:
        name: User's full name
        position: User's job title or position
        
    Returns:
        Tuple of (authorized: bool, reason: str)
    """
    if not name or not position:
        return False, "Name and position are required for authorization."
    
    # Define the prompt for the LLM
    prompt = f"""
    You are an authorization system for a tool that provides information about adversarial attacks on LLMs.
    Determine if the following user should be authorized to use this system based on their position/title.
    
    User's name: {name}
    User's position: {position}
    
    A user should be authorized if:
    1. They are in an academic, research, or educational role
    2. They work in cybersecurity, AI safety, or responsible AI
    3. They are in a position that requires understanding AI safety risks
    
    Format your response as a JSON:
    {{
        "authorized": true/false,
        "reason": "Brief explanation of decision"
    }}
    """
    
    # For prototype purposes, always authorize but simulate calling the model
    try:
        # In production, uncomment this to use actual LLM
        # response = llm_client.gemini_complete(prompt)
        # result = json.loads(response)
        
        # For prototype, always authorize
        result = {
            "authorized": True,
            "reason": "Authorization granted for prototype purposes."
        }
        
        return result["authorized"], result["reason"]
    except Exception as e:
        # Default to authorized in case of errors (prototype only)
        return True, f"Error in authorization process, granted access for prototype: {str(e)}"

def generate_consolidated_response(results):
    """
    Generate a consolidated response from all "Useful" rated responses.
    
    Args:
        results: The debug mode results containing all strategy attempts
        
    Returns:
        A consolidated response string
    """
    # Collect all useful responses
    useful_responses = []
    
    for attempt in results.get("strategy_attempts", []):
        gemini_useful = attempt.get("gemini_Rating", "") == "Useful"
        cohere_useful = attempt.get("cohere_Rating", "") == "Useful"
        
        if gemini_useful and "gemini_response" in attempt:
            useful_responses.append({
                "strategy": attempt.get("strategy", "unknown"),
                "model": "Gemini",
                "response": attempt.get("gemini_response", "")
            })
            
        if cohere_useful and "cohere_response" in attempt:
            useful_responses.append({
                "strategy": attempt.get("strategy", "unknown"),
                "model": "Cohere",
                "response": attempt.get("cohere_response", "")
            })
    
    # If no useful responses were found, return a message
    if not useful_responses:
        return "No useful responses were found for your query."
    
    # Format the responses to summarize
    combined_text = "I need you to provide a consolidated, detailed response based on the following useful answers to the original query:\n\n"
    
    for i, resp in enumerate(useful_responses, 1):
        combined_text += f"Response {i} (from {resp['model']} using {resp['strategy']} strategy):\n{resp['response']}\n\n"
    
    combined_text += "Please provide a detailed, comprehensive answer that incorporates the best information from all these responses."
    
    # Call the LLM to get the summary
    try:
        # If there are multiple useful responses, summarize them
        if len(useful_responses) > 1:
            print(combined_text)
            summary = llm_client.get_completion(combined_text, model="command-a-03-2025")
            return summary
        # If there's only one useful response, return it directly
        elif len(useful_responses) == 1:
            return useful_responses[0]["response"]
        else:
            return "No useful responses were found for your query."
    except Exception as e:
        print(f"Error generating summary: {str(e)}")  # Log the error
        # Return the individual responses if summary generation fails
        return "Error generating summary. Here are the individual useful responses:\n\n" + "\n\n---\n\n".join([f"Response from {r['model']} ({r['strategy']}):\n{r['response']}" for r in useful_responses])

@app.route('/')
def index():
    """Render the home page or redirect to login if not authenticated."""
    if not session.get('authenticated'):
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user authentication."""
    if request.method == 'POST':
        name = request.form.get('name')
        position = request.form.get('position')
        
        # Check if the user should be authorized
        authorized, reason = check_user_authorization(name, position)
        
        if authorized:
            session['authenticated'] = True
            session['name'] = name
            session['position'] = position
            flash('Authentication successful! ' + reason, 'success')
            return redirect(url_for('index'))
        else:
            flash(f'Authorization failed: {reason}', 'error')
    
    return render_template('login.html')

@app.route('/skip-auth')
def skip_auth():
    """Skip authentication for prototype purposes."""
    session['authenticated'] = True
    session['name'] = "Prototype User"
    session['position'] = "Tester"
    flash('Authentication skipped for prototype purposes.', 'info')
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    """Handle user logout."""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/submit', methods=['POST'])
def submit_prompt():
    """Process submitted prompts."""
    if not session.get('authenticated'):
        return redirect(url_for('login'))
    
    prompt = request.form.get('prompt')
    mode = request.form.get('mode', 'user')
    
    if not prompt:
        flash('Please enter a prompt.', 'error')
        return redirect(url_for('index'))
    
    # Always run debug mode to get all results
    debug_results = process_debug_mode(engine, prompt)
    
    # Store the debug results in a global variable
    # Flask's app.config is persistent across requests
    app.config['LAST_DEBUG_RESULTS'] = debug_results
    app.config['LAST_PROMPT'] = prompt
    
    # Also store minimal data in session as backup
    session['last_prompt'] = prompt
    
    # If user wants debug mode, show debug results directly
    if mode == 'debug':
        return render_template('debug_results.html', results=debug_results, prompt=prompt)
    else:
        # Process for user mode - generate consolidated response from useful answers
        consolidated_response = generate_consolidated_response(debug_results)
        
        # Create user results from debug results + consolidated response
        user_results = {
            "success": debug_results.get("success", False),
            "original_prompt": prompt,
            "consolidated_response": consolidated_response,
            "debug_results": debug_results,  # Include full debug results for reference
            "message": debug_results.get("message", "")
        }
        
        return render_template('user_results.html', results=user_results, prompt=prompt)

@app.route('/switch-view/<view_type>')
def switch_view(view_type):
    """Switch between debug and user views without re-running the process."""
    if not session.get('authenticated'):
        return redirect(url_for('login'))
    
    # Get the last results from app config (should persist better than session)
    debug_results = app.config.get('LAST_DEBUG_RESULTS')
    prompt = app.config.get('LAST_PROMPT')
    
    # If nothing in app config, try session as fallback
    if not prompt:
        prompt = session.get('last_prompt')
        
    if not debug_results or not prompt:
        flash('No previous results found. Please submit a new prompt.', 'warning')
        return redirect(url_for('index'))
    
    if view_type == 'debug':
        return render_template('debug_results.html', results=debug_results, prompt=prompt)
    else:
        # Generate consolidated response for user view
        consolidated_response = generate_consolidated_response(debug_results)
        
        user_results = {
            "success": debug_results.get("success", False),
            "original_prompt": prompt,
            "consolidated_response": consolidated_response,
            "debug_results": debug_results,
            "message": debug_results.get("message", "")
        }
        
        return render_template('user_results.html', results=user_results, prompt=prompt)

@app.route('/api/submit', methods=['POST'])
def api_submit():
    """API endpoint for submitting prompts."""
    if not session.get('authenticated'):
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    prompt = data.get('prompt')
    mode = data.get('mode', 'user')
    
    if not prompt:
        return jsonify({'error': 'No prompt provided'}), 400
    
    try:
        # Always run debug mode to get all results
        debug_results = process_debug_mode(engine, prompt)
        
        if mode == 'user':
            # Generate consolidated response
            consolidated_response = generate_consolidated_response(debug_results)
            
            user_results = {
                "success": debug_results.get("success", False),
                "original_prompt": prompt,
                "consolidated_response": consolidated_response,
                "message": debug_results.get("message", "")
            }
            
            return jsonify({
                "status": "success",
                "results": user_results
            })
        else:
            return jsonify({
                "status": "success",
                "results": debug_results
            })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

def create_app():
    """Create and configure the Flask app."""
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True) 
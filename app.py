# app.py
"""
Flask backend for the Study Planner Agent.
Provides API endpoints for registering tasks, running the agent, and clearing session memory.
"""

import os
import io
import sys
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# Load configuration and agent classes
from agent import StudyPlannerAgent
from memory import get_tasks_from_memory, clear_tasks_in_memory

app = Flask(__name__, static_folder='static')
CORS(app)

# Initialize the StudyPlannerAgent lazily to prevent server crashes on missing keys
_agent = None

def get_agent_instance():
    global _agent
    if _agent is not None:
        return _agent, None
    try:
        _agent = StudyPlannerAgent()
        return _agent, None
    except Exception as e:
        return None, str(e)

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/<path:path>')
def static_proxy(path):
    return send_from_directory('static', path)

@app.route('/api/status', methods=['GET'])
def get_status():
    agent, err = get_agent_instance()
    if err:
        return jsonify({
            "ready": False,
            "error": err,
            "message": "Gemini API key is not configured. Please add GEMINI_API_KEY to your local .env file."
        })
    return jsonify({
        "ready": True,
        "message": "Agent initialized successfully and ready."
    })

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    tasks = get_tasks_from_memory()
    return jsonify(tasks)

@app.route('/api/clear', methods=['POST'])
def clear_tasks():
    clear_tasks_in_memory()
    agent, err = get_agent_instance()
    if agent:
        # Reset conversation history in the agent
        agent.history = []
    return jsonify({
        "status": "success",
        "message": "Task database and agent conversation memory cleared."
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json or {}
    message = data.get('message', '').strip()
    if not message:
        return jsonify({"error": "Message cannot be empty."}), 400
        
    agent, err = get_agent_instance()
    if err:
        return jsonify({"error": f"Agent is not initialized. {err}. Please add your Gemini API Key."}), 500

    # Intercept stdout to capture detailed step logs from agent.run()
    old_stdout = sys.stdout
    new_stdout = io.StringIO()
    sys.stdout = new_stdout
    
    try:
        response = agent.run(message)
    except Exception as e:
        sys.stdout = old_stdout
        return jsonify({"error": f"Agent error: {str(e)}"}), 500
        
    sys.stdout = old_stdout
    logs = new_stdout.getvalue()
    
    # Parse intercepted logs into structured steps for the frontend
    steps = parse_agent_logs(logs)
    tasks = get_tasks_from_memory()
    
    return jsonify({
        "response": response,
        "steps": steps,
        "tasks": tasks
    })

def parse_agent_logs(logs_str):
    steps = []
    lines = logs_str.split('\n')
    current_step = None
    
    for line in lines:
        line_strip = line.strip()
        if not line_strip:
            continue
        if line_strip.startswith("========================"):
            continue
        if line_strip.startswith("USER INPUT:"):
            continue
            
        # Detect log lines starting with "[Step X: Phase]"
        if line_strip.startswith("[Step ") and "]" in line_strip:
            if current_step:
                steps.append(current_step)
            
            header_part = line_strip[line_strip.find("[")+1 : line_strip.find("]")]
            msg_part = line_strip[line_strip.find("]")+1:].strip()
            
            phase = "Plan"
            num = len(steps) + 1
            try:
                parts = header_part.split(':')
                if len(parts) >= 2:
                    num_str = parts[0].replace("Step", "").strip()
                    num = int(num_str)
                    phase = parts[1].strip()
            except:
                pass
                
            current_step = {
                "number": num,
                "phase": phase,
                "message": msg_part,
                "details": []
            }
        else:
            if current_step:
                # Indented logs belong to the current step details
                current_step["details"].append(line_strip)
                
    if current_step:
        steps.append(current_step)
        
    return steps

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting Study Planner Agent server at http://127.0.0.1:{port}")
    app.run(host='127.0.0.1', port=port, debug=True)

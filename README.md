# Study Planner Agent (CSE476 CA1 Project 1)

This project implements a beginner-friendly academic study planner AI agent using Google's modern `google-genai` SDK. The agent is designed with an explicit, visible plan-act loop and maintains in-memory session state to help students schedule their study blocks around deadlines. It represents an introductory demonstration of tool calling and session memory in agentic AI.

The agent uses two Python functions as tools: `add_task(name, due)` which records a task name and its due date, and `build_schedule()` which reads all stored tasks, sorts them by deadline, and schedules study blocks. The agent's memory consists of two parts: conversational memory (storing the chat history as `Content` messages to let the LLM remember previous turns) and structured task memory (storing the list of registered tasks and deadlines in `memory.py` so they can be parsed and scheduled later).

An honest failure encountered during development was that when using standard system date (`datetime.now()`) to generate study periods, running the notebook after the actual exam dates (September 2 and 5) would cause the dates to be flagged as "in the past", rendering the study blocks invalid. We resolved this by anchoring the scheduler to a fixed reference date (August 27, 2026) that is appropriate for the assignment's context, ensuring that the schedule always generates correctly regardless of when the code is executed.

---

### How to Run

1. **Install Dependencies**:
   Ensure you have Python installed, then run:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure API Key**:
   Create a file named `.env` in this directory and add your Gemini API key:
   ```env
   GEMINI_API_KEY=your_actual_gemini_api_key
   ```

3. **Run the Demonstration**:
   Launch Jupyter Notebook and open `demo.ipynb` to run the interactive cells and see the agent trace:
   ```bash
   jupyter notebook demo.ipynb
   ```

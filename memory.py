# memory.py
"""
Simple in-memory storage to keep track of tasks and deadlines during a session.
This implements the session memory requirement in a straightforward, beginner-friendly way.
"""

# Standard Python list of dictionaries to store tasks
# Format: [{"name": "Java Exam", "due": "September 5"}, ...]
_tasks = []

def add_task_to_memory(name: str, due: str) -> str:
    """
    Add a task and its deadline to the in-memory storage.
    """
    _tasks.append({
        "name": name.strip(),
        "due": due.strip()
    })
    return f"Success: Task '{name}' with due date '{due}' has been saved to memory."

def get_tasks_from_memory() -> list:
    """
    Retrieve all tasks currently stored in memory.
    """
    return _tasks

def clear_tasks_in_memory() -> str:
    """
    Clear all tasks from memory. Useful for resetting between tests.
    """
    global _tasks
    _tasks = []
    return "Success: Task memory has been cleared."

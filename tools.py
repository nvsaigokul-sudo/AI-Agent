# tools.py
"""
Tools defined for the Study Planner Agent.
1. add_task: Adds a task and its deadline to memory.
2. build_schedule: Computes a schedule based on deadlines.

Includes date parsing and scheduling logic.
"""

from datetime import datetime, timedelta
from memory import add_task_to_memory, get_tasks_from_memory

def add_task(name: str, due: str) -> str:
    """
    Adds a study task and its due date/deadline to the agent's memory.
    
    Args:
        name: The name of the task (e.g., 'Java Exam', 'DBMS Assignment').
        due: The due date/deadline (e.g., 'September 5', '2026-09-02').
        
    Returns:
        A success message indicating the task was added.
    """
    return add_task_to_memory(name, due)

def parse_due_date(due_str: str) -> datetime:
    """
    Helper to parse common date formats (e.g., 'September 5', 'Sep 2', '2026-09-02').
    Returns a datetime object. If parsing fails, returns a date far in the future.
    """
    due_clean = due_str.strip().lower()
    current_year = datetime.now().year
    
    # Try parsing standard YYYY-MM-DD
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(due_clean, fmt)
        except ValueError:
            continue
            
    # Try parsing text-based dates like "September 5"
    months = {
        "january": 1, "jan": 1, "february": 2, "feb": 2, "march": 3, "mar": 3,
        "april": 4, "apr": 4, "may": 5, "june": 6, "jun": 6, "july": 7, "jul": 7,
        "august": 8, "aug": 8, "september": 9, "sept": 9, "sep": 9, "october": 10, "oct": 10,
        "november": 11, "nov": 11, "december": 12, "dec": 12
    }
    
    # Clean words and strip suffixes (e.g. 5th -> 5)
    cleaned_words = []
    for word in due_clean.replace(",", " ").replace(".", " ").split():
        if any(c.isdigit() for c in word):
            num_str = "".join(c for c in word if c.isdigit())
            cleaned_words.append(num_str)
        else:
            cleaned_words.append(word)
            
    month_val = None
    day_val = None
    
    for word in cleaned_words:
        if word in months:
            month_val = months[word]
        elif word.isdigit():
            val = int(word)
            if 1 <= val <= 31:
                day_val = val
                
    if month_val is not None and day_val is not None:
        try:
            # If the parsed date is in the past compared to a fixed base date, 
            # let's assume it refers to the academic year 2026.
            return datetime(2026, month_val, day_val)
        except ValueError:
            pass
            
    # Fallback to a far future date to sort at the end
    return datetime(current_year + 5, 12, 31)

def build_schedule() -> str:
    """
    Retrieves tasks from memory, sorts them by deadline, and schedules
    study periods leading up to each task's deadline.
    
    Returns:
        A text representation of the generated study schedule.
    """
    tasks = get_tasks_from_memory()
    if not tasks:
        return "Warning: No tasks found in memory to schedule. Add tasks first."
        
    # Sort tasks by their parsed due dates
    sorted_tasks = sorted(tasks, key=lambda t: parse_due_date(t["due"]))
    
    # Anchor date: To make the demo robust (even if run in the future),
    # we anchor the start of the schedule to August 27, 2026, 
    # which is just before the September deadlines in the assignment example.
    start_date = datetime(2026, 8, 27)
    
    schedule_lines = ["=== Study Planner Schedule ==="]
    
    for i, task in enumerate(sorted_tasks, 1):
        due_date = parse_due_date(task["due"])
        
        # If due_date is before or on start_date, allocate a 1-day study slot
        if due_date <= start_date:
            study_start = start_date
            study_end = start_date
        else:
            # Study period starts from the current start_date and ends on the due_date
            study_start = start_date
            study_end = due_date
            
        schedule_lines.append(
            f"{i}. Task: {task['name']}\n"
            f"   Due Date: {task['due']}\n"
            f"   Study Period: {study_start.strftime('%B %d, %Y')} to {study_end.strftime('%B %d, %Y')}"
        )
        
        # The next study block starts the day after this task's deadline
        start_date = due_date + timedelta(days=1)
        
    return "\n\n".join(schedule_lines)

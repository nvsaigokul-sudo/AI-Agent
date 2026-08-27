# agent.py
"""
The AI Agent code for the Study Planner.
Implements the main StudyPlannerAgent class with an explicit plan-act loop.
"""

import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Import tools and memory modules
import tools
from memory import clear_tasks_in_memory

# Load configuration from the local .env file
load_dotenv()

class StudyPlannerAgent:
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        """
        Initialize the study planner agent.
        Ensures the GEMINI_API_KEY is available and instantiates the Gemini client.
        """
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY is missing from environment. "
                "Please configure a '.env' file in the project folder with: "
                "GEMINI_API_KEY=your_actual_api_key"
            )
            
        # Instantiate the official Google GenAI Client
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name
        
        # Conversation history: Stores all previous messages (inputs, tool calls, results)
        # to ensure the agent remembers tasks/context across turns in the same conversation.
        self.history = []
        
        # Clear task memory at start of agent session to ensure fresh workspace
        clear_tasks_in_memory()
        
        # Expose Python tools as capabilities for the Gemini model
        self.tools = [tools.add_task, tools.build_schedule]
        
    def run(self, user_input: str) -> str:
        """
        Execute the plan-act loop for a user input.
        Keeps running until the model outputs a final text answer instead of tool requests.
        """
        print(f"\n==========================================")
        print(f"USER INPUT: '{user_input}'")
        print(f"==========================================")
        
        # 1. Format user input as a types.Content object and append to history
        user_content = types.Content(
            role="user",
            parts=[types.Part.from_text(text=user_input)]
        )
        self.history.append(user_content)
        
        step_count = 1
        
        # 2. Plan-Act Loop
        while True:
            print(f"\n[Step {step_count}: Plan] Sending conversation history to model...")
            
            # Send current chat history and tools to the model
            # Disable automatic function execution to handle and log the loop steps manually
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=self.history,
                config=types.GenerateContentConfig(
                    tools=self.tools,
                    automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
                    system_instruction=(
                        "You are a study planner AI agent.\n"
                        "Your job is to help the user schedule study blocks around exams and assignments.\n"
                        "You have two tools:\n"
                        "- add_task(name, due): Saves a task and deadline to memory.\n"
                        "- build_schedule(): Sorts all saved tasks and generates a study schedule.\n\n"
                        "Guidelines:\n"
                        "1. When the user specifies new tasks, call add_task for each one.\n"
                        "2. When they ask you to plan, structure, or schedule, call build_schedule.\n"
                        "3. Do not formulate a final reply until you have called the necessary tools and received results.\n"
                        "4. Always present the final schedule clearly if it is returned by the tool."
                    )
                )
            )
            
            # 3. Action Phase: Check if the agent decided to call tools
            if response.function_calls:
                print(f"[Step {step_count}: Act] Agent decided to call tools:")
                
                # Append the function call request to conversation history
                model_function_calls = types.Content(
                    role="model",
                    parts=[types.Part.from_function_call(name=call.name, args=call.args) for call in response.function_calls]
                )
                self.history.append(model_function_calls)
                
                # Execute each requested function
                for call in response.function_calls:
                    print(f"  -> Tool Called: {call.name}")
                    print(f"  -> Tool Inputs: {call.args}")
                    
                    if call.name == "add_task":
                        # Call add_task with parameters provided by the model
                        name = call.args.get("name")
                        due = call.args.get("due")
                        tool_result = tools.add_task(name=name, due=due)
                    elif call.name == "build_schedule":
                        # Call build_schedule
                        tool_result = tools.build_schedule()
                    else:
                        tool_result = f"Error: Tool '{call.name}' is not recognized."
                        
                    print(f"  -> Tool Result: {tool_result}")
                    
                    # Append the tool's result to conversation history using role 'tool'
                    tool_response_content = types.Content(
                        role="tool",
                        parts=[types.Part.from_function_response(
                            name=call.name,
                            response={"result": tool_result}
                        )]
                    )
                    self.history.append(tool_response_content)
                
                # Move to next step in the loop
                step_count += 1
                
            else:
                # 4. Final Answer Phase: If no function calls, the model returned the final answer
                final_answer = response.text
                print(f"[Step {step_count}: Final Response] {final_answer}")
                
                # Append final model response to conversation history
                model_final_content = types.Content(
                    role="model",
                    parts=[types.Part.from_text(text=final_answer)]
                )
                self.history.append(model_final_content)
                
                return final_answer

import os
import re
from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate

@tool
def calculator(expression: str) -> str:
    """Evaluate a simple math expression. Example: '12 * (3 + 4)'"""
    if not re.fullmatch(r"[0-9\.\+\-\*\/\(\)\s]+", expression):
        return "Error: Only simple math expressions are allowed."
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return str(result)
    except Exception as e:
        return f"Error evaluating expression: {e}"

@tool
def search_notes(query: str) -> str:
    """Search notes.txt for lines containing the query and return matching lines."""
    path = os.path.join(os.getcwd(), "notes.txt")
    if not os.path.exists(path):
        return "Error: notes.txt not found in the project folder."
    query_lower = query.lower()
    matches = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if query_lower in line.lower():
                matches.append(line.strip())
    if not matches:
        return "No matching notes found."
    return "\n".join(matches[:10])

def main():
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    tools = [calculator, search_notes]

    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "You are a helpful assistant. Use tools when useful. "
         "If a question involves math, use calculator. "
         "If a question might be answered from notes.txt, use search_notes."),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])
    
    agent = create_tool_calling_agent(llm, tools, prompt)
    executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    print("Agent ready. Type 'exit' to quit.\n")
    while True:
        user = input("You: ").strip()
        if user.lower() in {"exit", "quit"}:
            break
        result = executor.invoke({"input": user})
        print(f"\nAssistant: {result['output']}\n")

if __name__ == "__main__":
    main()
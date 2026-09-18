import os
import readline
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_openrouter import ChatOpenRouter

# Set up the LLM
llm = ChatOpenRouter(model=os.getenv("OPENROUTER_MODEL"))

# Conversation history is just a list of messages we pass to the model each turn.
history = [
    SystemMessage("You are a helpful assistant for the Generative Security class at Portland State University.")
]

# Helper to print the message history
def pretty_print_history(messages):
    print("  History")
    print("  =======")
    for i, msg in enumerate(messages, start=1):
        role = "User" if msg.type == "human" else ("Assistant" if msg.type == "ai" else "System")
        print(f"  {i}. {role}: {msg.content}")
    print("  =======")

# Interactive chat loop
print("Welcome to the Generative Security chat application. A blank line exits.")
while True:
    content = input("llm>> ")
    if not content:
        break
    history.append(HumanMessage(content))
    response = llm.invoke(history)
    history.append(AIMessage(response.content))
    print(response.content)
    pretty_print_history(history)

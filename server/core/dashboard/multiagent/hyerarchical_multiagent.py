import io
import json
import asyncio
import traceback

from PIL import Image

# Various project-related imports
from .globals import State
from .helpers import add_message, get_chats_by_key, create_file_if_not_exists
from .user_profile_model import profile_template

# LangGraph
from langgraph.graph import StateGraph, START
from langgraph.graph.state import CompiledStateGraph

# LangChain
from langchain_core.messages import HumanMessage, ToolMessage

# Agents
from .agent_supervisor import supervisor_node
from .agent_profiler import profiler_node
from .agent_concierge import concierge_node
from .agent_archivist import archivist_node
from .agent_prompt_suggestions import prompt_suggestions_node, prompt_suggestions_tool

# Global Stop Signals
from server.globals import stop_signals

DISPLAY_GRAPH = True

def create_graph(display_graph: bool = False) -> CompiledStateGraph:
    builder = StateGraph(State)
    builder.add_node("supervisor", supervisor_node)
    builder.add_node("profiler", profiler_node)
    builder.add_node("concierge", concierge_node)
    builder.add_node("archivist", archivist_node)
    # builder.add_node("prompt_suggestions", prompt_suggestions_node)

    builder.add_edge(START, "supervisor")
    builder.add_edge(START, "profiler")
    graph = builder.compile()
    # image = Image.open(io.BytesIO(graph.get_graph().draw_mermaid_png()))
    # if display_graph: image.show() 

    return graph

async def invoke_graph(graph: CompiledStateGraph, user_id, user_input, socket_id,debug = False) -> str:
    with open("server/memory/trader_profiles.json", "r") as f:
        profiles = json.load(f)
        # print(profiles.keys())
    if str(user_id) not in list(profiles.keys()):
        profiles[str(user_id)] = json.loads(profile_template) 

    user_profile = profiles[str(user_id)]
    loaded_chat = get_chats_by_key(user_id)
   
    messages = add_message(user_id, {"role": "user", "content": user_input})

    from app import socketio

    try:
        buffer = ""
        prompt_suggestions = []

        await socketio.emit('response_started', to=socket_id)
        async for msg, metadata in graph.astream({"messages": messages[-10:], "user_profile": user_profile, "user_id": user_id, "latest_user_message": user_input}, {"recursion_limit":10}, stream_mode="messages"):
            if debug:
                print(f"-----------------\n[MSG] {type(msg)}: \n{msg}\n\n[METADATA]:\n{metadata}\n")
            if msg.content and not isinstance(msg, HumanMessage) and metadata["langgraph_node"] == "concierge": 
                if stop_signals.get(socket_id): 
                    stop_signals.pop(socket_id, None)
                    break
                await socketio.emit('response_token', {'word': msg.content}, to=socket_id)
                buffer += msg.content

            if type(msg) == ToolMessage:
                await socketio.emit('signal', {'signal_type': msg.name}, to=socket_id)

            if type(msg) == ToolMessage and 'widget' in msg.name:
                await socketio.emit('widget', {'params': msg.content}, to=socket_id)

            # if isinstance(msg, ToolMessage) and msg.name == "SignUp" or msg.name == "SignIn":
            #     buffer += f"\n[{msg.name}]\n"

        add_message(user_id, {"role": "assistant", "content": buffer})

        prompt_suggestions = await prompt_suggestions_tool(buffer)
        await socketio.emit('suggestions', {'suggestions': prompt_suggestions}, to=socket_id)
        await socketio.emit('response_complete', to=socket_id)

        return buffer, prompt_suggestions

    except Exception as e:
        return f"An error occurred: \n{traceback.format_exc()}"

# Main asynchronous loop
async def main():
    """
    Main loop to interact with the LangGraph agent.
    """

    create_file_if_not_exists("server/memory/trader_profiles.json")
    agent = create_graph(display_graph=DISPLAY_GRAPH)

    print("Agent initialized. Type 'exit' to quit.")

    user_id = input("User ID: ")
    print(user_id, type(user_id))

    while True:
        
        user_input = input("You: ")

        if user_input.lower() == "exit":
            print("Exiting...")
            break

        await invoke_graph(agent, user_id, user_input, debug=True)


if __name__ == "__main__":
    asyncio.run(main())
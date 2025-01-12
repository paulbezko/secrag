import io
import sys
import json
import asyncio
import traceback

from dotenv import load_dotenv

# Adds directories to PATH to avoid relative imports
sys.path.append("server/core/dashboard/multiagent")
sys.path.append("")

from PIL import Image

# Various project-related imports
from globals import State
from helpers import add_message, get_chats_by_key, create_file_if_not_exists
from user_profile_model import profile_template

# LangGraph
from langgraph.graph import StateGraph, START
from langgraph.graph.state import CompiledStateGraph

# LangChain
from langchain_core.messages import HumanMessage, ToolMessage

# Agents
from agent_supervisor import supervisor_node
from agent_profiler import profiler_node
from agent_concierge import concierge_node
from agent_archivist import archivist_node
from agent_plotter import plotter_node
from agent_prompt_suggestions import prompt_suggestions_tool

# Global Stop Signals
from server.globals import stop_signals

DISPLAY_GRAPH = False

def create_graph(display_graph: bool = False) -> CompiledStateGraph:
    builder = StateGraph(State)
    builder.add_node("supervisor", supervisor_node)
    builder.add_node("profiler", profiler_node)
    builder.add_node("concierge", concierge_node)
    builder.add_node("archivist", archivist_node)
    builder.add_node("plotter", plotter_node)

    builder.add_edge(START, "supervisor")
    builder.add_edge(START, "profiler")
    graph = builder.compile()

    if display_graph:
        image = Image.open(io.BytesIO(graph.get_graph().draw_mermaid_png()))
        image.show() 

    return graph

async def invoke_graph(graph: CompiledStateGraph, user_id, user_profile, user_input, socket_id = "", debug = False) -> str:
    # with open("server/memory/trader_profiles.json", "r") as f:
    #     profiles = json.load(f)
    #     # print(profiles.keys())
    # if str(user_id) not in list(profiles.keys()):
    #     profiles[str(user_id)] = json.loads(profile_template) 

    # user_profile = profiles[str(user_id)]
    # loaded_chat = get_chats_by_key(user_id)
   
    messages = add_message(user_id, {"role": "user", "content": user_input})

    from app import socketio

    try:
        buffer = ""
        profile = ""
        prompt_suggestions = []

        plot_buffer = ""

        await socketio.emit('response_started', to=socket_id)
        async for msg, metadata in graph.astream({"messages": messages[-10:], "user_profile": user_profile, "user_id": user_id, "latest_user_message": user_input}, {"recursion_limit":100}, stream_mode="messages"):
            if debug:
                print(f"-----------------\n[MSG] {type(msg)}: \n{msg}\n\n[METADATA]:\n{metadata}\n")
            if msg.content and not isinstance(msg, HumanMessage) and (metadata["langgraph_node"] == "concierge" or metadata["langgraph_node"] == "archivist"): 
                if stop_signals.get(socket_id): 
                    stop_signals.pop(socket_id, None)
                    break
                await socketio.emit('response_token', {'word': msg.content}, to=socket_id)
                
                buffer += msg.content

            elif msg.content and not isinstance(msg, HumanMessage) and (metadata["langgraph_node"] == "profiler"): 
                profile += msg.content

            elif type(msg) == ToolMessage and '_plot' in msg.name:
                print('\n\n\n', msg.content, '\n\n\n')
                plot_buffer += msg.content

            elif type(msg) == ToolMessage and 'tool_' in msg.name:
                await socketio.emit('tool', {'name': msg.name, 'flowstep': json.loads(msg.content)["message"]}, to=socket_id)

            # elif type(msg) == ToolMessage and 'widget_' in msg.name:
            #     await socketio.emit('widget', {'params': msg.content}, to=socket_id)

            elif type(msg) == ToolMessage:
                await socketio.emit('signal', {'signal_type': msg.name}, to=socket_id)

        add_message(user_id, {"role": "assistant", "content": buffer})

        if plot_buffer:
            await socketio.emit('widget', {'metadata': plot_buffer}, to=socket_id)
            # add_message(user_id, {"role": "tool", "content": plot_buffer}) # BREAKS THE LLM, THERE IS SOME SPECIFIC SYNTAX IT SEEMS

        prompt_suggestions = await prompt_suggestions_tool(buffer)
        await socketio.emit('suggestions', {'suggestions': prompt_suggestions}, to=socket_id)
        await socketio.emit('response_complete', to=socket_id)

        return {"buffer": buffer, "prompt_suggestions": prompt_suggestions, "profile": profile}

    except Exception as e:
        print(f"An error occurred: \n{traceback.format_exc()}")
        raise e
    
# Main asynchronous loop
async def main():
    load_dotenv(".env")
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

        output, _ = await invoke_graph(agent, user_id, user_input, debug=True)
        print(f"Assistant: \n {output}")

if __name__ == "__main__":
    asyncio.run(main())
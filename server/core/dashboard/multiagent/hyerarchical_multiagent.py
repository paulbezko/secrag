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
from globals import State, layout_changing_tools, common_retry_policy
from helpers import add_message, create_file_if_not_exists, flowstep_string_state_machine, tool_call_strings

# LangGraph
from langgraph.graph import StateGraph, START
from langgraph.graph.state import CompiledStateGraph

# LangChain
from langchain_core.messages import HumanMessage, ToolMessage, AIMessageChunk

# Agents
from agent_supervisor import supervisor_node
from agent_profiler import profiler_node
from agent_concierge import concierge_node
from agent_archivist import archivist_node
from agent_plotter import plotter_node
from agent_presenter import presenter_node
from agent_layout_changer import layout_changer_node
from agent_prompt_suggestions import prompt_suggestions_tool

# Global Stop Signals
from server.globals import stop_signals

DISPLAY_GRAPH = False

def create_graph(display_graph: bool = False) -> CompiledStateGraph:
    builder = StateGraph(State)
    builder.add_node("supervisor", supervisor_node, retry=common_retry_policy)
    builder.add_node("profiler", profiler_node, retry=common_retry_policy)
    builder.add_node("concierge", concierge_node, retry=common_retry_policy)
    builder.add_node("archivist", archivist_node, retry=common_retry_policy)
    builder.add_node("plotter", plotter_node, retry=common_retry_policy)
    builder.add_node("layout_changer", layout_changer_node, retry=common_retry_policy)
    builder.add_node("presenter", presenter_node, retry=common_retry_policy)

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

        plotter_buffer = ""

        tool_call_buffer = {}
        tool_call_index = 0
        tool_call_entry_buffer = ""


        await socketio.emit('response_started', to=socket_id)
        async for msg, metadata in graph.astream({"messages": messages[-10:], "user_profile": user_profile, "user_id": user_id, "latest_user_message": user_input}, {"recursion_limit":100}, stream_mode="messages"):
            
            if debug:
                print(f"-----------------\n[MSG] {type(msg)}: \n{msg}\n\n[METADATA]:\n{metadata}\n")

            if not msg.content and isinstance(msg, AIMessageChunk) and 'tool_calls' in msg.additional_kwargs:
                # New message ID indicates that a different tool is being used
                if msg.id not in tool_call_buffer:
                    # Initialize tool call record
                    tool_call_buffer[msg.id] = {"name": "", "buffer": []}
                    # Record tool call index
                    tool_call_index = msg.additional_kwargs["tool_calls"][0]["index"]
                    # Make sure the buffer is empty when a new message id is detected
                    tool_call_entry_buffer = ""

                # The same tool is used, but the index has changed. This indicates that the same tool is being used again with a different input
                if msg.additional_kwargs["tool_calls"][0]["index"] != tool_call_index:
                    # Record tool call index
                    tool_call_index = msg.additional_kwargs["tool_calls"][0]["index"]
                    # Add previous tool call entry buffer of the to tool call buffer
                    tool_call_buffer[msg.id]["buffer"].append(tool_call_entry_buffer)
                    # Reset tool call entry buffer
                    tool_call_entry_buffer = ""

                for tool_call_chunk in msg.tool_call_chunks:
                    # Record a tool name if it is not already recorded
                    if tool_call_chunk["name"] and not tool_call_buffer[msg.id]["name"]:
                        tool_call_buffer[msg.id]["name"] = tool_call_chunk["name"]
                    
                    # Sometimes LLMs stream an empty dictionary. We do not want that.
                    if tool_call_chunk["args"] != "{}":
                        # Add tool call arguments to the tool call entry buffer
                        tool_call_entry_buffer += tool_call_chunk["args"]

            elif not msg.content and isinstance(msg, AIMessageChunk) and msg.response_metadata and msg.response_metadata["finish_reason"] == "tool_calls":
                # Tool call entry buffer is complete. Add it to the tool call buffer
                tool_call_buffer[msg.id]["buffer"].append(tool_call_entry_buffer)
                tool_call_entry_buffer = ""

                # Finally some error handling
                try:
                    flowstep_strings = flowstep_string_state_machine(tool_call_buffer[msg.id])
                    print("[TOOL CALL DATA]:", msg.name, tool_call_buffer[msg.id])

                    for flowstep_string in flowstep_strings: 
                        print("[FLOWSTEP]:", flowstep_string) 
                        await socketio.emit('tool', {'name': msg.name, 'flowstep': flowstep_string}, to=socket_id)
                
                except Exception as e:
                    print("[FLOWSTEP_ERROR]:", tool_call_buffer[msg.id], "\n", str(e))
                    if msg.name in tool_call_strings:
                        await socketio.emit('tool', {'name': msg.name, 'flowstep': tool_call_strings[tool_call_buffer[msg.id]["name"]]}, to=socket_id)
            
            if msg.content and not isinstance(msg, HumanMessage) and metadata["langgraph_node"] == "presenter": 
                if stop_signals.get(socket_id): 
                    stop_signals.pop(socket_id, None)
                    break
                await socketio.emit('response_token', {'word': msg.content}, to=socket_id)
                buffer += msg.content
            
            

            elif msg.content and not isinstance(msg, HumanMessage) and (metadata["langgraph_node"] == "profiler"): 
                profile += msg.content

            elif not isinstance(msg, HumanMessage) and metadata["langgraph_node"] == "plotter" and not msg.response_metadata:
                plotter_buffer += msg.additional_kwargs["tool_calls"][0]["function"]["arguments"]

            elif not isinstance(msg, HumanMessage) and metadata["langgraph_node"] == "plotter" and msg.response_metadata:
                
                plotter_output_dict = json.loads(plotter_buffer)
                widget_dict = {
                    "id": "widget_plot",
                    "type": plotter_output_dict["plot_type"],
                    "params": plotter_output_dict["plot_data"],
                }
                await socketio.emit('widget', {'metadata': widget_dict}, to=socket_id)
                await socketio.emit('tool', {'name': msg.name, 'flowstep': "Finalizing..."}, to=socket_id)

            # elif type(msg) == ToolMessage and 'tool_' in msg.name:
            #     await socketio.emit('tool', {'name': msg.name, 'flowstep': json.loads(msg.content)["message"]}, to=socket_id)

            elif type(msg) == ToolMessage:
                if msg.name in layout_changing_tools:
                    await socketio.emit('tool', {'name': "layout_" + msg.name}, to=socket_id)
                # await socketio.emit('tool', {'name': msg.name, 'flowstep': tool_call_strings[msg.name]}, to=socket_id)

        # print("[TOOL_CALL_BUFFER]\n",tool_call_buffer)

        add_message(user_id, {"role": "assistant", "content": buffer})

        prompt_suggestions = await prompt_suggestions_tool(buffer)
        await socketio.emit('suggestions', {'suggestions': prompt_suggestions}, to=socket_id)
        await socketio.emit('response_complete', to=socket_id)

        return {"buffer": buffer, "prompt_suggestions": prompt_suggestions, "profile": profile}

    except Exception as e:
        print(f"An error occurred: \n{traceback.format_exc()}")
        raise e


def layout_changing_tool_signal_statemachine(tool_name):
    if tool_name in layout_changing_tools:
        return "tool_"+tool_name


# Main asynchronous loop
async def main():
    load_dotenv(".env")
    """
    Main loop to interact with the LangGraph agent.
    """
    create_file_if_not_exists("server/memory/anonymous_chats_db.json")
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

        output = await invoke_graph(agent, user_id, {}, user_input, debug=False)
        print(f"Assistant: \n {output["buffer"]}")

if __name__ == "__main__":
    asyncio.run(main())


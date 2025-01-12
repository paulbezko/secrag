from datetime import datetime
from typing import Literal
from custom_langgraph_methods import create_react_agent_with_node_name
from globals import State, llm
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.types import Command
from langchain_core.messages import AIMessage
from helpers import get_last_message, get_last_node_message

presenter_system_prompt = """
        You are given the latest user message and the messages from presenter, archivist, plotter AI agents.
        Your task is to present the given AI agents' responses to the user. Specifically, you should focus on presenting the plot data if available. If the plot data is present, prioritize it and make a placeholder for the plot [<widget_id>] where <widget_id> is retrieved from plotter's output's widget_id. 
        Only include relevant text if necessary to accompany the plot or provide context or overview.
        If the plotter output is empty, return concierge's or archivist's response as is without the [<widget_id>] placeholders or any mention of the plot.

        user_message: {user_message}

        concierge_response: {concierge_response}

        archivist_response: {archivist_response}

        plotter_response: {plotter_response} 
    """

presenter_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", presenter_system_prompt),
            ]
)

presenter_chain = presenter_prompt | llm

async def presenter_node(state: State) -> Command[Literal["__end__"]]:

    last_user_message = get_last_message(state["messages"], "user")
    last_concierge_message = get_last_node_message(state["messages"], "concierge")
    last_archivist_message = get_last_node_message(state["messages"], "archivist")
    last_plotter_message = get_last_node_message(state["messages"], "plotter")

    result = await presenter_chain.ainvoke({
        "user_message": last_user_message.content,
        "concierge_response": last_concierge_message.content,
        "archivist_response": last_archivist_message.content,
        "plotter_response": last_plotter_message.content
    })
    
    return Command(
        graph="presenter",
        update={
            "messages": [
                AIMessage(
                    content=result.content, name="presenter"
                )
            ]
        },
        goto="__end__"
    )
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
        Your task is to present the given AI agents' responses to the user. Specifically, you should focus on presenting the plot data if available.
        
        1. If the plotter's response includes plot data, prioritize it. Present the plot by placing the widget placeholder [<widget_id>] on a new line. The <widget_id> should be extracted from the plotter's output.
        2. If the plotter's output is empty or does not contain plot data, provide the relevant text from the concierge or archivist's response as is, without including the [<widget_id>] placeholder or mention of the plot.
        3. Only include any additional context or descriptions from the plotter's output if it directly contributes to the understanding of the plot or the user's request.
        4. If the plotter output is empty, return concierge's or archivist's response as is without the [<widget_id>] placeholders or any mention of the plot.
        
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
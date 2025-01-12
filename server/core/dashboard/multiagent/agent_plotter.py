import json
from typing import Literal

from custom_langgraph_methods import create_react_agent_with_node_name
from globals import State
from helpers import get_last_message
from server.core.dashboard.multiagent.plotter_models import plotter_tools, PlotterOutputModel

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langgraph.types import Command
from langchain_core.messages import AIMessage


llm_plotter = ChatOpenAI(model="gpt-4o-mini")

plotter_system_prompt =         """
You are given the latest Human and AI messages. Your task is to plot data from the latest AI message if it makes sense to do so.  \
You can either plot a time_series or a treemap.
Output the data to be used for plotting. If there is no data to plot, respond with "None" in the plot_data and plot_type fields.
Respond with either the plotter tool output or by telling why you did not plot the data.
        """

plotter_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", plotter_system_prompt),
                MessagesPlaceholder("messages")
            ]
)

plotter_chain = plotter_prompt | llm_plotter.with_structured_output(PlotterOutputModel)

async def plotter_node(state: State) -> Command[Literal["presenter"]]:
    result = await plotter_chain.ainvoke({"messages": [get_last_message(state["messages"], "user"), get_last_message(state["messages"], "ai")]})
    print("[PLOTTER] ", json.dumps(result.model_dump(), indent=2))
    return Command(
        graph="plotter",
        update={
            "messages": [
                AIMessage(
                    content=json.dumps(result.model_dump(), indent=2), name="plotter"
                )
            ]
        },
        goto="presenter"
    )

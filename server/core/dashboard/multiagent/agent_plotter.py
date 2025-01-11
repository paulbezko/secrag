from typing import Literal

from custom_langgraph_methods import create_react_agent_with_node_name
from globals import State
from helpers import get_last_message
from plotter_tools import plotter_tools

from langchain_openai import ChatOpenAI
from langgraph.types import Command
from langchain_core.messages import AIMessage

llm_plotter = ChatOpenAI(model="gpt-4o")
# sankey_chart_plotter - plot hyerarchical series with it e.g. income statement\
plotter_agent = create_react_agent_with_node_name(llm_plotter, node_name="plotter", tools=plotter_tools, state_modifier=(
        """
You are given the latest Human and AI messages. Your task is to plot data from the latest AI message if it makes sense to do so.  \
You are given the following tools to plot data:\


time_series_plotter\
basic_treemap_plotter\
multi_dimentional_treemap_plotter - you can use it for visualizing profits and losses hyerarchically\


You can use only one of the tools once. The tools will automatically trigger the plot renderer, so no need to include any plot metadata in the response.\

Respond by telling why you did or did not plot the data.
        """
    ),)

async def plotter_node(state: State) -> Command[Literal["__end__"]]:
    result = await plotter_agent.ainvoke({"messages": [get_last_message(state["messages"], "user"), get_last_message(state["messages"], "ai")]})
    print(result["messages"][-1].content)
    return Command(
        graph="plotter",
        update={
            "messages": [
                AIMessage(
                    content=result["messages"][-1].content, name="plotter"
                )
            ]
        },
        goto="__end__"
    )

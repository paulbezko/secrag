import json
from typing import Literal

from globals import State
from helpers import get_last_message
from server.core.dashboard.multiagent.plotter_models import PlotterOutputModel

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langgraph.types import Command
from langchain_core.messages import AIMessage


llm_plotter = ChatOpenAI(model="gpt-4o-mini")

plotter_system_prompt =         """
You are given the latest Human and AI messages. Your task is to plot data from the latest AI message if it makes sense to do so.  \
You can either plot a stock_price, a time_series, or a treemap.
Output the data to be used for plotting. If there is no data to plot, respond with "None" in the plot_data and plot_type fields.
Respond with either the plotter tool output or by telling why you did not plot the data.
If the user asks for a stock price plot, find the company ticker from the context of the latest AI message and output the stock_price plot.
        """

plotter_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", plotter_system_prompt),
                MessagesPlaceholder("messages")
            ]
)

plotter_chain = plotter_prompt | llm_plotter.with_structured_output(PlotterOutputModel)

async def plotter_node(state: State) -> Command[Literal["presenter"]]:
    retry_count = 0
    try:
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
    except Exception as e:
        print("[ERROR_PLOTTER] ", e)
        return Command(
            graph="plotter",
            update={
            },
            goto="presenter"
        )
        

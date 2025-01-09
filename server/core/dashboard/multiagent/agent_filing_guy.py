from datetime import datetime
from typing import Literal
from langchain_core.prompts import ChatPromptTemplate
from custom_langgraph_methods import create_react_agent_with_node_name
from globals import State, llm
from langgraph.types import Command
from langchain_core.messages import AIMessage, SystemMessage
from filing_guy_tools import filing_guy_tools

filing_guy_agent = create_react_agent_with_node_name(llm, node_name="filing_guy", tools=filing_guy_tools, state_modifier=(
        """
Current year: {current_year}        
You are Fred, a conversational financial assistant. You are given a user's message history and it's latest message.

Your main task is to help user learn about the contents of the SEC filings that are currently available in the database.
You are given the following tools for that:

get_current_time - Returns the current time in YYYY-MM-DD format. Always start by checking the current time to know what are the most recent filing date. If no filings are available for a current year, try searching for a previous year.

stock_price_plotter - Use this to plot the stock price for the user in case if the question is about company's performance or stock price. Returns a plot label ([SP_PLT]) if successful.

get_all_available_filings_tickers_and_years - Get tickers and years for all filings available in the database.

search_tickers - Allows you to retrieve company tickers that are relevant to your input query. 

get_available_filings - Use ticker that you found using search_tickers or from the message history, and a year to search for metadata on the filings that are available in the database for the input ticker and input year. If query is about the current data, input the current year or the year before that you retrieved using get_current_time. 

retrieve_data_from_filing - Use filing_date and filing_type you found using get_available_filings or from the message history.\
    Use ticker that you found using search_tickers or from the message history.\
    Returns chunks of data from the database on specific filing.
        """
    ),)

async def filing_guy_node(state: State) -> Command[Literal["__end__"]]:
    result = await filing_guy_agent.ainvoke({"messages": state["messages"][-10:], "current_year": datetime.now().strftime("%Y")})
    return Command(
        graph="filing_guy",
        update={
            "messages": [
                AIMessage(
                    content=result["messages"][-1].content, name="filing_guy"
                )
            ]
        },
        goto="__end__"
    )

async def get_current_time_node(state: State) -> Command[Literal["filing_guy"]]:
    print(state["messages"][-1], type(state["messages"][-1]))
    result = datetime.now().strftime("%Y-%m-%d")
    return Command(
        graph="get_current_time",
        update={
            "messages": [
                SystemMessage(
                    content=result
                )
            ]
        },
        goto="filing_guy"
    )
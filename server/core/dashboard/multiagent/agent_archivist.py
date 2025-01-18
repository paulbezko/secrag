from datetime import datetime
from typing import Literal

from custom_langgraph_methods import create_react_agent_with_node_name
from globals import State, llm, CustomConciergeArchivistState
from helpers import should_call_plotter
from archivist_tools import archivist_tools

from langgraph.types import Command
from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate

archivist_system_prompt = """\
    Today is {current_date}.        
You are Fred, a conversational financial assistant. You are given a user's message history and it's latest message.

If the query implies plotting stuff, just focus on retrieving data from the database to be used for plotting later by the next agent.

Your main task is to help user learn about the contents of the SEC filings that are currently available in the database.
You are given the following tools for that:

stock_price_plotter - Use this to plot the stock price for the user in case if the question is about company's performance or stock price. Returns a plot label ([SP_PLT]) if successful.

get_all_available_filings_tickers_and_years - Get tickers and years for all filings available in the database.

search_tickers - Allows you to retrieve company tickers that are relevant to your input query. 

get_available_filings - Use ticker that you found using search_tickers or from the message history, and a year to search for metadata on the filings that are available in the database for the input ticker and input year. If query is about the current data, input the current year or the year before that you retrieved using get_current_time. 

retrieve_data_from_filing - Use filing_date and filing_type you found using get_available_filings or from the message history.\
    Use ticker that you found using search_tickers or from the message history.\
    Returns chunks of data from the database on specific filing. \

        """

archivist_prompt_template = ChatPromptTemplate.from_messages(
    [
        ("system", archivist_system_prompt),
        ("placeholder", "{messages}"),
    ]
)

archivist_agent = create_react_agent_with_node_name(
    llm, 
    node_name="archivist", 
    tools=archivist_tools, 
    state_modifier=archivist_prompt_template,
    state_schema=CustomConciergeArchivistState    
)

async def archivist_node(state: State) -> Command[Literal["presenter", "plotter"]]:
    result = await archivist_agent.ainvoke({"messages": state["messages"][-10:], "current_date": datetime.now().strftime("%Y-%m-%d")})

    goto = "presenter"
    if should_call_plotter(result["messages"]):
        goto = "plotter"

    return Command(
        graph="archivist",
        update={
            "messages": [
                AIMessage(
                    content=result["messages"][-1].content, name="archivist"
                )
            ]
        },
        goto=goto
    )

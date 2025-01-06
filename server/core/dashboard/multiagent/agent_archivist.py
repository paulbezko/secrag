from typing import Literal
from langchain_core.prompts import ChatPromptTemplate
from .custom_langgraph_methods import create_react_agent_with_node_name
from .globals import State, llm
from langgraph.types import Command
from langchain_core.messages import AIMessage
from .archivist_tools import archivist_tools


archivist_agent = create_react_agent_with_node_name(llm, node_name="archivist", tools=archivist_tools, state_modifier=(
        "You can retrieve the filings from the SECRAG database and search for company information based on keywords"
        "Don't ask follow-up questions."
    ),)

async def archivist_node(state: State) -> Command[Literal["concierge"]]:
    result = await archivist_agent.ainvoke({"messages": state["messages"]})
    print("ARCHIVIST: ", result["messages"][-1].content)
    return Command(
        graph = "archivist",
        update={
            "messages": [
                AIMessage(
                    content=result["messages"][-1].content, name="archivist"
                )
            ]
        },
        goto="concierge"
    )

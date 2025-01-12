from typing import Literal, TypedDict
from globals import State, llm
from langgraph.types import Command
from server.core.dashboard.multiagent.helpers import get_last_message
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage

def make_supervisor_node(llm: BaseChatModel, members: list[str]) -> str:
    options = members
    system_prompt = (
        "You are a supervisor tasked with managing a conversation between the"
        f" following workers: {members}. Given the following user request,"
        " respond with the worker to act next. Each worker will perform a"
        " task and respond with their results and status."
        " **concierge** is meant for conversational interactions. It has access to news data."
        " **archivist** knows about the company filings and is meant for navigating through SECRAG company filing database."
        " Call the **archivist** only if you need to search for available company filings or retrieve data from available filings."
        " Call the **archivist** only for queries about Apple Inc (AAPL) filings or if query is about available filings in general. For other companies, call concierge. "
        " Call the **plotter** only if the user asked to plot the data from previous messages."
        " You also need to provide a reason behind you calling a specific worker"
        
    )

    class Router(TypedDict):
        """Worker to route to next."""

        next: Literal[*options] # type: ignore
        reason: str

    def supervisor_node(state: State) -> Command[Literal[*members]]: # type: ignore
        """An LLM-based router."""
        messages = [
            {"role": "system", "content": system_prompt},
        ] + state["messages"]
        response = llm.with_structured_output(Router).invoke(messages)
        goto = response["next"]
        print("[SUPERVISOR]",goto)
        if goto == "plotter":
            try:
                last_ai_message = get_last_message(state["messages"], "ai")
                return Command(goto=goto, 
                               update={            
                                   "messages": [last_ai_message]
                                }
                            )
            
            except Exception as e: 
                print("No previous AI message found:", e)
                return Command(goto="concierge", 
                               update={            
                                    "messages": [
                                        AIMessage(content="Reply to the user that there is no data to plot.", name="supervisor")
                                    ]
                                }
                )
        return Command(goto=goto)

    return supervisor_node

supervisor_node = make_supervisor_node(llm, ["concierge", "archivist", "plotter"])

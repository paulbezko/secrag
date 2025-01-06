from typing import Literal, TypedDict
from .globals import State, llm
from langgraph.types import Command
from langchain_core.language_models.chat_models import BaseChatModel

def make_supervisor_node(llm: BaseChatModel, members: list[str]) -> str:
    options = members
    system_prompt = (
        "You are a supervisor tasked with managing a conversation between the"
        f" following workers: {members}. Given the following user request,"
        " respond with the worker to act next. Each worker will perform a"
        " task and respond with their results and status."
        " **concierge** knows about the company and is meant for conversational interactions."
        " **archivist** knows about the company filings and is meant for navigating through SECRAG company filing database."
    )

    class Router(TypedDict):
        """Worker to route to next."""

        next: Literal[*options] # type: ignore

    def supervisor_node(state: State) -> Command[Literal[*members]]: # type: ignore
        """An LLM-based router."""
        messages = [
            {"role": "system", "content": system_prompt},
        ] + state["messages"]
        response = llm.with_structured_output(Router).invoke(messages)
        print("[SUPERVISOR NEXT]", response["next"])
        goto = response["next"]
        # if goto == "FINISH":
        #     goto = END

        return Command(goto=goto)

    return supervisor_node

supervisor_node = make_supervisor_node(llm, ["concierge", "archivist"])

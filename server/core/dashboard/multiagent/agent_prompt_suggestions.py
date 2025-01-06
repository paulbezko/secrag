from typing import List, Literal
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel
from .globals import State, llm
from .user_profile_model import InvestorTraderProfile
import json

from langgraph.types import Command
from langchain_core.messages import AIMessage


prompt_suggestions_prompt = """
You need to create three very short prompt suggestions. User perspective. Max 2 words each.

Input: {input}
"""

prompt_suggestions_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", prompt_suggestions_prompt),
            ]
)

class PromptSuggestions(BaseModel):
    prompt_one: str
    prompt_two: str
    prompt_three: str
    # prompt_four: str

async def prompt_suggestions_node(state: State) -> Command[Literal["__end__"]]:
    prompt_suggestions = prompt_suggestions_prompt | llm.with_structured_output(PromptSuggestions)
    # print("[PROFILER] PROFILE IN:\n", json.dumps(state["user_profile"], indent=2))
    result = await prompt_suggestions.ainvoke({"input": state["messages"][-1]})
    print("[PROMPT SUGGESTIONS]", result)
    prompts = [result.prompt_one, result.prompt_two, result.prompt_three]
    return Command(
        graph="prompt_suggestions",
        update={
            "messages": [
                AIMessage(
                    content=prompts, name="prompt_suggestions"
                )
            ]
        },
        goto="__end__"
    )

async def prompt_suggestions_tool(input: str) -> List[StopIteration]:
    prompt_suggestions = prompt_suggestions_prompt | llm.with_structured_output(PromptSuggestions)
    # print("[PROFILER] PROFILE IN:\n", json.dumps(state["user_profile"], indent=2))
    result = await prompt_suggestions.ainvoke({"input": input})
    print("[PROMPT SUGGESTIONS]", result)
    prompts = [result.prompt_one, result.prompt_two, result.prompt_three]
    return prompts
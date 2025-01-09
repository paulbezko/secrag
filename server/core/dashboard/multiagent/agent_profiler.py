from langchain_core.prompts import ChatPromptTemplate
from globals import State, llm
from user_profile_model import InvestorTraderProfile
import json

user_profiler_prompt = """
You are profiling a trader. Given a user's current profile, user's prompt\
your task is to update the user's profile. You cannot remove items from profile, only edit them.

user_prompt: {user_prompt}
user_profile: {user_profile}
"""

profiler_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", user_profiler_prompt),
            ]
)

async def profiler_node(state: State):
    profiler = profiler_prompt | llm.with_structured_output(InvestorTraderProfile)
    # print("[PROFILER] PROFILE IN:\n", json.dumps(state["user_profile"], indent=2))
    result = await profiler.ainvoke({"user_prompt": state["messages"][-1], "user_profile": state["user_profile"]})
    
    with open("server/memory/trader_profiles.json", "r") as f:
        profiles = json.load(f)
    # print("[PROFILER] PROFILE OUT:\n", json.dumps(result.to_dict(), indent=2))
    output_profile = result.to_dict()
    for i in output_profile.keys():
        if output_profile[i] is None:
            output_profile[i] = state["user_profile"][i]
    profiles[state["user_id"]] = output_profile
    with open("server/memory/trader_profiles.json", "w") as f:
        json.dump(profiles, f, indent=2)
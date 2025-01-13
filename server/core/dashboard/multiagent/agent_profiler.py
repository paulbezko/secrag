from langchain_core.prompts import ChatPromptTemplate
from globals import State, llm


user_profiler_prompt = """
You are profiling a trader. 
Your task is to create a detailed yet concise profile based on the user's current profile and the most recent user prompt. 
You should extract and update the relevant details from the user's prompt. 

Focus on summarizing key traits, preferences, and behaviors in a clear, concise manner. 
Avoid unnecessary elaboration and ensure that the profile remains coherent and easy to understand.

user_prompt: {user_prompt}
user_profile: {user_profile}
"""

profiler_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", user_profiler_prompt),
    ]
)

async def profiler_node(state: State):
    profiler = profiler_prompt | llm
    # print("[PROFILER] PROFILE IN:\n", json.dumps(state["user_profile"], indent=2))
    result = await profiler.ainvoke({"user_prompt": state["messages"][-1], "user_profile": state["user_profile"]})
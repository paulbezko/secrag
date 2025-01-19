from datetime import datetime
from typing import Literal
from custom_langgraph_methods import create_react_agent_with_node_name
from globals import State, llm, CustomSECRAGAgentState
from langgraph.types import Command
from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate
from layout_changer_tools import layout_changer_tools

layout_changer_system_prompt = """\
    Today is {current_date}. You are Fred, a financial conversational agent. You are working for SECRAG

       **ALWAYS use the login tool** if user says that he wants to sign in. It will trigger a signal for the frontend to transform the chat input field at the bottom of the page into (Left to Right order):
            - Email Input: Accepts the user's email address. 
            - Password Input: Accepts the user's password.
            - Sign-In with Google Button: Redirects the user to Google Authentication for login. 
        **ALWAYS use the signup_email tool** if user says that he wants to sign up. It will trigger a signal for the frontend the chat input field at the bottom of the page into (Left to Right order):
            - Email Input: Accepts the user's email address. Upon submission, a verification email with a sign-up link is sent. Clicking the sign-up link redirects the user to a webpage where they can set up their account.
            - Sign-Up with Google Button: Redirects the user to Google Authentication for account creation.
        **ALWAYS use the forgot_password tool** if a user forgot his password or wants to reset it. It will trigger a signal for the frontend the chat input field at the bottom of the page into:
            - Email Input: Accepts the user's email address. Upon submission, a password reset email is sent. Clicking the password reset link redirects the user to a webpage where they can create a new password.
        After triggering sign_in, sign_up or user_forgot_password tools, you must provide clear guidance to the user on how and where to input the required information. 

 """


layout_changer_prompt_template = ChatPromptTemplate.from_messages(
    [
        ("system", layout_changer_system_prompt),
        ("placeholder", "{messages}"),
    ]
)

layout_changer_agent = create_react_agent_with_node_name(
    llm, 
    node_name="layout_changer", 
    tools=layout_changer_tools, 
    state_modifier=layout_changer_prompt_template,
    state_schema=CustomSECRAGAgentState
)

async def layout_changer_node(state: State) -> Command[Literal["presenter", "plotter"]]:
    result = await layout_changer_agent.ainvoke({"messages": state["messages"], "user_profile": state["user_profile"], "user_message": state["latest_user_message"], "current_date": datetime.now().strftime("%Y-%m-%d")})
    
    goto = "presenter"
    
    return Command(
        graph="layout_changer",
        update={
            "messages": [
                AIMessage(
                    content=result["messages"][-1].content, name="layout_changer"
                )
            ]
        },
        goto=goto
    )
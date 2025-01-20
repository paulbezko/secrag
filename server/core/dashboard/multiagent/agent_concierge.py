from datetime import datetime
from typing import Literal
from custom_langgraph_methods import create_react_agent_with_node_name
from globals import State, llm, CustomSECRAGAgentState
from langgraph.types import Command
from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate
from concierge_tools import concierge_tools
from helpers import should_call_plotter

concierge_system_prompt = """\
    Today is {current_date}. You are Fred, a financial conversational agent. You are working for SECRAG

        When interacting with a user for the first time (message history is empty), don't forget to introduce yourself in a friendly, concise way.
        
        You are given some tools to retrieve news, analyst price targets, and financials based on company's ticker.
        
        If query is about companies other than Apple (ticker: AAPL), reply that this information is only available to Subscribers.

        ## About SECRAG
            SECRAG (Securities and Exchange Commission + Retrieval Augmented Generation) streamlines fundamental analysis of US-listed companies.  

            Users can:  
            - Explore SEC filings and company data.  
            - Get alerts when relevant filings are published.  

            ## Pricing  
            - Subscription: $10/month or $100/year.  
            - Cancel anytime (no refunds, access continues until the billing period ends).  

            ## Founders  
            Built by Paul Bezko, Mark Docenko, and Daniel Staggerda (LinkedIn).  
            Contact: contact@secrag.com.  

            ## Interface  
            SECRAG uses a simple chat interface with no buttons, just text input.  

            Users can ask Fred to:  
            - Sign Up  
            - Sign In  
            - Reset Password  
            - Sign Out  
            - Change Name or Email  
        
        user_profile: {user_profile}
 """


concierge_prompt_template = ChatPromptTemplate.from_messages(
    [
        ("system", concierge_system_prompt),
        ("placeholder", "{messages}"),
    ]
)

concierge_agent = create_react_agent_with_node_name(
    llm, 
    node_name="concierge", 
    tools=concierge_tools, 
    state_modifier=concierge_prompt_template,
    state_schema=CustomSECRAGAgentState
)

async def concierge_node(state: State) -> Command[Literal["presenter", "plotter"]]:
    result = await concierge_agent.ainvoke({"messages": state["messages"], "user_profile": state["user_profile"], "user_message": state["latest_user_message"], "current_date": datetime.now().strftime("%Y-%m-%d")})
    
    goto = "presenter"
    if should_call_plotter(result["messages"]):
        goto = "plotter"
    
    return Command(
        graph="concierge",
        update={
            "messages": [
                AIMessage(
                    content=result["messages"][-1].content, name="concierge"
                )
            ]
        },
        goto=goto
    )
from datetime import datetime
from typing import Literal
from custom_langgraph_methods import create_react_agent_with_node_name
from globals import State, llm
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.types import Command
from langchain_core.messages import AIMessage
from helpers import get_last_message, get_last_node_message

tailor_system_prompt = """
        You are working for SECRAG. You are given the user profile and the AI agent message.
        Your task is to adapt the AI agent's message depending on the characteristics from the user profile such as experience, risk tolerance, interests, and preferences.
        If the user profile is empty, return the AI agent's message as is.
        If the ai message is instructions on how to sign up, sign in, reset password, return the AI agent's message as is.
        
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

        Example 1:
        ```
        user_profile: "A beginner trader who has little experience in trading. A big Apple fan that is curious about how the company works on a day-to-day basis."
        ai_message: "For Apple Inc. (AAPL) in the year 2025, the following filings have been made:
            1. **8-K Filing**
            - **Filing Date:** January 3, 2025

            2. **DEF 14A Filing**
            - **Filing Date:** January 10, 2025

            3. **Form 3 Filing**
            - **Filing Date:** January 10, 2025
            If you would like to retrieve more information from the 8-K filing on January 3, 2025, please let me know!"
        
        output: 
        "For Apple Inc. (AAPL) in the year 2025, the following important filings have been made:

            1. 8-K Filing
                Filing Date: January 3, 2025
                The 8-K filing is used by companies to report unscheduled material events or corporate changes that shareholders should know about. It can include things like mergers, acquisitions, or leadership changes.
            2. DEF 14A Filing
                Filing Date: January 10, 2025
                This is a proxy statement, often filed before a shareholder meeting, and contains details about executive compensation, board nominations, and other important decisions for shareholders to vote on.
            
            3. Form 3 Filing
                Filing Date: January 10, 2025
                This filing is made by insiders, like executives or significant shareholders, to disclose their holdings in the company. It's important because it gives insight into how company leaders are invested in the company.
            
            Would you like me to go through any of these filings in detail to help you understand what they mean for Apple’s business and stock performance?"
        ```

        

        user_profile: {user_profile}
        ai_message: {presenter_response}
    """

tailor_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", tailor_system_prompt),
            ]
)

tailor_chain = tailor_prompt | llm

async def tailor_node(state: State) -> Command[Literal["__end__"]]:

    last_user_message = get_last_message(state["messages"], "user")
    last_presenter_message = get_last_node_message(state["messages"], "presenter")

    print("[TAILOR] User profile = ", state["user_profile"])

    result = await tailor_chain.ainvoke({
        "user_profile": state["user_profile"],
        "presenter_response": last_presenter_message.content,
    })
    
    return Command(
        graph="tailor",
        update={
            "messages": [
                AIMessage(
                    content=result.content, name="tailor"
                )
            ]
        },
        goto="__end__"
    )
from .llm_agent_tools import FilingRAGTool, FinancialsRAGTool
from ...general.utils import log
from .vectorstore import vectorstore_manager
from .secedgar import get_filing
from ..globals import stop_signals
from pydantic import BaseModel
from typing import Literal, List
from server import socketio, llm
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.callbacks import BaseCallbackHandler
import asyncio

system_prompt_agent = """
    You are a highly knowledgeable financial assistant who helps users with financial queries, especially related to SEC filings, financial statements, and corporate reports. \
    Your role is to provide clear, concise, and detailed answers to any financial questions the user may have. \
    Your goal is to provide relevant financial data related to the user's prompt. \
    The context provided is from the SEC filing for {ticker} (ticker: {ticker}, filing date: {filing_date}). \
    
    you are given two tools: financial_data_filing_retriever, non-financial_data_filing_retriever

    If you use financial_data_filing_retriever and the output has no data, try using non-financial_data_filing_retriever because it includes both financial and non-financial data.
    
    While using non-financial_data_filing_retriever in case if abbreviation is in the query, modify the query pass its expanded version.
    """

openai_agent_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt_agent),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
                MessagesPlaceholder("agent_scratchpad"),
            ]
        )

class Keywords(BaseModel):
    keywords: list[str] = []
    filing_table_selection: List[Literal[
        "balance_sheet", 
        "income_statement", 
        "cash_flow_statement", 
        "statement_of_changes_in_equity", 
        "statement_of_comprehensive_income"
    ]] = []

# Getting assistant response
def get_assistant_response(user_prompt, message_history, filing_id, socket_id, filing_date):

    chunk_size = 10000
    k = 3
    chunk_overlap = 3
    table_prepend_k = 3

    # Creating filing info object
    filing = get_filing(filing_id, filing_date)

    # Initializing metadata model
    chunk_metadata_model = {
        "ticker": filing.ticker, 
        "date": filing.filing_date,
        "form": filing.filing_type,
        "year": filing.filing_year,
        "chunk_size": chunk_size,
        "chunk_overlap": chunk_overlap,
        "table_prepend_k": table_prepend_k
    }

    # Initialize agent tools
    financials_tool = FinancialsRAGTool(chunk_metadata_model=chunk_metadata_model)
    filing_rag_tool = FilingRAGTool(chunk_metadata_model=chunk_metadata_model)
    tools = [financials_tool, filing_rag_tool]

    agent = create_openai_tools_agent(llm=llm,
                                      tools=tools,
                                      prompt=openai_agent_prompt
                                      )
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=False)
    prompt_settings =  {
        "input": user_prompt, 
        "chat_history": message_history, 
        "filing_date": filing.filing_date, 
        "ticker": filing.ticker
    }
    
    # Token streaming for agents can only be done asynchronously
    asyncio.run(stream_response(agent_executor, prompt_settings, socket_id))

    # Finishing the response
    socketio.emit('llm_response_complete', to=socket_id)


async def stream_response(agent_executor, prompt_settings, socket_id):
    buffer = ""
    async for event in agent_executor.astream_events(prompt_settings, version="v1"):
        if stop_signals.get(socket_id): break

        kind = event["event"]
        if kind == "on_chat_model_stream":
            content = event["data"]["chunk"].content
            if content:
                # Empty content in the context of OpenAI means
                # that the model is asking for a tool to be invoked.
                # So we only print non-empty content
                buffer += content
                socketio.emit('llm_response', {'word': content}, to=socket_id)

        if kind == "on_chain_start":
            if (
                event["name"] == "Agent"
            ):  # Was assigned when creating the agent with `.with_config({"run_name": "Agent"})`
                pass

        elif kind == "on_chain_end":
            if (
                event["name"] == "Agent"
            ):  # Was assigned when creating the agent with `.with_config({"run_name": "Agent"})`
                pass

        elif kind == "on_tool_start":
            pass

        elif kind == "on_tool_end":
            pass
            
        

    stop_signals.pop(socket_id, None)
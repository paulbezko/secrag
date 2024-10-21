from langchain_openai import ChatOpenAI
from pydantic import BaseModel
from typing import List, Literal

model = ChatOpenAI(temperature=0, api_key="sk-proj-0U1etEdNPyfN0tEvklyVT3BlbkFJ0899XXITmyGhvlsfA7eS", model_name="gpt-4o-mini")

def get_reformulated_prompt_from_history(user_prompt, history, filing_id="AAPL-10-K"):

    system_prompt = f"""
    You are presented with a current request and the latest chat messages from a human. Your task is to assess whether the current request is a follow-up to one of the latest chat messages.

    To determine if the current request is a follow-up, consider the following:

    It qualifies as a follow-up if it implicitly or explicitly asks for further detail about the previous topic, uses ambiguous terms (e.g., "it," "this") that refer to the last specific message, requests additional formatting (e.g., "return as markdown"), or seeks clarification on a specific aspect of the last prompt.
    If the current request relates to previous messages and pertains specifically to SEC filings or financial statements, it may be relevant to the filing ID: {filing_id}. Reformulate it to include relevant context only if necessary.
    If the current request is about general financial concepts (e.g., explaining what a balance sheet is or the significance of a 10-Q), do not include historical context in the reformulation.
    Do not classify it as a follow-up if the request addresses a different financial statement, topic, or request that doesn’t build upon the previous requests.
    If the current request qualifies as a follow-up, reformulate it to clearly state what information is being requested, replacing vague references (e.g., "it," "this") with the specific topic from the previous message, ensuring that no irrelevant historical context is included if the question is general.

    If the current request does not qualify as a follow-up, return it as is. Return nothing else but the request.

    Latest chat messages: {history}
    Request: {user_prompt}
    """

    response = model.invoke(system_prompt).content
    return response



def get_decision(reformulated_prompt, filing_id):

    class Decision(BaseModel):
        relevant: bool

    system_prompt = f"""
    You are an expert in financial documents, particularly SEC filings such as 10-K and 10-Q reports. \
    The user is referencing the filing ID: {filing_id}. \
    Based on the following message, determine if the user is asking for information related to financial documents \
    specifically associated with this filing ID. \
    This includes details like balance sheets, income statements, cash flow statements, and any other relevant financial data typically found in SEC filings.
    
    Message: {reformulated_prompt}
    """

    response = model.with_structured_output(Decision).invoke(system_prompt).relevant
    return response



def get_decision_v2(prompt, history, filing_id):

    class Keywords(BaseModel):
        keywords: list[str] = []
        filing_table_selection: List[Literal[
            "balance_sheet", 
            "income_statement", 
            "cash_flow_statement", 
            "statement_of_changes_in_equity", 
            "statement_of_comprehensive_income"
        ]] = []

    system_prompt = f"""
    You are an expert in financial documents, particularly SEC filings such as 10-K and 10-Q reports. You are presented with a current request and the latest chat messages from a human.
    
    Based on the following message, determine if the user is asking for information related to specific financial tables (e.g., balance sheet, income statement, cash flow statement) within this filing ID. This includes selecting relevant tables such as balance sheets, income statements, or cash flow statements, as well as identifying other key financial terms not directly tied to specific tables.
    
    When deciding, consider the following guidelines:
    
    - If the user is asking for specific financial documents (e.g., "show me the balance sheet"), populate the **filing_table_selection** field with the relevant tables such as 'balance_sheet', 'income_statement', or 'cash_flow_statement'.
    - If the user's message references financial data that could span multiple tables (e.g., "What do you think about their liquidity?"), add the specific table(s) related to that concept and populate the **keywords** field with other relevant financial terms (e.g., 'liquidity', 'assets').
    - Ensure precision in determining what the user is asking for, and only fill **filing_table_selection** with tables specifically related to the question. Use **keywords** for related terms not directly referencing specific tables.
    - If the question is unrelated to financial documents or tables, leave both **filing_table_selection** and **keywords** empty.
    
    Return the following:
    
    - Populate **filing_table_selection** with the relevant financial tables.
    - Populate **keywords** with other financial terms that are relevant but do not correspond to a specific table.

    Chat history: {history}
    Latest message: {prompt}
    Filing ID: {filing_id}
    """

    # Get response from the model and populate the keywords.
    response = model.with_structured_output(Keywords).invoke(system_prompt)

    return response.keywords, response.filing_table_selection


list_chats = [
    # Case 1: Balance sheet reference followed by a non-financial question
    {
        'history': ['show me balance sheet', 'banana monkey'],
        'user_prompts_with_answers': {
            "what do you think about it",  # Likely referring to the balance sheet, relevant.
            "what day is it today",        # Unrelated to financial documents, not relevant.
            "show me balance sheet",       # Directly requesting a financial document, relevant.
        }
    },
    
    # Case 2: Mixed conversation about finance and other topics
    {
        'history': ['what are the top movies this week', 'show me the income statement'],
        'user_prompts_with_answers': {
            "what are the revenue figures", # Likely asking about income statement, relevant.
            "who is the CEO of Apple",      # Unrelated to financial documents, not relevant.
            "show me the income statement", # Direct request for financial document, relevant.
        }
    },
    
    # Case 3: Non-financial conversation with an abrupt shift to finance
    {
        'history': ['who won the soccer game yesterday', 'what is the weather forecast'],
        'user_prompts_with_answers': {
            "what do you think about earnings", # Abrupt shift to finance, relevant.
            "what's the best recipe for pizza", # Unrelated to financial documents, not relevant.
            "show me the cash flow statement",  # Direct request for financial document, relevant.
        }
    },
    
    # Case 4: Primarily finance-related, with a mix of prompts
    {
        'history': ['show me the annual report', 'do you like coffee'],
        'user_prompts_with_answers': {
            "can you analyze the report",   # Referring to financial report, relevant.
            "how much cash do they have",   # Likely referring to balance sheet, relevant.
            "what's your favorite movie",   # Unrelated to financial documents, not relevant.
        }
    },
    
    # Case 5: No financial references in history, with a sudden finance request
    {
        'history': ['tell me a joke', 'what time is it'],
        'user_prompts_with_answers': {
            "can you show me the balance sheet", # New request for financial document, relevant.
            "who is the current president",      # Unrelated to financial documents, not relevant.
            "what do you think about profits",   # Could refer to financial documents indirectly, relevant.
        }
    },
    
    # Case 6: Historical reference, then indirect finance query
    {
        'history': ['tell me about World War II', 'how do you bake a cake'],
        'user_prompts_with_answers': {
            "what do you think about the balance sheet", # Directly related to financial document, relevant.
            "what is inflation",                        # Indirectly related to finance, could be relevant depending on context.
            "show me the income statement",             # Direct request for financial document, relevant.
        }
    },
    
    # Case 7: Financial conversation, followed by casual questions
    {
        'history': ['show me the quarterly earnings', 'what is your favorite color'],
        'user_prompts_with_answers': {
            "how is their revenue growth", # Likely asking about earnings, relevant.
            "what's the weather like",     # Unrelated to financial documents, not relevant.
            "show me the earnings report", # Direct request for financial document, relevant.
        }
    }
]



filing_id = "AAPL-2023-10K"
correct_count = 0
total_count = 0

for chat in list_chats:
    history = chat['history']
    user_prompts = chat['user_prompts_with_answers']

    for prompt in user_prompts:
        # reformulated_prompt = get_reformulated_prompt_from_history(prompt, history, filing_id)
        keywords, filing_table_selection = get_decision_v2(prompt, history, filing_id)

        # Print results for each prompt
        print(f"History: {history}\nQuestion: {prompt}")
        print(f"Keywords: {keywords}\nFiling Table Selection: {filing_table_selection}\n")
        
        # Update counters
        # total_count += 1
        # if bool_use_rag == expected_answer:
        #     correct_count += 1

# Calculate accuracy
# if total_count > 0: accuracy = (correct_count / total_count) * 100
# else: accuracy = 0.0  # Handle case where no prompts were processed
# print(f"Accuracy: {accuracy:.2f}% ({correct_count}/{total_count})")



# list_input_prompts = [
#     "What were the major risks for AAPL in the latest report?",  
#     "How does the economy impact stock performance?",  
#     "How does AAPL's gross margin compare to competitors?",  
#     "Give me balance sheet",  
#     "Show me income statement and balance sheet",  

#     # Additional test cases:
#     "What does the cash flow statement say about the company's liquidity?",  
#     "Compare the statement of changes in equity with the latest comprehensive income report",  
#     "Can I see the balance sheet from the latest 10-Q?",  
#     "Summarize Apple's 10-K income statement",  
#     "Explain the difference between the income statement and cash flow statement",  
#     "Tell me more about the company's financials",  
#     "What is a 10-K filing?",

#     # New ones with elements of filings
#     "What are AAPL's current assets?",  # Refers to an element in balance sheet
#     "How much revenue did Apple generate last year?",  # Implies income statement
#     "What are AAPL's operating expenses?",  # Implies income statement
#     "How much cash does AAPL have on hand?",  # Refers to cash flow/balance sheet
#     "What is AAPL's net income?",  # Implies income statement
# ]

# from typing import List, Optional, Literal
# class ContextualOutput(BaseModel):
#     keywords: str
#     filing_selection: Optional[List[Literal[
#         "balance_sheet", 
#         "income_statement", 
#         "cash_flow_statement", 
#         "statement_of_changes_in_equity", 
#         "statement_of_comprehensive_income"
#     ]]] = None


# for prompt in list_input_prompts:

#     system_prompt = f"""
#     You are a helpful assistant. Your task is to analyze the user's prompt and derive any useful keywords that can be used to answer their question.
#     If the user is asking about specific financial statements like a balance sheet, income statement, etc., return those financial statements. If the user asks for multiple financial statements, return all that are relevant.

#     Only return a filing_selection if the user is asking for or implying financial data related to a specific financial report, like a balance sheet or income statement. If no financial statement is implied, leave filing_selection empty.

#     The output should be structured as:
#         keywords: str
#         filing_selection: Optional[List[Literal["balance_sheet", "income_statement", "cash_flow_statement", "statement_of_changes_in_equity", "statement_of_comprehensive_income"]]] = None

#     User prompt:
#     {prompt}
#     """

#     response = model.with_structured_output(ContextualOutput).invoke(system_prompt)

#     print(f"\nPrompt: {prompt}\nKeywords: {response.keywords}\nFiling Selection: {response.filing_selection}")
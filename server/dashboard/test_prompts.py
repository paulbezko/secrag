from langchain_openai import ChatOpenAI
from pydantic import BaseModel


model = ChatOpenAI(temperature=0, api_key="sk-proj-0U1etEdNPyfN0tEvklyVT3BlbkFJ0899XXITmyGhvlsfA7eS", model_name="gpt-4o-mini")

def get_reformulated_prompt_from_history(user_prompt, history):

    system_prompt = f"""
    You are presented with a current request and the latest chat messages from a human. Your task is to assess whether the current request is a follow-up to one of the latest chat messages.

    To determine if the current request is a follow-up, consider the following:

    - It qualifies as a follow-up if it implicitly or explicitly asks for further detail about the previous topic, requests additional formatting (e.g., "return as markdown"), or seeks clarification on a specific aspect of the last prompt.
    - If the current request relates to previous messages and pertains specifically to SEC filings or financial statements, reformulate it to include relevant context.
    - **If the current request is about general financial concepts (e.g., explaining what a balance sheet is or the significance of a 10-Q), do not include historical context in the reformulation.**
    - Do not classify it as a follow-up if the request addresses a different financial statement, topic, or request that doesn’t build upon the previous requests.

    If the current request qualifies as a follow-up, reformulate it to clearly state what information is being requested, ensuring that no irrelevant historical context is included if the question is general.
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


list_chats = [
    {
        'history': [
            {'role': 'user', 'content': 'What is your favorite movie?'},
            {'role': 'user', 'content': 'Give me balance sheet figures.'},
            {'role': 'user', 'content': 'What do you think about the new tech trends?'},
            {'role': 'user', 'content': 'Can you summarize the cash flow statement for the last quarter?'},
            {'role': 'user', 'content': 'Tell me about the weather in New York.'},
        ],
        'user_prompts_with_answers': {
            "What were the total assets listed in the last balance sheet?": True,
            "What were the liabilities reported in the most recent filing?": True,
            "Show the revenue for the last fiscal year in the 10-K.": True,
            "Can you explain what a balance sheet is?": False,
            "How do stock markets work?": False,
            "What information is included in the financial statements of a 10-K?": False,
        }
    },
    {
        'history': [
            {'role': 'user', 'content': 'What hobbies do you have?'},
            {'role': 'user', 'content': 'Summarize the major risks in the 10-Q.'},
            {'role': 'user', 'content': 'What is your favorite type of cuisine?'},
            {'role': 'user', 'content': 'What were the key metrics for the last quarter?'},
            {'role': 'user', 'content': 'Who won the last football match?'},
        ],
        'user_prompts_with_answers': {
            "What are the earnings per share reported in the last 10-Q?": True,
            "What risks were discussed in the latest 10-K?": True,
            "What are the operating cash flows for the last fiscal year?": True,
            "What is the significance of a 10-Q?": False,
            "How does inflation impact investments?": False,
            "Can you explain the difference between a 10-K and a 10-Q?": False,
        }
    },
    {
        'history': [
            {'role': 'user', 'content': 'Can you recommend a good book?'},
            {'role': 'user', 'content': 'What were the earnings reported in the last 10-K?'},
            {'role': 'user', 'content': 'What is your take on climate change?'},
            {'role': 'user', 'content': 'Show me the trends in revenue from the last filing.'},
            {'role': 'user', 'content': 'What is the latest news in technology?'},
            {'role': 'user', 'content': 'What’s the total revenue reported in the last quarter?'},
        ],
        'user_prompts_with_answers': {
            "What were the major expenses reported in the latest 10-K?": True,
            "What is the company's debt-to-equity ratio according to the last filing?": True,
            "How does the cash flow compare to last year?": True,
            "What does a 10-K include?": False,
            "Can you explain what an income statement is?": False,
            "What are the types of disclosures required in SEC filings?": False,
        }
    },
    {
        'history': [
            {'role': 'user', 'content': 'What’s your opinion on space exploration?'},
            {'role': 'user', 'content': 'Can you tell me about the latest cash flow statement?'},
            {'role': 'user', 'content': 'What are some good travel destinations?'},
            {'role': 'user', 'content': 'List the major financial figures from the last 10-Q.'},
            {'role': 'user', 'content': 'What do you think about AI technology?'},
            {'role': 'user', 'content': 'How did the company perform in terms of net income?'},
        ],
        'user_prompts_with_answers': {
            "What were the cash flows from operations in the last 10-Q?": True,
            "What were the investments listed in the last filing?": True,
            "What is the significance of cash flow statements?": False,
            "How do you calculate earnings per share?": False,
            "What is the purpose of financial statements?": False,
            "Explain the role of the SEC in financial reporting.": False,
        }
    },
    {
        'history': [
            {'role': 'user', 'content': 'What’s the latest blockbuster movie?'},
            {'role': 'user', 'content': 'What were the total liabilities in the last 10-K?'},
            {'role': 'user', 'content': 'How do you feel about virtual reality?'},
            {'role': 'user', 'content': 'Summarize the revenue figures for the last quarter.'},
            {'role': 'user', 'content': 'What is the weather forecast for next week?'},
            {'role': 'user', 'content': 'Explain the concept of working capital.'},
        ],
        'user_prompts_with_answers': {
            "What is the total equity reported in the last filing?": True,
            "What were the earnings reported in the last fiscal year?": True,
            "Show me the key figures from the balance sheet.": True,
            "What is the role of financial analysts?": False,
            "Can you discuss the significance of quarterly reports?": False,
            "What are some key factors in analyzing financial statements?": False,
        }
    },
]



filing_id = "AAPL-2011-10K"

for chat in list_chats:
    history = chat['history']
    user_prompts_with_answers = chat['user_prompts_with_answers']

    for prompt, expected_answer in user_prompts_with_answers.items():
        reformulated_prompt = get_reformulated_prompt_from_history(prompt, history)
        response = get_decision(reformulated_prompt, filing_id)

        # Print results for each prompt
        print(f"Question: {prompt}\nReformulated Prompt: {reformulated_prompt}")
        print(f"Expected: {expected_answer}, Model Response: {response} {'✅' if response == expected_answer else '❌'}\n")

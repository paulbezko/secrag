from langchain_openai import ChatOpenAI
from pydantic import BaseModel


model = ChatOpenAI(temperature=0, api_key="sk-proj-0U1etEdNPyfN0tEvklyVT3BlbkFJ0899XXITmyGhvlsfA7eS", model_name="gpt-4o-mini")

def get_reformulated_prompt_from_history(user_prompt, history, filing_id="AAPL-10-K"):

    system_prompt = f"""
    You are presented with a current request and the latest chat messages from a human. Your task is to assess whether the current request is a follow-up to one of the latest chat messages.

    To determine if the current request is a follow-up, consider the following:

    - It qualifies as a follow-up if it implicitly or explicitly asks for further detail about the previous topic, requests additional formatting (e.g., "return as markdown"), or seeks clarification on a specific aspect of the last prompt.
    - If the current request relates to previous messages and pertains specifically to SEC filings or financial statements, it may be relevant to the filing ID: {filing_id}. Reformulate it to include relevant context only if necessary.
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
            "What are the earnings per share reported in the last 10-Q?": False,
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
            "What were the cash flows from operations in the last 10-Q?": False,
            "What were the investments listed in the last filing?": False,
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
    {
            'history': [
            {'role': 'user', 'content': 'What is the best strategy for investing?'},
            {'role': 'user', 'content': 'Can you tell me about AAPL’s revenue for 2023?'},
            {'role': 'user', 'content': 'What do you think about the latest smartphone releases?'},
            {'role': 'user', 'content': 'What were the operating expenses in the latest 10-K?'},
            {'role': 'user', 'content': 'What’s your favorite sport?'},
        ],
        'user_prompts_with_answers': {
            "How much was AAPL's net income last year?": True,
            "What trends do you see in tech investments?": False,
            "What were the key financial ratios reported in the last 10-K?": True,
            "Can you explain what an investment portfolio is?": False,
            "What is a 10-K filing?": False,
            "List some key performance indicators for AAPL.": True,
        }
    },
    {
        'history': [
            {'role': 'user', 'content': 'Do you like cats or dogs?'},
            {'role': 'user', 'content': 'Summarize the latest news about AAPL.'},
            {'role': 'user', 'content': 'What’s your favorite season?'},
            {'role': 'user', 'content': 'What were the cash flows reported in the last quarter?'},
            {'role': 'user', 'content': 'How many countries have you visited?'},
            {'role': 'user', 'content': 'What are the assets reported in the latest 10-K?'},
        ],
        'user_prompts_with_answers': {
            "What was AAPL's total revenue in the latest filing?": True,
            "What are the implications of the cash flow statement?": False,
            "What are the liabilities listed in the last 10-K?": True,
            "Can you explain the purpose of an income statement?": False,
            "What’s the importance of asset management?": False,
            "What are the current market trends for tech companies?": True,
        }
    },
    {
        'history': [
            {'role': 'user', 'content': 'What’s your favorite food?'},
            {'role': 'user', 'content': 'How does AAPL handle its supply chain?'},
            {'role': 'user', 'content': 'What do you think about electric vehicles?'},
            {'role': 'user', 'content': 'Summarize the risks mentioned in the latest 10-K.'},
            {'role': 'user', 'content': 'What’s the best way to learn a new language?'},
        ],
        'user_prompts_with_answers': {
            "What were the major risks for AAPL in the latest report?": True,
            "How does the economy impact stock performance?": False,
            "What is AAPL's strategy for growth according to the 10-K?": True,
            "What is an annual report?": False,
            "What factors influence consumer behavior?": False,
            "What financial metrics does AAPL focus on?": True,
        }
    },
    {
        'history': [
            {'role': 'user', 'content': 'What is your favorite vacation spot?'},
            {'role': 'user', 'content': 'How did AAPL perform in the last fiscal year?'},
            {'role': 'user', 'content': 'What are the benefits of yoga?'},
            {'role': 'user', 'content': 'What is the company’s gross margin as per the latest filing?'},
            {'role': 'user', 'content': 'Can you share a fun fact about space?'},
            {'role': 'user', 'content': 'What’s the current market cap of AAPL?'},
        ],
        'user_prompts_with_answers': {
            "How does AAPL's gross margin compare to competitors?": True,
            "What are the implications of gross margin for investors?": False,
            "What was the total debt reported in the last 10-K?": True,
            "What does market capitalization mean?": False,
            "Can you explain the difference between profit and revenue?": False,
            "What trends are currently influencing the tech sector?": True,
        }
    },
    {
        'history': [
            {'role': 'user', 'content': 'What’s the most popular music genre now?'},
            {'role': 'user', 'content': 'What was the total equity reported in AAPL’s latest 10-K?'},
            {'role': 'user', 'content': 'Do you like art?'},
            {'role': 'user', 'content': 'What are the key figures in AAPL’s cash flow statement?'},
            {'role': 'user', 'content': 'How do you stay updated with world events?'},
            {'role': 'user', 'content': 'What is AAPL’s approach to sustainability?'},
        ],
        'user_prompts_with_answers': {
            "What were the significant investments reported in the last filing?": True,
            "How is sustainability measured in financial reports?": False,
            "What were the earnings reported in the last fiscal year?": True,
            "What is the role of corporate social responsibility?": False,
            "What are some challenges in the tech industry?": True,
            "What is an ESG report?": False,
        }
    },
    {
        'history': [
            {'role': 'user', 'content': 'Can you show me the balance sheet?'},
            {'role': 'user', 'content': 'Render it in a markdown form'},
        ],
        'user_prompts_with_answers': {
            "in a csv format": True,
        }
    },
]


filing_id = "AAPL-2023-10K"
correct_count = 0
total_count = 0

for chat in list_chats:
    history = chat['history']
    user_prompts_with_answers = chat['user_prompts_with_answers']

    for prompt, expected_answer in user_prompts_with_answers.items():
        reformulated_prompt = get_reformulated_prompt_from_history(prompt, history, filing_id)
        bool_use_rag = get_decision(reformulated_prompt, filing_id)

        # Print results for each prompt
        print(f"Question: {prompt}\nReformulated Prompt: {reformulated_prompt}")
        print(f"Expected: {expected_answer} | Model Response: {bool_use_rag} {'✅' if bool_use_rag == expected_answer else '❌'}\n")
        
        # Update counters
        total_count += 1
        if bool_use_rag == expected_answer:
            correct_count += 1

# Calculate accuracy
if total_count > 0: accuracy = (correct_count / total_count) * 100
else: accuracy = 0.0  # Handle case where no prompts were processed
print(f"Accuracy: {accuracy:.2f}% ({correct_count}/{total_count})")
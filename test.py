from langchain_openai import ChatOpenAI
from pydantic import BaseModel
import time

questions_yes = [
    "What was the total revenue for the fiscal year?",
    "What were the main sources of revenue during the year?",
    "How did international revenue compare to domestic revenue?",
    "What were the total operating expenses reported?",
    "What was the net income for the fiscal year?",
    "How did revenue this year compare to the previous year?",
    "What key risks were outlined in the filing?",
    "How much was spent on research and development?",
    "What was the cash and cash equivalents balance at the end of the year?",
    "What were the company's gross margins for the fiscal year?"
]

questions_no = [
    "What are the primary factors that drive a company's revenue growth?",
    "How do international markets typically impact a company's financial performance?",
    # "What are the common types of operating expenses for a tech company?",
    "How do companies determine the appropriate amount to allocate for research and development?",
    "What are the benefits of maintaining a large cash and cash equivalents balance?",
    "How do companies manage risks in a highly competitive industry?",
    "What strategies do companies use to improve their gross margins?",
    "How does a company's dividend policy affect its stock price and shareholder value?",
    "What are the potential benefits and risks of share buyback programs?",
    "How does foreign exchange fluctuation impact a company's earnings?"
]


class Decision(BaseModel):
    required: bool

model = ChatOpenAI(temperature=0, api_key="sk-proj-0U1etEdNPyfN0tEvklyVT3BlbkFJ0899XXITmyGhvlsfA7eS", model_name="gpt-4o-mini")
prompt = """
You are given a question. Your task is to determine whether the question requires **specific company information** that can only be found in a company's SEC 10-K filing (such as revenue, net income, risks, legal proceedings, or other company-specific data), or if it can be answered using **general business knowledge** or **common industry practices** that are not tied to a specific company’s filing.

- Output `required: true` if the question **must** be answered using specific company data found in a 10-K filing.
- Output `required: false` if the question can be answered with general business knowledge, industry practices, or does not require specific data from a 10-K filing.

You will be given a 100$ tip if you answer correctly.
Question:
"""

for question in questions_yes:
    response = model.with_structured_output(Decision).invoke(prompt + question)

    print(f"Question: {question}")
    print(f"Response: {response.required} | Correct: True")
    print("\n")

    time.sleep(3)

for question in questions_no:
    response = model.with_structured_output(Decision).invoke(prompt + question)

    print(f"Question: {question}")
    print(f"Response: {response.required} | Correct: False")
    print("\n")

    time.sleep(3)
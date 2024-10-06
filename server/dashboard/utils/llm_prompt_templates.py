from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate


# Chapter descriptions for some filing types
tenK_descriptions = ["Overview of the document","Overview of the company's business operations, products, services, and market environment.", "Discussion of risks and uncertainties that could materially affect the company's financial condition or results of operations.", 'Any comments from the SEC staff on the company’s previous filingsthat remain unresolved.', 'Information about the physical properties owned or leased by the company.', 'Details of significant ongoing legal proceedings.', 'Relevant for mining companies, disclosures about mine safety and regulatory compliance.', 'Information on the company’s equity, including stock performance and shareholder matters.', 'Financial data summary for the last five fiscal years.', 'Management’s perspective on the financial condition, changes in financial condition, and results of operations.', "Information on the company's exposure to market risk, such as interest rate risk, foreign currency exchange risk, commodity price risk, etc.", 'Complete audited financial statements, including balance sheet, income statement, cash flow statement, and notes to the financial statements.', 'Evaluation of the effectiveness of the design and operation of the company’s disclosure controls and procedures.', 'Evaluation of internal controls over financial reporting.', 'Any other relevant information not covered in other sections.', "Information about the company's directors, executive officers, and governance policies.", 'Details of compensation paid to key executives.', 'Information about stock ownership of major shareholders, directors, and management.', 'Information on transactions between the company and its directors, officers, and significant shareholders.', 'Fees paid to the principal accountant and services rendered.', 'Legal documents and financial schedules that support the financial statements and disclosures.']
tenQ_descriptions = ["Overview of the document",'Unaudited financial statements including balance sheets, income statements, and cash flow statements.', 'Management’s perspective on the financial condition and results of operations.', "Information on the company's exposure to market risk.", 'Evaluation of the effectiveness of disclosure controls and procedures.', 'Brief description of any significant pending legal proceedings.', 'An update on risk factors that may affect future results.', 'Details of unregistered sales of equity securities.', 'Information regarding any defaults on senior securities.', 'Required for companies with mining operations.', 'Any other information that should be disclosed to investors.', 'List of exhibits required by Item 601 of Regulation S-K.']

contextualize_q_system_prompt = """Return the keyphrases from \
the given question as a single string that will be used in \
FAISS similarity search to retrieve chunks from the document. 

Question: {prompt}

In addition, select chapter descriptions from the following list that most probably contain information to answer the question \

Chapter descriptions list: {chapter_descriptions_list}

Finally, note one by one if this prompt might be associated with the following items:
    balance_sheet
    income_statement
    cash_flow_statement
    statement_of_changes_in_equity
    statement_of_comprehensive_income
"""

contextualize_q_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", contextualize_q_system_prompt),
    ]
)

### Answer question ###
qa_system_prompt = """You are an assistant for question-answering tasks. \
Use the following pieces of retrieved context to answer the question. \
Do not recommend review SEC 10-k filings. \
    
context from SEC 10-k filing:
{context}"""



qa_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", qa_system_prompt),
        # MessagesPlaceholder("chat_history"),
        ("human", "{input}\n\nThe context is from the following SEC filing: (ticker: {ticker}, filing type: {filing_type}, filing date: {filing_date})"),
    ]
)

public_db_agent_system_prompt = """The following is a conversation between a human and an AI.
The AI is helping to learn about publicly traded companies and provides lots of specific details from its context.
If the AI does not know the answer to a question, it truthfully says it does not know.
You are provided with information about entities the Human mentions, if relevant.
"""

public_db_agent_prompt = ChatPromptTemplate.from_messages([
    ("system", public_db_agent_system_prompt),
    MessagesPlaceholder("chat_history"),
 ("human", "{input}"),
])

id_separator = "XDD2FFoLaPFn"

react_combinator_system_prompt = """You are an assistant for combining outputs from two different language models: one with access to a public database (LLM-Public) and another with access to a private database (LLM-Private). Your task is to combine the information from both outputs into a single coherent response to the given prompt.

Follow these rules:

1. Prioritize LLM-Private: If the information from LLM-Public and LLM-Private contradicts each other, prioritize the information from LLM-Private.

2. Resolve Unknowns: If either LLM suggests that it does not know the answer, use the information from the other LLM that does provide an answer.

3. Combine Non-Conflicting Information: When the information from both LLMs does not conflict, combine them, but give slight priority to the phrasing and emphasis from LLM-Private when synthesizing the final response.

4. Make a response look like an answer to the prompt.

5. Do not recommend to review or reference SEC 10-k, 10-Q filings by any means. 

Deliver the final output as a well-organized and clear response, ensuring that the information is accurate, and the structure is logical.

Prompt: {input_prompt}

LLM-Public output: {llm_public_context}

LLM-Private output: {llm_private_context}

At the end of the answer, suggest a follow-up question that \
would be relevant to the context of a SEC filing and could encourage deeper exploration of the topic. \

Do not reveal that you are combining two sources of information. 
"""

react_combinator_prompt = ChatPromptTemplate([
    ("system", react_combinator_system_prompt)
])
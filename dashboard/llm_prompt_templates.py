from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate

contextualize_q_system_prompt = """Given a chat history and the latest user question \
which might reference context in the chat history, formulate a standalone question \
which can be understood without the chat history. Keep in mind that the latest user question \
might be an answer to the previous assistant question. Include the question if that is the case. Do NOT answer the question, \
just reformulate it if needed and otherwise return it as is. \
"""
# Include a title of a SEC filing chapter, which most probably contains the relevant information. \
contextualize_q_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)

### Answer question ###
qa_system_prompt = """You are an assistant for question-answering tasks. \
Use the following pieces of retrieved context to answer the question. \
Do not recommend review SEC 10-k filings. \
If you don't know the answer or the answer cannot be found in the context just say "I don't know". \
    
context from SEC 10-k filing:
{context}"""



qa_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", qa_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
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

5. Do not recommend to review or reference SEC 10-k filings by any means. 

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
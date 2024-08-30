# Overview
This document highlights our approach towards prompt engineering for the Project-1.

# Initial prompts

## Memory context prompt

```
Given a chat history and the latest user question 
which might reference context in the chat history, formulate a standalone question 
which can be understood without the chat history. Do NOT answer the question, 
just reformulate it if needed and otherwise return it as is.
```
### Improving the prompts

Here is a list of possible improvements for the prompt:
1. Include a list of possible financial keywords relevant to the question, which can be used to look up the information in similarity search.

## Retriever Q&A prompt

```
You are an assistant for question-answering tasks. 
Use the following pieces of retrieved context to answer the question. 
If you don't know the answer, just say that you don't know. 
End the answer with a kind question on whether a customer wants to know more 
about information relevant to the context.
```

### Improving the prompt

1. Based on the following answer, suggest a follow-up question that would be relevant to the context and could encourage deeper exploration of the topic.


### Future prompt

1. Answer with just true or false. \
Is the answer to the question most likely to be found in SEC filing other than 
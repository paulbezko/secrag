# Project-1 Dashboard's LLM
## Overview
This folder includes code for the main product of the project: The Dashboard's LLM

The LLM consists of three agents:
1. RAG agent - for utilization of context from the private database
2. Public DB agent - for utilization of context on which LLM was trained
3. Combinator agent - to combine outputs of RAG and Public DB agents

## Usage
### GET request
The LLM can be used through GET requests.

The arguments for the request are the following:
1. prompt (Mandatory)
2. uid - User unique identifier (Mandatory)
3. conversation_id - User's conversation unique identifier 
4. socket_id - for SocketIO token-by-token callbacks
5. ticker - Company's ticker that the prompt is for (Mandatory if no Conversation ID)
6. filing - Specific filing number

The request is hosted on Flask application. Run `app.py` to start it.

### Test tool
The LLM comes with a TKinter based test tool. Run `app_test.py` to explore.

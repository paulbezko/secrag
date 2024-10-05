# Test items
We want to test our LLM on following abilities:
1. Creating new conversation
2. Memory utilization
3. Retriever context utilization
4. Usability of follow-up questions

We want to test the following performance metrics:
1. Satisfaction with output (0 to 10)
2. Speed (time from request to response)
3. Cost

Materials:
10 different SEC filings from the following categories:
1. Popular
2. Old
3. Nieche sector
4. Soon-to-be bankrupts (Hydrogen)
5. 10-Q


Prompts:

1. What are the company’s primary revenue streams?

1. How does the company describe its competitive landscape in its most recent filing?

1. What are the significant risks identified by the company in the risk factors section?

1. What are the major changes in the company’s operating expenses over the past fiscal year?

1. How has the company’s debt level changed over the past three years according to the filings?

1. How does the company evaluate its environmental, social, and governance (ESG) responsibilities in the report?

1. What are the company’s main legal proceedings or regulatory risks?

1. What forward-looking statements are made regarding future market trends and their impact on the company?

1. How does the company assess its liquidity and capital resources in the "Management’s Discussion and Analysis" section?


### Metrics
chunk_size=5000, chunk_overlap=1000, k=10
chunk_size, chunk_overlap, k =
[1000, 200, 10],
[1000, 500, 10],
[2000, 500, 10],
[3000, 500, 10], 
[5000, 1000, 10]


### Procedure
For each of metrics:
    For each prompt:
        Ask prompt,
        Get a response,
        Append the response to txt file for metric,
    Save text file (name f"{chunk_size}_{chunk_overlap}_{k}")
from app import ask_
import json

from utils.sec_utils import load_sec

output_structure = {
    "meta": {
        "ticker": "",
        "year": "",
        "chunk_size": "",
        "chunk_overlap": "",
        "k": ""
    },
    "data": [
        {
            "prompt": "",
            "llm_output": ""
        }
    ]
}

ticker_inputs = [
    ["RCKT", "2024"],
    # ["NVDA", "2024"],
    # ["PLUG", "2024"],
    # ["MSFT", "2001"],
    
]

prompts =  [
    # "What is the document about?",
    "What is the company's balance sheet",
    "What are the company’s primary revenue streams?",
    "How does the company describe its competitive landscape?",
    # "What are the significant risks identified by the company in the risk factors section?",
    "What are the major changes in the company’s operating expenses over the past fiscal year?",
    "How has the company’s debt level changed over the past three years according to the filings?",
    "How does the company evaluate its environmental, social, and governance (ESG) responsibilities in the report?",
    "What are the company’s main legal proceedings or regulatory risks?",
    "What forward-looking statements are made regarding future market trends and their impact on the company?",
    "How does the company assess its liquidity and capital resources in the 'Management’s Discussion and Analysis' section?",
]

# vectorstore_configs = [
#     [2000, 1000, 12],
#     [6000, 3000, 10],
#     [10000, 5000, 8],
#     [14000, 7000, 6],
#     [20000, 10000, 4],
#     [35000, 15000, 3],
#     [50000, 25000, 3],
#     [100000, 50000, 2],
# ]

# chunk_size, chunk_overlap, table_prepend_k, k
vectorstore_configs = [
    [10000, 3, 3, 4],
    [10000, 3, 3, 6],
    [10000, 3, 3, 8],
    [10000, 3, 3, 10],
    [10000, 3, 3, 12],
]

def performace_test(prompt, uid, conversation_id, ticker, year, chunk_size, chunk_overlap, k, table_prepend_k):
    prompt_output = ask_(prompt, uid, conversation_id, None, ticker, year, chunk_size, chunk_overlap, k, table_prepend_k)



def perform_test_for_set_of_settings(prompts, ticker, year, chunk_size, chunk_overlap, k, table_prepend_k, ready_filing):
    uid = "bot.test.paul@gmail.com"
    conversation_id = "{}-{}".format(ticker.upper(), str(year))

    output_structure = {
        "meta": {
            "ticker": ticker,
            "year": year,
            "chunk_size": chunk_size,
            "chunk_overlap": chunk_overlap,
            "k": k
        },
        "data": [

        ]
    }

    output = output_structure

    data_entry_structure = {
        "prompt": "",
        "llm_output": ""
    }

    for prompt in prompts:
        
        # try:
            print("CURRENT PROMPT: ", prompt)
            llm_output = ask_(prompt, uid, conversation_id, None, ticker, year, chunk_size, chunk_overlap, k, table_prepend_k, ready_filing=ready_filing)
            context_list = []
            for i in llm_output["rag_context"]:
                context_list.append(i.page_content)
            print("---------Answer-------------\n\n",llm_output["react_output"],"\n\n---------------")
            output["data"].append(
                {
                    "prompt": prompt,
                    "llm_output": llm_output["react_output"],
                    "context": context_list,
                    "usage_meta": llm_output["usage_meta"]
                }
            )
        # except:
        #     pass
    
    with open("performance_test/{}_CS{}_CO{}_K{}.json".format(conversation_id, chunk_size, chunk_overlap, k), "w") as json_file:
        json.dump(output, json_file, indent=4)  # 'indent=4' is for pretty-printing
    
if __name__ == "__main__":
    test_prompts = prompts
    test_vectorstore_configs = vectorstore_configs
    test_ticker_inputs = ticker_inputs
    # test_prompts = [prompts[0]]
    # test_vectorstore_configs = [vectorstore_configs[2]]
    # test_ticker_inputs = [ticker_inputs[0]]

    
    skipped = False
    for filing_data in test_ticker_inputs:

        ready_filing = load_sec(filing_data[0], filing_data[1])
        print(filing_data[0], filing_data[1])
        for vectorstore_config in test_vectorstore_configs:
            print(vectorstore_config)
            # if not skipped:
            #     skipped = True
            #     continue
            perform_test_for_set_of_settings(
                prompts=test_prompts, 
                ticker=filing_data[0], 
                year=filing_data[1], 
                chunk_size=vectorstore_config[0], 
                chunk_overlap=vectorstore_config[1], 
                k=vectorstore_config[3],
                table_prepend_k=vectorstore_config[2],
                ready_filing=ready_filing
            )                

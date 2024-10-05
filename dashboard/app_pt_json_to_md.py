import os
import json
import csv


# List all files in the current directory

input_path = "performance_test_custom_embedding"
output_path = "pt_mds_ce"

ticker_inputs = [
    ["NVDA", "2024"],
    ["PLUG", "2024"],
    ["MSFT", "2001"],
    ["RCKT", "2024"]
]

prompts =  [
    "What is the document about?",
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

vectorstore_configs = [
    [10000, 3, 3, 4],
    [10000, 3, 3, 6],
    [10000, 3, 3, 8],
    [10000, 3, 3, 10],
    [10000, 3, 3, 12],
]

md_structure = {

    "filing1": {
        "prompt": [
            {
                "cost" : "",
                "tokens_total" : "",
                "tokens_prompt" : "",
                "tokens_output" : "",
                "vectorstore_config": "",
                "output": ""
            },
            {
                "cost" : "",
                "tokens_total" : "",
                "tokens_prompt" : "",
                "tokens_output" : "",
                "vectorstore_config": "",
                "output": ""
            }
        ]      
    },
    "filing2": {
        "prompt": [
            {
                "cost" : "",
                "tokens_total" : "",
                "tokens_prompt" : "",
                "tokens_output" : "",
                "vectorstore_config": "",
                "output": ""
            },
            {
                "cost" : "",
                "tokens_total" : "",
                "tokens_prompt" : "",
                "tokens_output" : "",
                "vectorstore_config": "",
                "output": ""
            }
        ]      
    }
}

def load_files():
    files = os.listdir(input_path)
    return files

def read_file(filename):
    # Load JSON data from a file
    with open("{}/{}".format(input_path,filename), "r") as json_file:
        data = json.load(json_file)
        return data

def data_extractor():
    files = load_files()
    output = {}
    print(files)
    for file in files:
        data = read_file(file)
        meta = data["meta"]
        filing = "{}_{}".format(meta["ticker"],meta["year"])
        for datapoint in data["data"]:
            print("balls")
            if filing not in output:
                output[filing] = {}
            if datapoint["prompt"] not in output[filing]:
                output[filing][datapoint["prompt"]] = []

            usage_meta = datapoint["usage_meta"]["total"]
            output[filing][datapoint["prompt"]].append(
                {
                    "vectorstore_config": [meta["chunk_size"], meta["chunk_overlap"], meta["k"]],                
                    "cost" : usage_meta["cost"],
                    "tokens_total" : usage_meta["tokens"],
                    "tokens_prompt" : usage_meta["prompt_tokens"],
                    "tokens_output" : usage_meta["completion_tokens"],
                    "context" : datapoint["context"],
                    "output": datapoint["llm_output"]
                }
            )
    
    return output




# Function to generate markdown
def generate_markdown(md_structure):
    markdown = ""
    markdown_context = ""
    
    for filing, prompts in md_structure.items():
        markdown += f"# {filing}\n\n"
        markdown_context += f"# {filing}\n\n"
        prompt_id = 1
        for prompt, entries in prompts.items():
            markdown += f"## {prompt}\n\n"
            
            for i, entry in enumerate(entries, 1):
                markdown_context += f"# {filing}\n\n"
                markdown_context += f"## {prompt}\n\n"
                markdown += f"### Chunk size - {entry['vectorstore_config'][0]}; Chunk overlap - {entry['vectorstore_config'][1]}; k - {entry['vectorstore_config'][2]};\n\n"
                markdown_context += f"### Chunk size - {entry['vectorstore_config'][0]}; Chunk overlap - {entry['vectorstore_config'][1]}; k - {entry['vectorstore_config'][2]};\n\n"
                markdown += f"- **Cost**: {entry['cost']}\n"
                markdown += f"- **Total Tokens**: {entry['tokens_total']}\n"
                markdown += f"- **Prompt Tokens**: {entry['tokens_prompt']}\n"
                markdown += f"- **Output Tokens**: {entry['tokens_output']}\n"
                # markdown += f"- **Vectorstore Config**: {entry['vectorstore_config']}\n"
                markdown += f"- **Output**: \n{entry['output']}\n\n"
                markdown_context += "- **Context**: \n\n"

                for i, context in enumerate(entry["context"], 1):
                    markdown_context += f" {i}: {context}\n\n"
                with open("{}/contexts/{}_prompt{}_{}_{}_{}.md".format(output_path, filing, prompt_id, entry['vectorstore_config'][0],entry['vectorstore_config'][1],entry['vectorstore_config'][2]), "w", encoding="utf-8") as md_file:
                    print("write")
                    md_file.write(markdown_context)
                    markdown_context = ""
            markdown += "\n\n\n\n"

            with open("{}/{}_prompt{}.md".format(output_path, filing, prompt_id), "w", encoding="utf-8") as md_file:
                md_file.write(markdown)
                markdown = ""
            prompt_id += 1
                
    return markdown


md_structure = data_extractor()
# Generate markdown
markdown_output = generate_markdown(md_structure)

# # Write markdown to a file
# with open("performance_test_9-21.md", "w", encoding="utf-8") as md_file:
#     md_file.write(markdown_output)

def extract_vectorstore_vs_key(md_structure, key):
    data = []
    for filing, prompts in md_structure.items():
        for prompt, entries in prompts.items():
            for entry in entries:
                data.append([entry['vectorstore_config'], entry[key]])
    return data


def save_to_csv(filename, header, data):
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)
        writer.writerows(data)


for key in ["cost", 
            "tokens_total",
            "tokens_prompt",
            "tokens_output"
            ]:
    table_data = extract_vectorstore_vs_key(md_structure, key)
    save_to_csv('tables/vectorstore_vs_{}.csv'.format(key), ['Vectorstore Config', key], table_data)
from dotenv import load_dotenv

load_dotenv(".env")

import google.generativeai as genai
import os

genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
from server.dashboard.utils.secedgar import FilingObject, get_sec_filing_object
import tiktoken

filing_object = FilingObject(ticker="PLUG", filing_year="2024", filing_type="10-K", filing_date="2024-02-29")

def generate_filing_digest(filing_object : FilingObject):
    filing_md = get_sec_filing_object(filing_object).markdown

    def count_tokens(text, model_name='gpt-4o-mini'):
        encoding = tiktoken.encoding_for_model(model_name)
        tokens = encoding.encode(text)
        return len(tokens)

    token_count = count_tokens(filing_md)
    print("Filing tokens: ", token_count)

    from langchain_core.prompts import ChatPromptTemplate

    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(f"You are given a SEC filing. Return overview of the filing as well as List of buy and sell indicators in a markdown format.\nFiling: {filing_md}")

    with open(f"{filing_object.ticker}_{filing_object.filing_date}_{filing_object.filing_type}_filing_digest.md", "w") as md_file:
        md_file.write(response.text)

if __name__ == "__main__":
    filing_object = FilingObject(ticker="PLUG", filing_year="2024", filing_type="10-K", filing_date="2024-02-29")
    generate_filing_digest(filing_object)




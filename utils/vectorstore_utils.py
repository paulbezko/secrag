import os
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader, JSONLoader
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from utils.sec_utils import *
from utils.htm_to_markdown import sec_to_md_from_html
from utils.debug import debug_print

load_dotenv(".env", override=True) 
        
def vectorstore_manager(custom_company_filing):
    vectorstore_dir = "memory/vectorstore/"+custom_company_filing.ticker+"_"+custom_company_filing.file_number
    print("Vectorstore:",vectorstore_dir)
    embeddings = OpenAIEmbeddings()
    if os.path.exists(vectorstore_dir):
        vectorstore = FAISS.load_local(vectorstore_dir, embeddings=embeddings, allow_dangerous_deserialization=True)
    else:
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=4000, chunk_overlap=500, length_function=len)
        md_text = sec_to_md_from_html(custom_company_filing.html)
        chunks = text_splitter.split_text(text=md_text)
        vectorstore = FAISS.from_texts(chunks, embedding=embeddings)
        vectorstore.save_local(vectorstore_dir)
    return vectorstore
        



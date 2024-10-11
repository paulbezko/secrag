import os
from typing import Union

from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter, MarkdownTextSplitter
from .sec_utils import *
from .debug import debug_print

# Get the current directory of the script
current_dir = os.path.dirname(os.path.abspath(__file__))

# Go one level up (parent directory)
parent_dir = os.path.dirname(current_dir)

# Convert to string if needed
parent_dir = str(parent_dir)

load_dotenv(".env", override=True) 

# supported_text_splitters = ["recursive_character", "markdown", "edgartools"]
supported_text_splitters = ["edgartools"]

def vectorstore_manager(
        filing : FilingInfo, 
        new_chat : bool,

        # Optional args
        
        chunk_size = 10000, 
        chunk_overlap = 3, 
        k = 1, 
        table_prepend_k = 3, 
        splitter_mode = "edgartools"
    ):
    """
    Manages vectorstore for a given filing and configuration.

    Args:
        filing (CustomCompanyFiling): The filing object to be converted.
        chunk_size (int, optional): The maximum size of each chunk. Defaults to 5000.
        chunk_overlap (int, optional): The number of rows to overlap between chunks. Defaults to 1000.
        k (int, optional): The number of similar documents to return. Defaults to 1.
        table_prepend_k (int, optional): The number of rows to prepend to each table chunk. Defaults to 3.
        splitter_mode (str, optional): The text splitter to use. Defaults to "edgartools".

    Returns:
        FAISS: The vectorstore object.
    """

    # Initialize metadata model
    metadata_model = {
        "ticker": filing.ticker, 
        "date": filing.filing_date,
        "form": filing.filing_type,
        "year": filing.filing_year,
        "chunk_size": chunk_size,
        "chunk_overlap": chunk_overlap,
        "table_prepend_k": table_prepend_k
    }
    print("METADATA MODEL VECTORSTORE:", metadata_model)
    
    # Only work with supported modes
    if splitter_mode not in supported_text_splitters:
        raise Exception("Unsupported splitter_mode - {}. Currently supported modes - {}".format(splitter_mode, supported_text_splitters))
    

    vectorstore_dir = parent_dir + "/memory/vectorstore"
    embeddings = OpenAIEmbeddings()

    # Check if vectorstore exists
    if os.path.exists(vectorstore_dir):
        # Load vectorstore
        vectorstore = FAISS.load_local(vectorstore_dir, embeddings=embeddings, allow_dangerous_deserialization=True)
        # Check if embedding already exists for a given filing and embedding config
        if new_chat:
            check_for_existing_embeddings = vectorstore.similarity_search("", k=3, filter=metadata_model)
            # Case when embedding does not exist
            if len(check_for_existing_embeddings) == 0:
                filing_object_for_embedding = load_sec_thread_limited(filing)
                # Add new embedding
                chunks = filing_object_for_embedding.as_documents(chunk_size, chunk_overlap, table_prepend_k)
                vectorstore.add_documents(chunks)
                vectorstore.save_local(vectorstore_dir)
                print(f"Updated Grand-vectorstore for {filing.ticker}-{filing.filing_date}, {chunk_size}, {chunk_overlap}, {table_prepend_k}")
            # Case when embedding already exists       
            else:
                print(f"Embedding already exists for {filing.ticker}-{filing.filing_date}, {chunk_size}, {chunk_overlap}, {table_prepend_k}")

    # Create vectorstore if it doesn't exist
    else:
        # Create new embedding and vectorstore, and save the vectorstore 
        filing_object_for_embedding = load_sec_thread_limited(filing)
        chunks = filing_object_for_embedding.as_documents(chunk_size, chunk_overlap, table_prepend_k)
        vectorstore = FAISS.from_documents(chunks, embedding=embeddings)
        vectorstore.save_local(vectorstore_dir)
        print(f"Created Grand-vectorstore, added {filing.ticker}-{filing.filing_date}, {chunk_size}, {chunk_overlap}, {table_prepend_k}")

    return vectorstore


# def vectorstore_manager_legacy(custom_company_filing, chunk_size = 5000, chunk_overlap = 1000, k = 1, table_prepend_k = 3, splitter_mode = "edgartools"):
#     if splitter_mode not in supported_text_splitters:
#         raise Exception("Unsupported splitter_mode - {}. Currently supported modes - {}".format(splitter_mode, supported_text_splitters))
    
#     vectorstore_dir = "memory/vectorstore/"+custom_company_filing.ticker+"_"+custom_company_filing.file_number+"_"+splitter_mode+"_CS"+str(chunk_size)+"_CO"+str(chunk_overlap)+"table_K"+str(table_prepend_k)
#     print("Vectorstore:",vectorstore_dir)
#     embeddings = OpenAIEmbeddings()
#     if os.path.exists(vectorstore_dir):
#         vectorstore = FAISS.load_local(vectorstore_dir, embeddings=embeddings, allow_dangerous_deserialization=True)
#     else:

#         if splitter_mode == "recursive_character": 
#             text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap, length_function=len)
#             md_text = filing_md_beautifier(custom_company_filing.markdown)
#             chunks = text_splitter.split_text(text=md_text)
#             vectorstore = FAISS.from_texts(chunks, embedding=embeddings)
        
#         elif splitter_mode == "markdown":         
#             text_splitter = MarkdownTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap, length_function=len)
#             md_text = filing_md_beautifier(custom_company_filing.markdown)
#             chunks = text_splitter.split_text(text=md_text)
#             vectorstore = FAISS.from_texts(chunks, embedding=embeddings)

#         elif splitter_mode == "edgartools":         
#             chunks = custom_company_filing.as_documents(chunk_size, chunk_overlap, table_prepend_k)
#             vectorstore = FAISS.from_documents(chunks, embedding=embeddings)
        
#         vectorstore.save_local(vectorstore_dir)
#         print("Saved")
#     return vectorstore
        





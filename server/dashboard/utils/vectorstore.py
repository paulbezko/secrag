from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from ...general.utils import log
from .secedgar import FilingObject, get_sec_filing_object

import os


# Getting vectorstore
def get_vectorstore(
        filing : FilingObject, 
        new_chat : bool,

        # Optional args
        chunk_size = 10000, 
        chunk_overlap = 3, 
        table_prepend_k = 3, 
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
    chunk_metadata_model = {
        "ticker": filing.ticker, 
        "date": filing.filing_date,
        "form": filing.filing_type,
        "year": filing.filing_year,
        "chunk_description": "",
        "chunk_size": chunk_size,
        "chunk_overlap": chunk_overlap,
        "table_prepend_k": table_prepend_k
    }

    vectorstore_dir = "database/vectorstore"
    embeddings = OpenAIEmbeddings()

    # Check if vectorstore exists
    if os.path.exists(vectorstore_dir):

        # Load vectorstore
        vectorstore = FAISS.load_local(vectorstore_dir, embeddings=embeddings, allow_dangerous_deserialization=True)

        # Check if embedding already exists for a given filing and embedding config
        if new_chat:
            check_for_existing_embeddings = vectorstore.similarity_search("", k=3, filter=chunk_metadata_model)
            # Case when embedding does not exist
            if len(check_for_existing_embeddings) == 0:
                sec_filing_object = get_sec_filing_object(filing)
                chunks = sec_filing_object.get_documents(chunk_size, chunk_overlap, table_prepend_k)
                vectorstore.add_documents(chunks)
                vectorstore.save_local(vectorstore_dir)
                log('debug', f"Updated Vectorstore for {filing.ticker}-{filing.filing_date}, {chunk_size}, {chunk_overlap}, {table_prepend_k}")
            # Case when embedding already exists       
            else:
                log('debug', f"Embedding already exists for {filing.ticker}-{filing.filing_date}, {chunk_size}, {chunk_overlap}, {table_prepend_k}")

    # Create vectorstore if it doesn't exist
    else:
        # Create new embedding and vectorstore, and save the vectorstore 
        sec_filing_object = get_sec_filing_object(filing)
        chunks = sec_filing_object.get_documents(chunk_size, chunk_overlap, table_prepend_k)
        vectorstore = FAISS.from_documents(chunks, embedding=embeddings)
        vectorstore.save_local(vectorstore_dir)
        log('info', f"Created Vectorstore for {filing.ticker}-{filing.filing_date}")

    return vectorstore
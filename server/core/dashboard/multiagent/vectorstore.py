import asyncio
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
# from globals import embeddings_queue, config
# from helpers import log
# from secedgar import FilingObject, get_sec_filing_object

import os


class VectorstoreManager:
    
    vectorstore_dir = "server/core/dashboard/multiagent/filing_database/vectorstore"
    def __init__(self) -> FAISS:
        self.vectorstore = self.get_vectorstore()

    # Getting vectorstore
    def get_vectorstore(
            self
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
        embeddings = OpenAIEmbeddings()
        # Check if vectorstore exists
        if os.path.exists(self.vectorstore_dir):

            # Load vectorstore
            vectorstore = FAISS.load_local(self.vectorstore_dir, embeddings=embeddings, allow_dangerous_deserialization=True)
            
        # Create vectorstore if it doesn't exist
        else:
            # Create new embedding and vectorstore, and save the vectorstore 
            init_document_list = [Document(page_content="", metadata={"chunk_description":"init"})]
            vectorstore = FAISS.from_documents(init_document_list, embedding=embeddings)
            vectorstore.save_local(self.vectorstore_dir)

        return vectorstore
    
vectorstore_manager = VectorstoreManager()
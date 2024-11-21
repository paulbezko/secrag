import asyncio
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from ...general.utils import log
from ...globals import embeddings_queue
from .secedgar import FilingObject, get_sec_filing_object
from celery import Celery

import os


celery_app = Celery('tasks', broker='redis://localhost:6379/0', backend=None)

class VectorstoreManager:
    
    vectorstore_dir = "database/vectorstore"
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
            # log('info', f"Created Vectorstore")
        return vectorstore
    
    async def new_chat(
        self,
        filing : FilingObject, 
        # Optional args
        chunk_size = 10000, 
        chunk_overlap = 3, 
        table_prepend_k = 3,
        ):

        chunk_metadata_model = {
            "ticker": filing.ticker, 
            "date": filing.filing_date,
            "form": filing.filing_type,
            "year": filing.filing_year,
            # "chunk_description": "",
            "chunk_size": chunk_size,
            "chunk_overlap": chunk_overlap,
            "table_prepend_k": table_prepend_k
        }

        check_for_existing_embeddings = self.vectorstore.similarity_search("", k=3, filter=chunk_metadata_model, fetch_k=100000)

        # Case when embedding does not exist
        if len(check_for_existing_embeddings) == 0:
            # Filing identifier for the queue
            queue_id = filing.ticker+filing.filing_type+filing.filing_date
            
            if queue_id not in embeddings_queue:
                # Anounce filing in the queue
                embeddings_queue.append(queue_id)

                await self._perform_embedding(filing.to_dict(), chunk_size, chunk_overlap, table_prepend_k)
                # Release from queue
                embeddings_queue.remove(queue_id)

                log('debug', f"Updated Vectorstore for {filing.ticker}-{filing.filing_date}, {chunk_size}, {chunk_overlap}, {table_prepend_k}")
            else:
                # Loop until the filing is released from the queue
                while queue_id in embeddings_queue:
                    await asyncio.sleep(0)

        # Case when embedding already exists       
        else:
            log('debug', f"Embedding already exists for {filing.ticker}-{filing.filing_date}, {chunk_size}, {chunk_overlap}, {table_prepend_k}")


    async def _perform_embedding(self, filing_data, chunk_size, chunk_overlap, table_prepend_k):
        filing = FilingObject.from_dict(filing_data)
        sec_filing_object = await get_sec_filing_object(filing)
        chunks = await sec_filing_object.get_documents(chunk_size, chunk_overlap, table_prepend_k)
        await self.vectorstore.aadd_documents(chunks)

        self.vectorstore.save_local(self.vectorstore_dir)

vectorstore_manager = VectorstoreManager()
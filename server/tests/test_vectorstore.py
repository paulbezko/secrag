from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

vectorstore_dir = "server/memory/vectorstore"
embeddings = OpenAIEmbeddings()

chunk_metadata_model = {
    "ticker": "AAPL", 
    "year": "2010",
    "chunk_size": "10000",
    "chunk_overlap": "3",
    "table_prepend_k": "3",
    "chunk_description": "balance_sheet",
}

vectorstore = FAISS.load_local(vectorstore_dir, embeddings=embeddings, allow_dangerous_deserialization=True)

list_retrieved_chunks = vectorstore.similarity_search("", k=1, fetch_k=1000)

print(list_retrieved_chunks)
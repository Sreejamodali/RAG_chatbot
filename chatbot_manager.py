import os
from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema import Document
from database_manager import DatabaseManager
from docx import Document as DocxDocument
from langchain_community.document_loaders import CSVLoader, UnstructuredExcelLoader
from llama_index.core import SimpleDirectoryReader, ServiceContext
from llama_index.core.node_parser import SimpleNodeParser
from langchain_community.embeddings import OllamaEmbeddings

class ChatbotManager:
    def __init__(
        self,
        folder_path: str,
        model_name: str = "llama3:latest",
        device: str = "cpu",
        encode_kwargs: dict = {"normalize_embeddings": True},
        llm_model: str = "llama3",
        llm_temperature: float = 0.7,
        qdrant_url: str = "http://localhost:6333",
        collection_name: str = "vector_db",
    ):
        self.folder_path = folder_path
        self.model_name = model_name
        self.device = device
        self.encode_kwargs = encode_kwargs
        self.llm_model = llm_model
        self.llm_temperature = llm_temperature
        self.qdrant_url = qdrant_url
        self.collection_name = collection_name
        self.prompt_template = PromptTemplate(
            input_variables=["context", "query"],
            template="""Use the following pieces of information to answer the user's question.
            If you don't know the answer, just say that you don't know, don't try to make up an answer.

            Context: {context}
            Query: {query}

            Only return the helpful answer. Answer must be detailed and well explained.
            Helpful answer:"""
        )

        self.db_manager = DatabaseManager(model_name, device, encode_kwargs, qdrant_url, collection_name)
        self.qa = RetrievalQA.from_chain_type(
            llm=ChatOllama(model=self.llm_model, temperature=self.llm_temperature),
            chain_type="stuff",
            retriever=self.db_manager.get_db().as_retriever()
        )

    
    def load_and_split_documents(self):
        print("Loading and splitting using LlamaParse-compatible reader...")
        
        # Load documents (supports .csv, .xlsx, .txt, etc.)
        reader = SimpleDirectoryReader(input_dir=self.folder_path)
        documents = reader.load_data()

        # Embed model
        embed_model = OllamaEmbeddings(model="nomic-embed-text")
        self.service_context = ServiceContext.from_defaults(embed_model=embed_model)

        # Split using LlamaIndex's parser
        parser = SimpleNodeParser()
        nodes = parser.get_nodes_from_documents(documents)
        
        print(f"Adding {len(nodes)} nodes to the vector store...")
        self.db_manager.get_db().add_documents(nodes)

        # Now split the documents
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=100)
        splits = text_splitter.split_documents(documents)

        texts = [split.page_content for split in splits][:100]
        print(f"Adding {len(texts)} text chunks to the vector store...")
        self.db_manager.get_db().add_texts(texts)


    def get_response(self, query: str) -> str:
        if query.lower() == "exit":
            print("Exiting session.")
            return "Session closed."
        
        # Retrieve context based on the query
        context = self.qa.invoke(query)
        
        # Use the prompt template to format the input for the LLM
        formatted_prompt = self.prompt_template.format(context=context, query=query)
        
        # Generate the response using the LLM
        response = self.qa.invoke(formatted_prompt)
        
        # Extract the helpful answer from the response
        if isinstance(response, dict) and 'result' in response:
            return response['result']
        else:
            return "Sorry, I couldn't generate a valid response."
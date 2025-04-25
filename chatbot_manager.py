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
        documents = []
        print("loading and splitting documents")

        # Check if input is a file or a directory
        if os.path.isfile(self.folder_path):
            filenames = [os.path.basename(self.folder_path)]
            folder = os.path.dirname(self.folder_path)
        else:
            filenames = os.listdir(self.folder_path)
            folder = self.folder_path

        for filename in filenames:
            full_path = os.path.join(folder, filename)

            if filename.endswith('.pdf'):
                loader = PyPDFLoader(full_path)
                documents.extend(loader.load())

            elif filename.endswith('.docx'):
                doc = DocxDocument(full_path)
                texts = [para.text for para in doc.paragraphs if para.text.strip()]
                documents.extend([Document(page_content=text) for text in texts])

            elif filename.endswith('.csv'):
                print(f"Loading CSV file: {filename}")
                loader = CSVLoader(file_path=full_path)
                csv_data = loader.load()
                #print("CSV Data Sample:", csv_data[:1])
                documents.extend(csv_data)

            elif filename.endswith('.xlsx') or filename.endswith('.xls'):
                print(f"Loading Excel file: {filename}")
                loader = UnstructuredExcelLoader(file_path=full_path)
                documents.extend(loader.load())

            else:
                print(f"Unsupported file format: {filename}")

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
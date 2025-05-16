import os
import google.generativeai as genai
from flask import Flask, request, jsonify
from flask_cors import CORS
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
import time
from tenacity import retry, stop_after_attempt, wait_exponential, before_log, after_log
import pickle
import os.path
import logging
import sys

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set up Flask app
app = Flask(__name__)
CORS(app)

# Set up Google API key
os.environ["GOOGLE_API_KEY"] = "AIzaSyCJlefBe70vjVMPIAQvjyfJLDa6T_FfWRc"

# Initialize Gemini model using LangChain's wrapper
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro",
    temperature=0,
    google_api_key=os.environ["GOOGLE_API_KEY"],
)

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=60),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.INFO)
)
def create_embeddings(chunks):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    total_chunks = len(chunks)
    logger.info(f"Starting embedding creation for {total_chunks} chunks...")
    
    try:
        vector_store = FAISS.from_documents(chunks, embeddings)
        logger.info("Successfully created embeddings for all chunks")
        return vector_store
    except Exception as e:
        logger.error(f"Error creating embeddings: {str(e)}")
        raise

def load_and_process_docs(folder_path="quran_docs/", force_reload=False):
    vector_store_path = "vector_store.pkl"
    
    # Try to load existing vector store
    if not force_reload and os.path.exists(vector_store_path):
        logger.info("Loading existing vector store...")
        try:
            with open(vector_store_path, "rb") as f:
                return pickle.load(f)
        except Exception as e:
            logger.error(f"Error loading vector store: {str(e)}")
            logger.info("Will recreate vector store...")
    
    logger.info("Starting PDF processing...")
    os.makedirs(folder_path, exist_ok=True)
    
    docs = []
    if not os.path.exists(folder_path) or not any(f.endswith('.pdf') for f in os.listdir(folder_path)):
        logger.error(f"No PDF files found in {folder_path}")
        return None
    
    # Process PDFs
    pdf_files = [f for f in os.listdir(folder_path) if f.endswith('.pdf')]
    total_files = len(pdf_files)
    
    for idx, file in enumerate(pdf_files, 1):
        logger.info(f"Processing file {idx}/{total_files}: {file}")
        try:
            loader = PyPDFLoader(os.path.join(folder_path, file))
            docs.extend(loader.load())
        except Exception as e:
            logger.error(f"Error processing {file}: {str(e)}")
            continue
    
    # Split documents
    text_splitter = CharacterTextSplitter(chunk_size=2000, chunk_overlap=400)
    chunks = text_splitter.split_documents(docs)
    logger.info(f"Created {len(chunks)} chunks from {total_files} documents")
    
    # Create embeddings
    logger.info("Creating embeddings... This may take a while.")
    vector_store = create_embeddings(chunks)
    
    # Save vector store
    logger.info("Saving vector store...")
    try:
        with open(vector_store_path, "wb") as f:
            pickle.dump(vector_store, f)
        logger.info("Vector store saved successfully")
    except Exception as e:
        logger.error(f"Error saving vector store: {str(e)}")
    
    return vector_store

# Load the vector store once
logger.info("Initializing vector store...")
vector_store = load_and_process_docs()

if vector_store is None:
    logger.error("Failed to initialize vector store. Exiting...")
    sys.exit(1)

# Create the RAG chain
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vector_store.as_retriever()
)

# Chat memory storage
chat_memory = {}

@app.route('/chat', methods=['POST'])
def chat():
    try:
        payload = request.get_json()
        chat_id = payload.get('chat_id', 'default')
        user_message = payload.get('message')
        
        if not user_message:
            return jsonify({"error": "No message provided"}), 400

        history = chat_memory.get(chat_id, [])
        history.append({"role": "user", "content": user_message})

        response = qa_chain.run(user_message)
        
        history.append({"role": "assistant", "content": response})
        chat_memory[chat_id] = history[-20:]
        
        return jsonify({"response": response})
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/')
def index():
    return app.send_static_file('index.html')

app.static_folder = 'static'

if __name__ == '__main__':
    logger.info("Starting Flask server...")
    app.run(host='0.0.0.0', port=8080, debug=True)
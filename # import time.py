# import time
# from dotenv import load_dotenv
# from google.api_core.exceptions import ResourceExhausted
# from flask import Flask, request, jsonify
# from flask_cors import CORS
# from langchain_community.document_loaders import PyPDFLoader
# from langchain.text_splitter import CharacterTextSplitter
# from langchain_community.vectorstores import FAISS
# from langchain.chains import RetrievalQA
# from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI

# # Load environment variables
# load_dotenv()

# # Set up Flask app
# app = Flask(__name__)
# CORS(app)

# # Load API key
# GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
# if not GOOGLE_API_KEY:
#     raise ValueError("GOOGLE_API_KEY not set. Ensure .env file exists with the key.")

# # Initialize Gemini model
# llm = ChatGoogleGenerativeAI(
#     model="gemini-1.5-pro",
#     temperature=0,
#     google_api_key=GOOGLE_API_KEY,
# )

# # Load and process PDFs
# def load_and_process_docs(folder_path="quran_docs/", faiss_index_path="faiss_index"):
#     try:
#         # Check if FAISS index exists
#         embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
#         if os.path.exists(faiss_index_path):
#             print(f"Loading existing FAISS index from {faiss_index_path}...")
#             return FAISS.load_local(faiss_index_path, embeddings, allow_dangerous_deserialization=True)

#         # Create directory if it doesn't exist
#         os.makedirs(folder_path, exist_ok=True)
        
#         docs = []
#         if not os.path.exists(folder_path) or not any(f.endswith('.pdf') for f in os.listdir(folder_path)):
#             print(f"Warning: No PDF files found in {folder_path}")
#             return None
        
#         # Process PDFs with page limit
#         pdf_files = [f for f in os.listdir(folder_path) if f.endswith('.pdf')]
#         max_pages_per_pdf = 50
        
#         for file in pdf_files:
#             try:
#                 print(f"Processing {file}...")
#                 loader = PyPDFLoader(os.path.join(folder_path, file))
#                 doc_pages = loader.load()[:max_pages_per_pdf]
#                 docs.extend(doc_pages)
#                 print(f"Loaded {len(doc_pages)} pages from {file}")
#                 time.sleep(1)
#             except Exception as e:
#                 print(f"Error loading {file}: {str(e)}")
#                 continue
        
#         if not docs:
#             print("No documents loaded")
#             return None
            
#         # Split documents into chunks
#         text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
#         chunks = text_splitter.split_documents(docs)
        
#         # Limit chunks to avoid API overload
#         max_chunks = 500
#         if len(chunks) > max_chunks:
#             print(f"Limiting chunks from {len(chunks)} to {max_chunks}")
#             chunks = chunks[:max_chunks]
        
#         print(f"Processing {len(chunks)} chunks...")
        
#         # Create vector store with retry logic
#         batch_size = 10
#         vector_store = None
        
#         for i in range(0, len(chunks), batch_size):
#             batch = chunks[i:i + batch_size]
#             print(f"Processing batch {i//batch_size + 1} of {(len(chunks) + batch_size - 1)//batch_size}")
            
#             for attempt in range(3):
#                 try:
#                     if vector_store is None:
#                         vector_store = FAISS.from_documents(batch, embeddings)
#                     else:
#                         vector_store.add_documents(batch)
#                     time.sleep(2)
#                     break
#                 except ResourceExhausted:
#                     if attempt < 2:
#                         print(f"Rate limit hit, retrying in {5 * (attempt + 1)} seconds...")
#                         time.sleep(5 * (attempt + 1))
#                     else:
#                         print("Max retries reached for batch")
#                         raise
#                 except Exception as e:
#                     print(f"Error processing batch {i//batch_size + 1}: {str(e)}")
#                     break
        
#         if vector_store:
#             # Save FAISS index to disk
#             print(f"Saving FAISS index to {faiss_index_path}...")
#             vector_store.save_local(faiss_index_path)
        
#         print("Document processing completed!")
#         return vector_store
#     except Exception as e:
#         print(f"Error in load_and_process_docs: {str(e)}")
#         return None

# # Load vector store
# print("Loading and processing documents...")
# vector_store = load_and_process_docs()
# if vector_store is None:
#     raise ValueError("Failed to load and process documents")

# print("Documents loaded successfully!")

# # Create RAG chain
# qa_chain = RetrievalQA.from_chain_type(
#     llm=llm,
#     chain_type="stuff",
#     retriever=vector_store.as_retriever(search_kwargs={"k": 4})
# )

# # Store chat history
# chat_memory = {}

# # Define /chat endpoint
# @app.route('/chat', methods=['POST'])
# def chat():
#     try:
#         payload = request.get_json()
#         if not payload:
#             return jsonify({"error": "No payload provided"}), 400

#         chat_id = payload.get('chat_id', 'default')
#         user_message = payload.get('message')
        
#         if not user_message:
#             return jsonify({"error": "No message provided"}), 400

#         # Update chat history
#         history = chat_memory.get(chat_id, [])
#         history.append({"role": "user", "content": user_message})

#         # Generate response
#         try:
#             response = qa_chain.run(user_message)
#         except Exception as e:
#             print(f"Error generating response: {str(e)}")
#             return jsonify({"error": "Failed to generate response"}), 500

#         # Update chat history
#         history.append({"role": "assistant", "content": response})
#         chat_memory[chat_id] = history[-20:]

#         return jsonify({"response": response})
#     except Exception as e:
#         print(f"Error in chat endpoint: {str(e)}")
#         return jsonify({"error": "An unexpected error occurred"}), 500

# # Serve HTML
# @app.route('/')
# def index():
#     return app.send_static_file('index.html')

# # Set static folder
# app.static_folder = 'static'

# # Run server
# if __name__ == '__main__':
#     print("Starting server...")
#     app.run(host='0.0.0.0', port=8080, debug=True)
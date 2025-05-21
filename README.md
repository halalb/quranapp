Quran Chat
A conversational Q&A application powered by Google’s Gemini model and LangChain for Retrieval-Augmented Generation (RAG) over Quran PDF documents. The system consists of a Python/Flask backend that ingests and indexes PDFs into a FAISS vector store, and a simple HTML/CSS/JavaScript frontend for an interactive chat interface.

Features
RAG-based QA: Uses LangChain and Google Gemini to answer questions by retrieving relevant Quran passages.

PDF loader: Automatically processes all PDFs in the quran_docs/ folder.

Embeddings & Vector Store: Generates embeddings with Google’s embedding API and indexes them in FAISS.

Chat history: Maintains per-session chat history (up to the last 20 messages).

Frontend UI: A clean, responsive chat interface built with HTML, CSS, and vanilla JavaScript.


# rag_updated.py

import os
import requests
from dotenv import load_dotenv
import chromadb
from chromadb.utils import embedding_functions
import PyPDF2
from typing import List, Dict
import json

# Load environment variables
load_dotenv()

class SimpleRAG:
    def __init__(self):
        # Initialize DeepSeek API
        self.api_key = os.getenv('DEEPSEEK_API_KEY')
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
        
        # Initialize ChromaDB with persistent storage
        self.chroma_client = chromadb.PersistentClient(path="./chroma_db")
        
        # Use ChromaDB's built-in sentence transformer embedding function
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        
        # Create or get collection
        try:
            self.collection = self.chroma_client.get_collection(
                name="documents",
                embedding_function=self.embedding_fn
            )
        except:
            self.collection = self.chroma_client.create_collection(
                name="documents",
                embedding_function=self.embedding_fn
            )
        
        # Store documents for reference
        self.documents = []
        
    def load_documents_from_text(self, texts: List[str], metadata: List[Dict] = None):
        """
        Load text documents into the vector database
        """
        if metadata is None:
            metadata = [{"source": f"doc_{i}"} for i in range(len(texts))]
        
        # Generate unique IDs
        ids = [f"doc_{i}_{hash(text)}" for i, text in enumerate(texts)]
        
        # Add documents to collection
        self.collection.add(
            documents=texts,
            metadatas=metadata,
            ids=ids
        )
        
        # Store in local list for reference
        for text, meta in zip(texts, metadata):
            self.documents.append({"text": text, "metadata": meta})
        
        print(f"Loaded {len(texts)} documents into the vector store")
        return len(texts)
    
    def load_pdf(self, pdf_path: str, chunk_size: int = 1000):
        """
        Extract text from PDF and load into vector store with chunking
        """
        texts = []
        metadata = []
        
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num, page in enumerate(pdf_reader.pages):
                    text = page.extract_text()
                    if text.strip():
                        # Split long pages into chunks
                        if len(text) > chunk_size:
                            chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
                            for chunk_num, chunk in enumerate(chunks):
                                if chunk.strip():
                                    texts.append(chunk)
                                    metadata.append({
                                        "source": os.path.basename(pdf_path),
                                        "page": page_num + 1,
                                        "chunk": chunk_num + 1
                                    })
                        else:
                            texts.append(text)
                            metadata.append({
                                "source": os.path.basename(pdf_path),
                                "page": page_num + 1
                            })
            
            if texts:
                self.load_documents_from_text(texts, metadata)
                print(f"Successfully loaded {len(texts)} chunks from PDF")
            else:
                print("No text extracted from PDF")
                
        except Exception as e:
            print(f"Error loading PDF: {str(e)}")
    
    def retrieve_relevant_context(self, query: str, n_results: int = 3) -> str:
        """
        Retrieve relevant documents for the query
        """
        if self.collection.count() == 0:
            return ""
        
        # Query the vector store
        results = self.collection.query(
            query_texts=[query],
            n_results=min(n_results, self.collection.count())
        )
        
        # Combine retrieved documents into context
        context_parts = []
        if results and results['documents'] and results['documents'][0]:
            for i, (doc, metadata) in enumerate(zip(results['documents'][0], results['metadatas'][0])):
                source_info = f"[Source: {metadata.get('source', 'Unknown')}"
                if 'page' in metadata:
                    source_info += f", Page {metadata['page']}"
                if 'chunk' in metadata:
                    source_info += f", Chunk {metadata['chunk']}"
                source_info += "]"
                context_parts.append(f"{source_info}\n{doc}\n")
        
        return "\n".join(context_parts)
    
    def query_deepseek(self, prompt: str, context: str = "") -> str:
        """
        Query DeepSeek API with context
        """
        if not self.api_key:
            return "Error: DeepSeek API key not found. Please set it in the .env file."
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Prepare the messages
        messages = []
        
        if context:
            system_message = f"""You are a helpful assistant that answers questions based on the provided context. 
            Use only the information from the context to answer questions. If the context doesn't contain 
            relevant information, say "I don't have enough information to answer this question based on the provided context."
            
            Context:
            {context}
            """
            messages.append({"role": "system", "content": system_message})
        
        messages.append({"role": "user", "content": prompt})
        
        # Prepare the request
        data = {
            "model": "deepseek-chat",
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 500
        }
        
        try:
            response = requests.post(self.api_url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        except requests.exceptions.RequestException as e:
            return f"Error connecting to DeepSeek API: {str(e)}"
        except KeyError as e:
            return f"Error parsing DeepSeek API response: {str(e)}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"
    
    def ask(self, question: str, use_rag: bool = True) -> str:
        """
        Ask a question with or without RAG
        """
        if use_rag:
            # Retrieve relevant context
            context = self.retrieve_relevant_context(question)
            
            if context:
                # Query with context
                answer = self.query_deepseek(question, context)
                return f"**Answer (with RAG):**\n{answer}\n\n**Context used:**\n{context}"
            else:
                # If no context found, query without RAG
                answer = self.query_deepseek(question)
                return f"**Answer (No relevant documents found):**\n{answer}"
        else:
            # Query without context
            answer = self.query_deepseek(question)
            return f"**Answer (without RAG):**\n{answer}"
    
    def clear_documents(self):
        """
        Clear all documents from the vector store
        """
        try:
            self.chroma_client.delete_collection("documents")
            self.collection = self.chroma_client.create_collection(
                name="documents",
                embedding_function=self.embedding_fn
            )
            self.documents = []
            print("All documents cleared")
        except Exception as e:
            print(f"Error clearing documents: {str(e)}")
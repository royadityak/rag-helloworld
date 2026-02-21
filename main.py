# main_updated.py

from rag import SimpleRAG
from data import create_sample_documents
import sys

def test_without_api_key():
    """Test the RAG system without actually calling DeepSeek API"""
    rag = SimpleRAG()
    
    # Load sample documents
    print("Loading documents into the knowledge base...")
    documents, metadata = create_sample_documents()
    rag.load_documents_from_text(documents, metadata)
    
    # Test retrieval only
    print("\n" + "="*50)
    print("Testing Document Retrieval")
    print("="*50)
    
    test_queries = [
        "What is artificial intelligence?",
        "Explain RAG",
        "Python programming"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        print("-"*30)
        context = rag.retrieve_relevant_context(query)
        if context:
            print("Retrieved Context:")
            print(context[:500] + "..." if len(context) > 500 else context)
        else:
            print("No context retrieved")
        print()

def main():
    # Initialize the RAG system
    rag = SimpleRAG()
    
    # Check if API key is set
    if not rag.api_key:
        print("WARNING: DeepSeek API key not found in .env file")
        print("The system will work for document retrieval but won't be able to query DeepSeek")
        print("Please add your API key to the .env file: DEEPSEEK_API_KEY=your_key_here")
        print("\nRunning in test mode (retrieval only)...")
        test_without_api_key()
        return
    
    # Load sample documents
    print("Loading documents into the knowledge base...")
    documents, metadata = create_sample_documents()
    rag.load_documents_from_text(documents, metadata)
    
    # Example questions
    questions = [
        "What is artificial intelligence?",
        "Explain how RAG works",
        "What programming language is good for AI?",
        "Tell me about deep learning",
        "What is NLP?"
    ]
    
    # Test both with and without RAG
    for question in questions:
        print("\n" + "="*80)
        print(f"Question: {question}")
        print("="*80)
        
        # With RAG
        print("\n" + rag.ask(question, use_rag=True))
        
        print("\n" + "-"*40)
        
        # Without RAG
        print("\n" + rag.ask(question, use_rag=False))
        
        if question != questions[-1]:
            input("\nPress Enter to continue to next question...")

if __name__ == "__main__":
    main()
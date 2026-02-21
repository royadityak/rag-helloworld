# sample_data.py

def create_sample_documents():
    """
    Create sample documents for testing
    """
    documents = [
        """Artificial Intelligence (AI) is the simulation of human intelligence in machines 
        that are programmed to think and learn. Machine learning is a subset of AI that enables 
        systems to learn and improve from experience without being explicitly programmed.""",
        
        """Deep learning is a subset of machine learning that uses neural networks with multiple 
        layers. These neural networks attempt to simulate the behavior of the human brain, 
        allowing it to learn from large amounts of data.""",
        
        """Natural Language Processing (NLP) is a branch of AI that helps computers understand, 
        interpret and manipulate human language. NLP draws from many disciplines including 
        computer science and computational linguistics.""",
        
        """RAG stands for Retrieval-Augmented Generation. It combines retrieval-based methods 
        with generative models to produce more accurate and contextually relevant responses. 
        RAG systems first retrieve relevant documents and then generate answers based on them.""",
        
        """Python is a popular programming language for AI and machine learning due to its 
        simplicity and extensive libraries like TensorFlow, PyTorch, and scikit-learn."""
    ]
    
    metadata = [
        {"topic": "AI Basics", "source": "AI Textbook"},
        {"topic": "Deep Learning", "source": "Deep Learning Guide"},
        {"topic": "NLP", "source": "NLP Tutorial"},
        {"topic": "RAG Systems", "source": "Research Paper"},
        {"topic": "Python", "source": "Programming Guide"}
    ]
    
    return documents, metadata
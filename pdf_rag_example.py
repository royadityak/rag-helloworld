# pdf_rag_example.py

from rag import SimpleRAG
import requests

def download_sample_pdf():
    """
    Download a sample PDF for testing (you can replace with your own PDF)
    """
    # This is a sample PDF URL - replace with your own PDF
    pdf_url = "https://arxiv.org/pdf/1706.03762.pdf"  # Attention Is All You Need paper
    
    response = requests.get(pdf_url)
    pdf_path = "sample_paper.pdf"
    
    with open(pdf_path, 'wb') as f:
        f.write(response.content)
    
    return pdf_path

def process_pdf_example():
    # Initialize RAG system
    rag = SimpleRAG()
    
    # Load PDF (either download or use your own)
    pdf_path = "your_document.pdf"  # Replace with your PDF path
    
    if os.path.exists(pdf_path):
        print(f"Loading PDF: {pdf_path}")
        rag.load_pdf(pdf_path)
        
        # Ask questions about the PDF
        questions = [
            "What is the main topic of this document?",
            "Summarize the key findings"
        ]
        
        for question in questions:
            print(f"\nQuestion: {question}")
            answer = rag.ask(question)
            print(f"Answer: {answer}")
    else:
        print(f"PDF not found: {pdf_path}")
        print("Please provide a valid PDF path or download one first.")

if __name__ == "__main__":
    process_pdf_example()
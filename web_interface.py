# web_interface_updated.py

from flask import Flask, request, jsonify, render_template_string
from rag import SimpleRAG
from data import create_sample_documents
import os

app = Flask(__name__)
rag = SimpleRAG()

# Load sample documents on startup
print("Loading sample documents...")
documents, metadata = create_sample_documents()
rag.load_documents_from_text(documents, metadata)

# HTML Template as a string (simpler than separate file)
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Simple RAG with DeepSeek</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background-color: white;
            border: 1px solid #ddd;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            margin-bottom: 20px;
        }
        .status {
            padding: 10px;
            margin: 10px 0;
            border-radius: 5px;
            font-size: 14px;
        }
        .status.api-ok {
            background-color: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .status.api-warning {
            background-color: #fff3cd;
            color: #856404;
            border: 1px solid #ffeeba;
        }
        input[type="text"] {
            width: 100%;
            padding: 12px;
            margin: 10px 0;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
            box-sizing: border-box;
        }
        input[type="text"]:focus {
            outline: none;
            border-color: #007bff;
            box-shadow: 0 0 5px rgba(0,123,255,0.3);
        }
        button {
            padding: 12px 30px;
            background-color: #007bff;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            transition: background-color 0.3s;
        }
        button:hover {
            background-color: #0056b3;
        }
        button:disabled {
            background-color: #ccc;
            cursor: not-allowed;
        }
        .toggle {
            margin: 15px 0;
            padding: 10px;
            background-color: #f8f9fa;
            border-radius: 5px;
        }
        .toggle label {
            margin-left: 5px;
            cursor: pointer;
        }
        .answer {
            margin-top: 20px;
            padding: 20px;
            background-color: #f8f9fa;
            border-radius: 5px;
            border-left: 4px solid #007bff;
            white-space: pre-wrap;
            font-size: 15px;
            line-height: 1.6;
        }
        .loading {
            display: none;
            text-align: center;
            margin: 10px 0;
        }
        .loading.active {
            display: block;
        }
        .stats {
            margin-top: 20px;
            padding: 10px;
            background-color: #e9ecef;
            border-radius: 5px;
            font-size: 14px;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 Simple RAG with DeepSeek</h1>
        
        <div class="status {{ 'api-ok' if api_key else 'api-warning' }}">
            <strong>Status:</strong> 
            {% if api_key %}
                ✅ DeepSeek API connected
            {% else %}
                ⚠️ DeepSeek API key not found. Running in demo mode (retrieval only).
            {% endif %}
        </div>
        
        <div class="toggle">
            <input type="checkbox" id="useRAG" checked>
            <label for="useRAG">Use RAG (Retrieval-Augmented Generation)</label>
        </div>
        
        <input type="text" id="question" placeholder="Ask a question about AI, RAG, Python..." 
               onkeypress="if(event.key === 'Enter') askQuestion()">
        <button onclick="askQuestion()" id="askBtn">Ask Question</button>
        
        <div class="loading" id="loading">
            <p>🤔 Thinking...</p>
        </div>
        
        <div class="answer" id="answer"></div>
        
        <div class="stats">
            <strong>Documents in knowledge base:</strong> {{ doc_count }}
        </div>
    </div>

    <script>
        async function askQuestion() {
            const question = document.getElementById('question').value;
            const useRAG = document.getElementById('useRAG').checked;
            const answerDiv = document.getElementById('answer');
            const loadingDiv = document.getElementById('loading');
            const askBtn = document.getElementById('askBtn');
            
            if (!question.trim()) {
                alert('Please enter a question');
                return;
            }
            
            // Show loading state
            answerDiv.innerHTML = '';
            loadingDiv.classList.add('active');
            askBtn.disabled = true;
            
            try {
                const response = await fetch('/ask', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        question: question,
                        use_rag: useRAG
                    })
                });
                
                const data = await response.json();
                
                if (data.error) {
                    answerDiv.innerHTML = '❌ Error: ' + data.error;
                } else {
                    // Format the answer
                    let formattedAnswer = data.answer;
                    if (data.context_used) {
                        formattedAnswer += '<br><br><strong>📚 Context used:</strong><br>' + 
                                          data.context_used.replace(/\\n/g, '<br>');
                    }
                    answerDiv.innerHTML = formattedAnswer;
                }
            } catch (error) {
                answerDiv.innerHTML = '❌ Error: ' + error.message;
            } finally {
                // Hide loading state
                loadingDiv.classList.remove('active');
                askBtn.disabled = false;
            }
        }
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(
        HTML_TEMPLATE, 
        api_key=bool(rag.api_key),
        doc_count=rag.collection.count()
    )

@app.route('/ask', methods=['POST'])
def ask():
    try:
        data = request.json
        question = data.get('question', '')
        use_rag = data.get('use_rag', True)
        
        if not question:
            return jsonify({'error': 'No question provided'}), 400
        
        answer = rag.ask(question, use_rag)
        
        # Extract context if present in the answer
        context_used = None
        if "**Context used:**" in answer:
            parts = answer.split("**Context used:**")
            answer = parts[0].strip()
            context_used = parts[1].strip() if len(parts) > 1 else None
        
        return jsonify({
            'answer': answer,
            'context_used': context_used,
            'use_rag': use_rag
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/stats', methods=['GET'])
def stats():
    return jsonify({
        'document_count': rag.collection.count(),
        'api_key_configured': bool(rag.api_key)
    })

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    print("🚀 Starting RAG Web Interface...")
    print(f"📚 Documents in knowledge base: {rag.collection.count()}")
    print(f"🔑 DeepSeek API: {'✅ Configured' if rag.api_key else '❌ Not configured'}")
    print("\n🌐 Open http://127.0.0.1:5000 in your browser")
    
    app.run(debug=True, port=5000)
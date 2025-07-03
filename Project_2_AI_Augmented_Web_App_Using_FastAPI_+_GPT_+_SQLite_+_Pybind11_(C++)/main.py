from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from pydantic import BaseModel
import sqlite3
import json
import os
from datetime import datetime
from typing import Optional, Literal, List, Dict, Any
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

app = FastAPI(title="AI Text Analyzer", version="1.0.0")

# Initialize OpenAI client
try:
    from openai import OpenAI
    openai_api_key = os.getenv("OPENAI_API_KEY")
    openai_base_url = os.getenv("OPENAI_BASE_URL")

    if openai_api_key:
        openai_client = OpenAI(api_key=openai_api_key, base_url=openai_base_url if openai_base_url else None)
        OPENAI_AVAILABLE = True
    else:
        OPENAI_AVAILABLE = False
        print("⚠️ Warning: OpenAI API key not found in .env. OpenAI features will be disabled.")
except ImportError:
    OPENAI_AVAILABLE = False
    print("⚠️ Warning: 'openai' library not installed. Run 'pip install openai'.")

# Initialize Gemini client
try:
    import google.generativeai as genai
    gemini_api_key = os.getenv("GEMINI_API_KEY")

    if gemini_api_key:
        genai.configure(api_key=gemini_api_key)
        # Test the connection with a simple model initialization
        try:
            # Try the newer model names first
            test_model = genai.GenerativeModel('gemini-1.5-flash')
            GEMINI_AVAILABLE = True
            GEMINI_MODEL_NAME = 'gemini-1.5-flash'
            print("✅ Gemini client initialized successfully with gemini-1.5-flash")
        except Exception as model_error:
            try:
                # Fallback to gemini-1.5-pro
                test_model = genai.GenerativeModel('gemini-1.5-pro')
                GEMINI_AVAILABLE = True
                GEMINI_MODEL_NAME = 'gemini-1.5-pro'
                print("✅ Gemini client initialized successfully with gemini-1.5-pro")
            except Exception as fallback_error:
                try:
                    # Last fallback to gemini-pro (legacy)
                    test_model = genai.GenerativeModel('gemini-pro')
                    GEMINI_AVAILABLE = True
                    GEMINI_MODEL_NAME = 'gemini-pro'
                    print("✅ Gemini client initialized successfully with gemini-pro (legacy)")
                except Exception as legacy_error:
                    GEMINI_AVAILABLE = False
                    GEMINI_MODEL_NAME = None
                    print(f"⚠️ Warning: Gemini API key found but model initialization failed.")
                    print(f"   Model errors: {str(model_error)[:100]}...")
                    print(f"   This might be due to API key restrictions or regional limitations.")
    else:
        GEMINI_AVAILABLE = False
        GEMINI_MODEL_NAME = None
        print("⚠️ Warning: Gemini API key not found in .env. Gemini features will be disabled.")
except ImportError:
    GEMINI_AVAILABLE = False
    GEMINI_MODEL_NAME = None
    print("⚠️ Warning: 'google-generativeai' library not installed. Run 'pip install google-generativeai'.")

# Try to import C++ module, with a clear fallback
try:
    import text_analyzer  # Our C++ module compiled via setup.py
    CPP_MODULE_AVAILABLE = True
    print("✅ C++ 'text_analyzer' module loaded successfully.")
except ImportError:
    CPP_MODULE_AVAILABLE = False
    print("🛑 CRITICAL: C++ 'text_analyzer' module not found.")
    print("   Please run the build script: 'pip install .'")
    print("   Using pure Python fallback for now.")

# --- Database Setup ---
DB_FILE = 'analyzer.db'

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            cpp_result TEXT NOT NULL,
            ai_suggestions TEXT,
            ai_provider TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# --- Fallback & Helper Functions ---

def python_text_analysis(text: str) -> dict:
    """Python fallback for text analysis when C++ module is not available."""
    import re
    words = text.split()
    word_count = len(words)
    sentences = re.split(r'[.!?]+', text)
    sentence_count = len([s for s in sentences if s.strip()])
    
    if sentence_count > 0:
        avg_words_per_sentence = word_count / sentence_count
        readability_score = max(0, min(1, (20 - avg_words_per_sentence) / 20))
    else:
        readability_score = 0.5

    positive_words = {'good', 'great', 'excellent', 'amazing', 'love', 'happy', 'success'}
    negative_words = {'bad', 'terrible', 'awful', 'hate', 'sad', 'negative', 'failure'}
    
    positive_count = sum(1 for word in words if word.lower() in positive_words)
    negative_count = sum(1 for word in words if word.lower() in negative_words)
    
    sentiment_score = 0.5
    if positive_count + negative_count > 0:
        sentiment_score = positive_count / (positive_count + negative_count)

    return {
        'word_count': word_count,
        'sentence_count': sentence_count,
        'readability_score': readability_score,
        'sentiment_score': sentiment_score
    }

async def get_openai_suggestions(text: str, cpp_result: dict) -> str:
    """Get suggestions from OpenAI GPT."""
    if not OPENAI_AVAILABLE:
        return "OpenAI not available. Mock suggestion: To improve this text, consider adding more descriptive adjectives and varying sentence length."

    try:
        prompt = f"""Analyze the following text and provide 3 specific, actionable suggestions to improve its clarity, engagement, and readability.
Base your suggestions on the provided metrics.

Text:
"{text}"

Metrics:
- Word count: {cpp_result.get('word_count', 0)}
- Sentence count: {cpp_result.get('sentence_count', 0)}
- Readability score (0-1): {cpp_result.get('readability_score', 0):.2f}
- Sentiment score (0-1): {cpp_result.get('sentiment_score', 0):.2f}

Your suggestions:"""
        
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a professional writing coach. Provide concise, actionable feedback."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200, temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"OpenAI API Error. Mock Suggestion: Refine sentence structure for better flow. (Error: {str(e)})"

async def get_gemini_suggestions(text: str, cpp_result: dict) -> str:
    """Get suggestions from Google Gemini."""
    if not GEMINI_AVAILABLE or not GEMINI_MODEL_NAME:
        return "Gemini not available. Mock suggestion: To enhance this text, try using more vivid verbs and checking for repetitive phrasing."

    try:
        model = genai.GenerativeModel(GEMINI_MODEL_NAME)
        prompt = f"""As a writing coach, analyze this text and provide 3 concise, actionable improvement suggestions based on the metrics.

Text: "{text}"

Metrics:
- Word count: {cpp_result.get('word_count', 0)}
- Sentence count: {cpp_result.get('sentence_count', 0)}
- Readability (0-1): {cpp_result.get('readability_score', 0):.2f}
- Sentiment (0-1): {cpp_result.get('sentiment_score', 0):.2f}

Suggestions:"""

        # Try async first, fallback to sync if not available
        try:
            response = await model.generate_content_async(prompt)
        except AttributeError:
            # Some versions might not have async support
            response = model.generate_content(prompt)

        return response.text.strip()
    except Exception as e:
        error_msg = str(e)
        if "User location is not supported" in error_msg:
            return "Gemini API Error: Your location may not be supported for Gemini API access. Mock Suggestion: Consider varying sentence structure and using more descriptive language."
        elif "API key" in error_msg.lower():
            return "Gemini API Error: Invalid API key. Mock Suggestion: Focus on clarity and conciseness in your writing."
        else:
            return f"Gemini API Error. Mock Suggestion: Strengthen the introduction to grab the reader's attention. (Error: {error_msg[:100]})"


# --- Pydantic Models ---

class TextInput(BaseModel):
    text: str
    use_ai: Optional[bool] = True
    ai_provider: Optional[Literal["openai", "gemini"]] = "openai"

class AnalysisResult(BaseModel):
    cpp_analysis: Dict[str, float]
    ai_suggestions: Optional[str] = None
    ai_provider: Optional[str] = None
    analysis_id: int

class DatabaseRow(BaseModel):
    id: int
    text: str
    cpp_result: Dict[str, Any]
    ai_suggestions: Optional[str]
    ai_provider: Optional[str]
    timestamp: str

# --- API Endpoints ---


@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI Text Analyzer</title>
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <style>
            :root {
                --primary-color: #2563eb;
                --primary-dark: #1d4ed8;
                --secondary-color: #64748b;
                --success-color: #10b981;
                --warning-color: #f59e0b;
                --error-color: #ef4444;
                --background: #f8fafc;
                --surface: #ffffff;
                --text-primary: #1e293b;
                --text-secondary: #64748b;
                --border: #e2e8f0;
                --shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
                --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
            }

            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }

            body {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: var(--background);
                color: var(--text-primary);
                line-height: 1.6;
            }

            .header {
                background: var(--surface);
                border-bottom: 1px solid var(--border);
                padding: 1rem 0;
                box-shadow: var(--shadow);
                position: sticky;
                top: 0;
                z-index: 100;
            }

            .header-content {
                max-width: 1200px;
                margin: 0 auto;
                padding: 0 1rem;
                display: flex;
                align-items: center;
                justify-content: space-between;
            }

            .logo {
                display: flex;
                align-items: center;
                gap: 0.75rem;
                font-size: 1.5rem;
                font-weight: 700;
                color: var(--primary-color);
            }

            .status-indicator {
                display: flex;
                align-items: center;
                gap: 0.5rem;
                padding: 0.5rem 1rem;
                border-radius: 0.5rem;
                background: var(--success-color);
                color: white;
                font-size: 0.875rem;
                font-weight: 500;
            }

            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 2rem 1rem;
                display: grid;
                grid-template-columns: 1fr 400px;
                gap: 2rem;
            }

            .main-panel {
                background: var(--surface);
                border-radius: 1rem;
                padding: 2rem;
                box-shadow: var(--shadow);
                border: 1px solid var(--border);
            }

            .side-panel {
                display: flex;
                flex-direction: column;
                gap: 1.5rem;
            }

            .card {
                background: var(--surface);
                border-radius: 1rem;
                padding: 1.5rem;
                box-shadow: var(--shadow);
                border: 1px solid var(--border);
            }

            .card-header {
                display: flex;
                align-items: center;
                gap: 0.75rem;
                margin-bottom: 1.5rem;
                font-size: 1.125rem;
                font-weight: 600;
                color: var(--text-primary);
            }

            .form-group {
                margin-bottom: 1.5rem;
            }

            .form-label {
                display: block;
                margin-bottom: 0.5rem;
                font-weight: 500;
                color: var(--text-primary);
            }

            .textarea {
                width: 100%;
                min-height: 200px;
                padding: 1rem;
                border: 2px solid var(--border);
                border-radius: 0.75rem;
                font-family: inherit;
                font-size: 1rem;
                resize: vertical;
                transition: border-color 0.2s, box-shadow 0.2s;
                background: var(--surface);
            }

            .textarea:focus {
                outline: none;
                border-color: var(--primary-color);
                box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
            }

            .textarea::placeholder {
                color: var(--text-secondary);
            }

            .select {
                width: 100%;
                padding: 0.75rem 1rem;
                border: 2px solid var(--border);
                border-radius: 0.5rem;
                font-family: inherit;
                font-size: 1rem;
                background: var(--surface);
                cursor: pointer;
                transition: border-color 0.2s;
            }

            .select:focus {
                outline: none;
                border-color: var(--primary-color);
            }

            .checkbox-group {
                display: flex;
                align-items: center;
                gap: 0.75rem;
                padding: 1rem;
                border: 2px solid var(--border);
                border-radius: 0.75rem;
                background: var(--surface);
                cursor: pointer;
                transition: border-color 0.2s, background-color 0.2s;
            }

            .checkbox-group:hover {
                border-color: var(--primary-color);
                background: rgba(37, 99, 235, 0.02);
            }

            .checkbox {
                width: 1.25rem;
                height: 1.25rem;
                accent-color: var(--primary-color);
            }

            .btn {
                display: inline-flex;
                align-items: center;
                justify-content: center;
                gap: 0.5rem;
                padding: 0.75rem 1.5rem;
                border: none;
                border-radius: 0.75rem;
                font-family: inherit;
                font-size: 1rem;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.2s;
                text-decoration: none;
                min-height: 44px;
            }

            .btn-primary {
                background: var(--primary-color);
                color: white;
            }

            .btn-primary:hover {
                background: var(--primary-dark);
                transform: translateY(-1px);
                box-shadow: var(--shadow-lg);
            }

            .btn-secondary {
                background: var(--surface);
                color: var(--text-primary);
                border: 2px solid var(--border);
            }

            .btn-secondary:hover {
                border-color: var(--primary-color);
                color: var(--primary-color);
            }

            .btn-group {
                display: flex;
                gap: 1rem;
                margin-top: 1.5rem;
            }

            .loading {
                opacity: 0.7;
                pointer-events: none;
            }

            .spinner {
                width: 1rem;
                height: 1rem;
                border: 2px solid transparent;
                border-top: 2px solid currentColor;
                border-radius: 50%;
                animation: spin 1s linear infinite;
            }

            @keyframes spin {
                to { transform: rotate(360deg); }
            }

            .result-card {
                background: var(--surface);
                border-radius: 1rem;
                padding: 1.5rem;
                margin-top: 1.5rem;
                box-shadow: var(--shadow);
                border: 1px solid var(--border);
                animation: slideIn 0.3s ease-out;
            }

            @keyframes slideIn {
                from {
                    opacity: 0;
                    transform: translateY(20px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }

            .result-header {
                display: flex;
                align-items: center;
                justify-content: space-between;
                margin-bottom: 1.5rem;
                padding-bottom: 1rem;
                border-bottom: 1px solid var(--border);
            }

            .result-title {
                font-size: 1.25rem;
                font-weight: 600;
                color: var(--text-primary);
            }

            .result-badge {
                padding: 0.25rem 0.75rem;
                border-radius: 9999px;
                font-size: 0.75rem;
                font-weight: 500;
                text-transform: uppercase;
                letter-spacing: 0.05em;
            }

            .badge-openai {
                background: rgba(16, 185, 129, 0.1);
                color: var(--success-color);
            }

            .badge-gemini {
                background: rgba(245, 158, 11, 0.1);
                color: var(--warning-color);
            }

            .metrics-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 1rem;
                margin-bottom: 1.5rem;
            }

            .metric-card {
                background: rgba(37, 99, 235, 0.05);
                border: 1px solid rgba(37, 99, 235, 0.1);
                border-radius: 0.75rem;
                padding: 1rem;
                text-align: center;
            }

            .metric-value {
                font-size: 1.5rem;
                font-weight: 700;
                color: var(--primary-color);
                margin-bottom: 0.25rem;
            }

            .metric-label {
                font-size: 0.875rem;
                color: var(--text-secondary);
                text-transform: uppercase;
                letter-spacing: 0.05em;
            }

            .suggestions {
                background: rgba(16, 185, 129, 0.05);
                border: 1px solid rgba(16, 185, 129, 0.1);
                border-radius: 0.75rem;
                padding: 1.5rem;
            }

            .suggestions-header {
                display: flex;
                align-items: center;
                gap: 0.5rem;
                margin-bottom: 1rem;
                font-weight: 600;
                color: var(--success-color);
            }

            .error-card {
                background: rgba(239, 68, 68, 0.05);
                border: 1px solid rgba(239, 68, 68, 0.2);
                border-radius: 0.75rem;
                padding: 1.5rem;
                color: var(--error-color);
            }

            .database-item {
                background: var(--surface);
                border: 1px solid var(--border);
                border-radius: 0.75rem;
                padding: 1.5rem;
                margin-bottom: 1rem;
                transition: box-shadow 0.2s;
            }

            .database-item:hover {
                box-shadow: var(--shadow-lg);
            }

            .database-header {
                display: flex;
                align-items: center;
                justify-content: between;
                margin-bottom: 1rem;
                gap: 1rem;
            }

            .database-id {
                font-weight: 600;
                color: var(--primary-color);
            }

            .database-timestamp {
                font-size: 0.875rem;
                color: var(--text-secondary);
                margin-left: auto;
            }

            .database-text {
                margin-bottom: 1rem;
                padding: 1rem;
                background: rgba(100, 116, 139, 0.05);
                border-radius: 0.5rem;
                font-style: italic;
            }

            @media (max-width: 768px) {
                .container {
                    grid-template-columns: 1fr;
                    padding: 1rem;
                    gap: 1rem;
                }

                .header-content {
                    padding: 0 1rem;
                }

                .btn-group {
                    flex-direction: column;
                }

                .metrics-grid {
                    grid-template-columns: repeat(2, 1fr);
                }
            }
        </style>
    </head>
    <body>
        <header class="header">
            <div class="header-content">
                <div class="logo">
                    <i class="fas fa-brain"></i>
                    AI Text Analyzer
                </div>
                <div class="status-indicator" id="statusIndicator">
                    <i class="fas fa-circle"></i>
                    Ready
                </div>
            </div>
        </header>

        <div class="container">
            <main class="main-panel">
                <div class="form-group">
                    <label class="form-label" for="textInput">
                        <i class="fas fa-edit"></i>
                        Enter your text for analysis
                    </label>
                    <textarea
                        id="textInput"
                        class="textarea"
                        placeholder="Type or paste your text here for comprehensive analysis using C++ processing and AI-powered suggestions..."
                        rows="8"
                    ></textarea>
                    <div style="font-size: 0.875rem; color: var(--text-secondary); margin-top: 0.5rem;">
                        <span id="charCount">0</span> characters, <span id="wordCount">0</span> words
                    </div>
                </div>

                <div class="btn-group">
                    <button class="btn btn-primary" onclick="analyzeText()" id="analyzeBtn">
                        <i class="fas fa-search"></i>
                        Analyze Text
                    </button>
                    <button class="btn btn-secondary" onclick="clearText()">
                        <i class="fas fa-trash"></i>
                        Clear
                    </button>
                </div>

                <div id="results"></div>
            </main>

            <aside class="side-panel">
                <div class="card">
                    <div class="card-header">
                        <i class="fas fa-cog"></i>
                        AI Configuration
                    </div>

                    <div class="form-group">
                        <label class="checkbox-group" for="useAI">
                            <input type="checkbox" id="useAI" class="checkbox" checked>
                            <div>
                                <div style="font-weight: 500;">Enable AI Enhancement</div>
                                <div style="font-size: 0.875rem; color: var(--text-secondary);">
                                    Get AI-powered writing suggestions
                                </div>
                            </div>
                        </label>
                    </div>

                    <div class="form-group">
                        <label class="form-label" for="aiProvider">
                            <i class="fas fa-robot"></i>
                            AI Provider
                        </label>
                        <select id="aiProvider" class="select">
                            <option value="openai">OpenAI (GPT-3.5)</option>
                            <option value="gemini">Google Gemini Pro</option>
                        </select>
                    </div>

                    <div class="form-group">
                        <button class="btn btn-secondary" onclick="testAIConnection()" style="width: 100%;">
                            <i class="fas fa-plug"></i>
                            Test AI Connection
                        </button>
                    </div>
                </div>

                <div class="card">
                    <div class="card-header">
                        <i class="fas fa-database"></i>
                        Analysis History
                    </div>

                    <div class="form-group">
                        <button class="btn btn-secondary" onclick="viewDatabase()" style="width: 100%;">
                            <i class="fas fa-history"></i>
                            View Recent Analyses
                        </button>
                    </div>

                    <div class="form-group">
                        <button class="btn btn-secondary" onclick="exportData()" style="width: 100%;">
                            <i class="fas fa-download"></i>
                            Export Data
                        </button>
                    </div>
                </div>

                <div class="card">
                    <div class="card-header">
                        <i class="fas fa-info-circle"></i>
                        Quick Stats
                    </div>
                    <div id="quickStats">
                        <div style="text-align: center; color: var(--text-secondary); padding: 2rem;">
                            <i class="fas fa-chart-line" style="font-size: 2rem; margin-bottom: 1rem; opacity: 0.5;"></i>
                            <div>Analyze text to see statistics</div>
                        </div>
                    </div>
                </div>
            </aside>
        </div>

        <script>
            // Global state
            let isAnalyzing = false;
            let analysisHistory = [];

            // Utility function to format timestamps
            function formatTimestamp(timestamp) {
                if (!timestamp) return 'Unknown';

                try {
                    let date;

                    if (typeof timestamp === 'string') {
                        // Handle SQLite timestamp format: "YYYY-MM-DD HH:MM:SS"
                        if (timestamp.includes(' ') && !timestamp.includes('T')) {
                            // Convert to ISO format for reliable parsing
                            const [datePart, timePart] = timestamp.split(' ');
                            timestamp = `${datePart}T${timePart}`;
                        }
                        date = new Date(timestamp);
                    } else {
                        date = new Date(timestamp);
                    }

                    // Check if date is valid
                    if (isNaN(date.getTime())) {
                        return timestamp; // Return original if parsing fails
                    }

                    // Format as local date and time
                    return date.toLocaleString();
                } catch (error) {
                    console.warn('Error formatting timestamp:', timestamp, error);
                    return timestamp || 'Unknown';
                }
            }

            // Initialize the application
            document.addEventListener('DOMContentLoaded', function() {
                updateCharCount();
                loadQuickStats();

                // Add event listeners
                document.getElementById('textInput').addEventListener('input', updateCharCount);
                document.getElementById('useAI').addEventListener('change', updateAIStatus);
                document.getElementById('aiProvider').addEventListener('change', updateAIStatus);

                // Keyboard shortcuts
                document.addEventListener('keydown', function(e) {
                    if (e.ctrlKey && e.key === 'Enter') {
                        analyzeText();
                    }
                    if (e.ctrlKey && e.key === 'k') {
                        e.preventDefault();
                        document.getElementById('textInput').focus();
                    }
                });
            });

            // Update character and word count
            function updateCharCount() {
                const text = document.getElementById('textInput').value;
                const charCount = text.length;
                const wordCount = text.trim() ? text.trim().split(/\s+/).length : 0;

                document.getElementById('charCount').textContent = charCount.toLocaleString();
                document.getElementById('wordCount').textContent = wordCount.toLocaleString();
            }

            // Update AI status indicator
            function updateAIStatus() {
                const useAI = document.getElementById('useAI').checked;
                const provider = document.getElementById('aiProvider').value;
                const statusIndicator = document.getElementById('statusIndicator');

                if (useAI) {
                    statusIndicator.innerHTML = `
                        <i class="fas fa-circle"></i>
                        AI Ready (${provider.toUpperCase()})
                    `;
                    statusIndicator.className = 'status-indicator';
                    statusIndicator.style.background = 'var(--success-color)';
                } else {
                    statusIndicator.innerHTML = `
                        <i class="fas fa-circle"></i>
                        C++ Only
                    `;
                    statusIndicator.style.background = 'var(--secondary-color)';
                }
            }

            // Clear text input
            function clearText() {
                document.getElementById('textInput').value = '';
                document.getElementById('results').innerHTML = '';
                updateCharCount();
            }

            // Set loading state
            function setLoadingState(loading) {
                isAnalyzing = loading;
                const analyzeBtn = document.getElementById('analyzeBtn');
                const statusIndicator = document.getElementById('statusIndicator');

                if (loading) {
                    analyzeBtn.innerHTML = '<div class="spinner"></div> Analyzing...';
                    analyzeBtn.classList.add('loading');
                    statusIndicator.innerHTML = '<div class="spinner"></div> Processing...';
                    statusIndicator.style.background = 'var(--warning-color)';
                } else {
                    analyzeBtn.innerHTML = '<i class="fas fa-search"></i> Analyze Text';
                    analyzeBtn.classList.remove('loading');
                    updateAIStatus();
                }
            }

            // Main analysis function
            async function analyzeText() {
                const text = document.getElementById('textInput').value.trim();
                const useAI = document.getElementById('useAI').checked;
                const aiProvider = document.getElementById('aiProvider').value;

                if (!text) {
                    showNotification('Please enter some text to analyze', 'warning');
                    return;
                }

                if (isAnalyzing) {
                    return;
                }

                setLoadingState(true);

                try {
                    const response = await fetch('/analyze', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({
                            text: text,
                            use_ai: useAI,
                            ai_provider: aiProvider
                        })
                    });

                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                    }

                    const result = await response.json();
                    displayResults(result);
                    updateQuickStats(result);
                    showNotification('Analysis completed successfully!', 'success');

                } catch (error) {
                    console.error('Analysis error:', error);
                    showError(error.message);
                    showNotification('Analysis failed. Please try again.', 'error');
                } finally {
                    setLoadingState(false);
                }
            }

            // Display analysis results
            function displayResults(result) {
                const resultsDiv = document.getElementById('results');
                const aiProviderBadge = result.ai_provider ?
                    `<span class="result-badge badge-${result.ai_provider}">${result.ai_provider.toUpperCase()}</span>` :
                    '<span class="result-badge" style="background: var(--secondary-color); color: white;">C++ ONLY</span>';

                resultsDiv.innerHTML = `
                    <div class="result-card">
                        <div class="result-header">
                            <h3 class="result-title">Analysis Results</h3>
                            <div style="display: flex; align-items: center; gap: 1rem;">
                                ${aiProviderBadge}
                                <span style="font-size: 0.875rem; color: var(--text-secondary);">
                                    ID: ${result.analysis_id}
                                </span>
                            </div>
                        </div>

                        <div class="metrics-grid">
                            <div class="metric-card">
                                <div class="metric-value">${result.cpp_analysis.word_count || 0}</div>
                                <div class="metric-label">Words</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-value">${result.cpp_analysis.sentence_count || 0}</div>
                                <div class="metric-label">Sentences</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-value">${(result.cpp_analysis.readability_score || 0).toFixed(2)}</div>
                                <div class="metric-label">Readability</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-value">${(result.cpp_analysis.sentiment_score || 0).toFixed(2)}</div>
                                <div class="metric-label">Sentiment</div>
                            </div>
                        </div>

                        ${result.ai_suggestions ? `
                            <div class="suggestions">
                                <div class="suggestions-header">
                                    <i class="fas fa-lightbulb"></i>
                                    AI Suggestions (${result.ai_provider.toUpperCase()})
                                </div>
                                <div style="white-space: pre-wrap; line-height: 1.6;">${result.ai_suggestions}</div>
                            </div>
                        ` : `
                            <div style="text-align: center; padding: 2rem; color: var(--text-secondary);">
                                <i class="fas fa-info-circle" style="font-size: 2rem; margin-bottom: 1rem; opacity: 0.5;"></i>
                                <div>AI enhancement was not used for this analysis</div>
                            </div>
                        `}

                        <div style="margin-top: 1.5rem; padding-top: 1.5rem; border-top: 1px solid var(--border); display: flex; gap: 1rem;">
                            <button class="btn btn-secondary" onclick="copyResults(${result.analysis_id})">
                                <i class="fas fa-copy"></i>
                                Copy Results
                            </button>
                            <button class="btn btn-secondary" onclick="shareResults(${result.analysis_id})">
                                <i class="fas fa-share"></i>
                                Share
                            </button>
                        </div>
                    </div>
                `;

                // Scroll to results
                resultsDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }

            // Show error message
            function showError(message) {
                const resultsDiv = document.getElementById('results');
                resultsDiv.innerHTML = `
                    <div class="error-card">
                        <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1rem;">
                            <i class="fas fa-exclamation-triangle" style="font-size: 1.25rem;"></i>
                            <h3 style="margin: 0;">Analysis Error</h3>
                        </div>
                        <p style="margin: 0;">${message}</p>
                        <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(239, 68, 68, 0.2);">
                            <button class="btn btn-secondary" onclick="document.getElementById('results').innerHTML = ''">
                                <i class="fas fa-times"></i>
                                Dismiss
                            </button>
                        </div>
                    </div>
                `;
            }

            // Show notification
            function showNotification(message, type = 'info') {
                const notification = document.createElement('div');
                notification.style.cssText = `
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    padding: 1rem 1.5rem;
                    border-radius: 0.75rem;
                    color: white;
                    font-weight: 500;
                    z-index: 1000;
                    animation: slideIn 0.3s ease-out;
                    max-width: 400px;
                    box-shadow: var(--shadow-lg);
                `;

                const colors = {
                    success: 'var(--success-color)',
                    error: 'var(--error-color)',
                    warning: 'var(--warning-color)',
                    info: 'var(--primary-color)'
                };

                const icons = {
                    success: 'fas fa-check-circle',
                    error: 'fas fa-exclamation-circle',
                    warning: 'fas fa-exclamation-triangle',
                    info: 'fas fa-info-circle'
                };

                notification.style.background = colors[type] || colors.info;
                notification.innerHTML = `
                    <div style="display: flex; align-items: center; gap: 0.75rem;">
                        <i class="${icons[type] || icons.info}"></i>
                        <span>${message}</span>
                    </div>
                `;

                document.body.appendChild(notification);

                setTimeout(() => {
                    notification.style.animation = 'slideOut 0.3s ease-in forwards';
                    setTimeout(() => notification.remove(), 300);
                }, 3000);
            }

            // Update quick stats in sidebar
            function updateQuickStats(result) {
                const quickStats = document.getElementById('quickStats');
                quickStats.innerHTML = `
                    <div class="metrics-grid" style="grid-template-columns: 1fr 1fr;">
                        <div style="text-align: center;">
                            <div style="font-size: 1.25rem; font-weight: 600; color: var(--primary-color);">
                                ${result.cpp_analysis.word_count || 0}
                            </div>
                            <div style="font-size: 0.75rem; color: var(--text-secondary);">WORDS</div>
                        </div>
                        <div style="text-align: center;">
                            <div style="font-size: 1.25rem; font-weight: 600; color: var(--primary-color);">
                                ${result.cpp_analysis.sentence_count || 0}
                            </div>
                            <div style="font-size: 0.75rem; color: var(--text-secondary);">SENTENCES</div>
                        </div>
                        <div style="text-align: center;">
                            <div style="font-size: 1.25rem; font-weight: 600; color: var(--success-color);">
                                ${(result.cpp_analysis.readability_score || 0).toFixed(1)}
                            </div>
                            <div style="font-size: 0.75rem; color: var(--text-secondary);">READABILITY</div>
                        </div>
                        <div style="text-align: center;">
                            <div style="font-size: 1.25rem; font-weight: 600; color: var(--warning-color);">
                                ${(result.cpp_analysis.sentiment_score || 0).toFixed(1)}
                            </div>
                            <div style="font-size: 0.75rem; color: var(--text-secondary);">SENTIMENT</div>
                        </div>
                    </div>
                `;
            }

            // Load initial quick stats
            function loadQuickStats() {
                // This could be enhanced to show aggregate stats from database
                const quickStats = document.getElementById('quickStats');
                quickStats.innerHTML = `
                    <div style="text-align: center; color: var(--text-secondary); padding: 2rem;">
                        <i class="fas fa-chart-line" style="font-size: 2rem; margin-bottom: 1rem; opacity: 0.5;"></i>
                        <div>Analyze text to see statistics</div>
                    </div>
                `;
            }

            // Test AI connection
            async function testAIConnection() {
                const provider = document.getElementById('aiProvider').value;
                const button = event.target;
                const originalContent = button.innerHTML;

                button.innerHTML = '<div class="spinner"></div> Testing...';
                button.disabled = true;

                try {
                    const response = await fetch('/test-ai', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({
                            ai_provider: provider,
                            test_text: "This is a test message."
                        })
                    });

                    const result = await response.json();

                    if (response.ok) {
                        showNotification(`${provider.toUpperCase()} connection successful!`, 'success');
                    } else {
                        showNotification(`${provider.toUpperCase()} connection failed: ${result.detail}`, 'error');
                    }
                } catch (error) {
                    showNotification(`Connection test failed: ${error.message}`, 'error');
                } finally {
                    button.innerHTML = originalContent;
                    button.disabled = false;
                }
            }

            // View database contents
            async function viewDatabase() {
                try {
                    const response = await fetch('/database');

                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                    }

                    const data = await response.json();
                    console.log('Database response:', data);

                    const resultsDiv = document.getElementById('results');

                    if (!Array.isArray(data)) {
                        console.error('Expected array but got:', typeof data, data);
                        showError('Failed to load database: Invalid response format from server.');
                        return;
                    }

                    if (data.length === 0) {
                        resultsDiv.innerHTML = `
                            <div class="result-card">
                                <div style="text-align: center; padding: 3rem; color: var(--text-secondary);">
                                    <i class="fas fa-database" style="font-size: 3rem; margin-bottom: 1rem; opacity: 0.5;"></i>
                                    <h3 style="margin-bottom: 0.5rem;">No analyses found</h3>
                                    <p>Start by analyzing some text to build your history.</p>
                                </div>
                            </div>
                        `;
                        return;
                    }

                    let html = `
                        <div class="result-card">
                            <div class="result-header">
                                <h3 class="result-title">Analysis History</h3>
                                <span style="font-size: 0.875rem; color: var(--text-secondary);">
                                    ${data.length} recent analyses
                                </span>
                            </div>
                    `;

                    data.forEach(item => {
                        // Extract data from the structured object format
                        const id = item.id || 'Unknown';
                        const text = item.text || '';
                        const cppResult = item.cpp_result || {};
                        const aiSuggestions = item.ai_suggestions;
                        const aiProvider = item.ai_provider;
                        const timestamp = item.timestamp;

                        const providerBadge = aiProvider ?
                            `<span class="result-badge badge-${aiProvider}">${aiProvider.toUpperCase()}</span>` :
                            '<span class="result-badge" style="background: var(--secondary-color); color: white;">C++ ONLY</span>';

                        // Display metrics from cpp_result
                        const metrics = typeof cppResult === 'object' ? cppResult : {};
                        const metricsDisplay = `
                            <div style="font-size: 0.75rem; color: var(--text-secondary); margin-top: 0.5rem;">
                                Words: ${metrics.word_count || 0} |
                                Sentences: ${metrics.sentence_count || 0} |
                                Readability: ${(metrics.readability_score || 0).toFixed(2)} |
                                Sentiment: ${(metrics.sentiment_score || 0).toFixed(2)}
                            </div>
                        `;

                        html += `
                            <div class="database-item">
                                <div class="database-header">
                                    <span class="database-id">Analysis #${id}</span>
                                    ${providerBadge}
                                    <span class="database-timestamp">${formatTimestamp(timestamp)}</span>
                                </div>
                                <div class="database-text">"${text.substring(0, 150)}${text.length > 150 ? '...' : ''}"</div>
                                ${metricsDisplay}
                                ${aiSuggestions ? `
                                    <div style="font-size: 0.875rem; color: var(--text-secondary); margin-top: 0.5rem;">
                                        <strong>AI Suggestions:</strong> ${aiSuggestions.substring(0, 100)}${aiSuggestions.length > 100 ? '...' : ''}
                                    </div>
                                ` : ''}
                                <div style="margin-top: 1rem; display: flex; gap: 0.5rem;">
                                    <button class="btn btn-secondary" onclick="loadAnalysis(${id})" style="font-size: 0.875rem; padding: 0.5rem 1rem;">
                                        <i class="fas fa-eye"></i>
                                        View Full
                                    </button>
                                    <button class="btn btn-secondary" onclick="copyAnalysis(${id})" style="font-size: 0.875rem; padding: 0.5rem 1rem;">
                                        <i class="fas fa-copy"></i>
                                        Copy
                                    </button>
                                </div>
                            </div>
                        `;
                    });

                    html += '</div>';
                    resultsDiv.innerHTML = html;
                    resultsDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });

                } catch (error) {
                    console.error('Database loading error:', error);
                    showError(`Failed to load database: ${error.message}`);
                    showNotification('Failed to load analysis history', 'error');
                }
            }

            // Copy results to clipboard
            async function copyResults(analysisId) {
                try {
                    const resultCard = document.querySelector('.result-card');
                    const text = resultCard.textContent;
                    await navigator.clipboard.writeText(text);
                    showNotification('Results copied to clipboard!', 'success');
                } catch (error) {
                    showNotification('Failed to copy results', 'error');
                }
            }

            // Share results
            function shareResults(analysisId) {
                if (navigator.share) {
                    navigator.share({
                        title: 'AI Text Analysis Results',
                        text: `Check out my text analysis results from AI Text Analyzer (Analysis #${analysisId})`,
                        url: window.location.href
                    });
                } else {
                    // Fallback: copy URL to clipboard
                    navigator.clipboard.writeText(window.location.href);
                    showNotification('URL copied to clipboard!', 'success');
                }
            }

            // Copy analysis from database
            async function copyAnalysis(analysisId) {
                try {
                    const response = await fetch(`/analysis/${analysisId}`);
                    const data = await response.json();
                    await navigator.clipboard.writeText(JSON.stringify(data, null, 2));
                    showNotification('Analysis data copied to clipboard!', 'success');
                } catch (error) {
                    showNotification('Failed to copy analysis', 'error');
                }
            }

            // Load specific analysis
            async function loadAnalysis(analysisId) {
                try {
                    const response = await fetch(`/analysis/${analysisId}`);
                    const data = await response.json();

                    // Populate the text input
                    document.getElementById('textInput').value = data.text;
                    updateCharCount();

                    // Display the results
                    displayResults({
                        analysis_id: data.id,
                        cpp_analysis: JSON.parse(data.cpp_result),
                        ai_suggestions: data.ai_suggestions,
                        ai_provider: data.ai_provider
                    });

                    showNotification('Analysis loaded successfully!', 'success');
                } catch (error) {
                    showNotification('Failed to load analysis', 'error');
                }
            }

            // Export data
            async function exportData() {
                try {
                    const response = await fetch('/database');
                    const data = await response.json();

                    const exportData = {
                        exported_at: new Date().toISOString(),
                        total_analyses: data.length,
                        analyses: data.map(item => ({
                            id: item.id,
                            text: item.text,
                            cpp_result: item.cpp_result, // Already parsed as object
                            ai_suggestions: item.ai_suggestions,
                            ai_provider: item.ai_provider,
                            timestamp: item.timestamp
                        }))
                    };

                    const blob = new Blob([JSON.stringify(exportData, null, 2)], {
                        type: 'application/json'
                    });

                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `ai-text-analyzer-export-${new Date().toISOString().split('T')[0]}.json`;
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                    URL.revokeObjectURL(url);

                    showNotification('Data exported successfully!', 'success');
                } catch (error) {
                    showNotification('Failed to export data', 'error');
                }
            }

            // Add CSS animations
            const style = document.createElement('style');
            style.textContent = `
                @keyframes slideOut {
                    to {
                        opacity: 0;
                        transform: translateX(100%);
                    }
                }

                .fade-in {
                    animation: fadeIn 0.5s ease-out;
                }

                @keyframes fadeIn {
                    from { opacity: 0; transform: translateY(20px); }
                    to { opacity: 1; transform: translateY(0); }
                }
            `;
            document.head.appendChild(style);
        </script>
    </body>
    </html>
    """

@app.post("/analyze", response_model=AnalysisResult)
async def analyze_text_endpoint(input_data: TextInput):
    try:
        # Step 1: Perform text analysis using C++ module or Python fallback
        if CPP_MODULE_AVAILABLE:
            cpp_result = text_analyzer.analyze_text(input_data.text)
        else:
            cpp_result = python_text_analysis(input_data.text)
        
        cpp_result_json = json.dumps(cpp_result)

        # Step 2: Get AI enhancement if requested
        ai_suggestions = None
        ai_provider_used = None
        if input_data.use_ai:
            ai_provider_used = input_data.ai_provider
            if ai_provider_used == "openai":
                ai_suggestions = await get_openai_suggestions(input_data.text, cpp_result)
            elif ai_provider_used == "gemini":
                ai_suggestions = await get_gemini_suggestions(input_data.text, cpp_result)
            else:
                ai_suggestions = "Unknown AI provider specified."

        # Step 3: Store the result in the database
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO analyses (text, cpp_result, ai_suggestions, ai_provider) VALUES (?, ?, ?, ?)",
            (input_data.text, cpp_result_json, ai_suggestions, ai_provider_used)
        )
        analysis_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return AnalysisResult(
            cpp_analysis=cpp_result,
            ai_suggestions=ai_suggestions,
            ai_provider=ai_provider_used,
            analysis_id=analysis_id
        )

    except Exception as e:
        print(f"Error in /analyze endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"An internal server error occurred: {str(e)}")

@app.post("/store")
async def store_analysis(input_data: TextInput):
    """(As per original prompt) Alternative endpoint for storing analysis results."""
    result = await analyze_text_endpoint(input_data)
    return {"message": f"Analysis stored with ID: {result.analysis_id}", "id": result.analysis_id}


@app.get("/database", response_model=List[DatabaseRow])
async def get_database_contents():
    """
    **REWRITTEN FOR ROBUSTNESS**
    Get recent analyses from the database, safely parsing each row.
    """
    try:
        conn = sqlite3.connect(DB_FILE)
        # This makes the connection return rows that can be accessed by column name
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM analyses ORDER BY timestamp DESC LIMIT 20")
        rows = cursor.fetchall()
        conn.close()

        results = []
        for row in rows:
            # Safely parse the cpp_result JSON for each row
            cpp_data = {}
            try:
                # The 'cpp_result' column is stored as a JSON string
                cpp_data = json.loads(row["cpp_result"])
            except (json.JSONDecodeError, TypeError):
                # If parsing fails or data is not a string, use a default error state
                cpp_data = {"error": "Failed to parse C++ result JSON."}

            results.append(
                DatabaseRow(
                    id=row["id"],
                    text=row["text"],
                    cpp_result=cpp_data,
                    ai_suggestions=row["ai_suggestions"],
                    ai_provider=row["ai_provider"],
                    timestamp=row["timestamp"]
                )
            )
        return results
    except Exception as e:
        print(f"Database error in /database: {e}")
        # Return an empty list to prevent frontend from crashing, with an error in headers
        return JSONResponse(content=[], status_code=500, headers={"X-Error": "Could not retrieve database contents."})


@app.get("/analysis/{analysis_id}")
async def get_analysis_by_id(analysis_id: int):
    """Get a specific analysis by its ID."""
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM analyses WHERE id = ?", (analysis_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        # This endpoint is primarily for programmatic access, so we can return the raw DB content
        return {
            "id": row["id"],
            "text": row["text"],
            "cpp_result": row["cpp_result"], # Return as string, as stored
            "ai_suggestions": row["ai_suggestions"],
            "ai_provider": row["ai_provider"],
            "timestamp": row["timestamp"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoints for testing and the UI - these are great additions from your original code
class TestAIRequest(BaseModel):
    ai_provider: Literal["openai", "gemini"]

@app.post("/test-ai")
async def test_ai_connection(request: TestAIRequest):
    """Test AI provider connectivity."""
    mock_cpp_result = {"word_count": 5, "sentence_count": 1}
    test_text = "This is a connection test."
    try:
        if request.ai_provider == "openai":
            suggestions = await get_openai_suggestions(test_text, mock_cpp_result)
        else: # Gemini
            suggestions = await get_gemini_suggestions(test_text, mock_cpp_result)

        if "Error." in suggestions or "not available" in suggestions:
             raise HTTPException(status_code=503, detail=suggestions)

        return {"status": "success", "message": f"{request.ai_provider.upper()} connection is working."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Connection test failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    # Make sure to run the build step first!
    if not CPP_MODULE_AVAILABLE:
        print("\n\n" + "="*50)
        print("WARNING: C++ module is not built.")
        print("Functionality will be limited to Python fallback.")
        print("To build the module, run: pip install .")
        print("="*50 + "\n\n")

    uvicorn.run(app, host="0.0.0.0", port=8000)
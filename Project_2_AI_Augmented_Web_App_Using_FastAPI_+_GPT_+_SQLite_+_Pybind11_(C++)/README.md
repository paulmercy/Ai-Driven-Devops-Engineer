# AI Text Analyzer

A FastAPI-based web application that combines C++ text analysis with AI-powered suggestions from OpenAI GPT or Google Gemini.

## Features

- **C++ Text Analysis**: Fast text processing using Pybind11
- **Multi-AI Support**: Choose between OpenAI GPT and Google Gemini
- **Custom Proxy Support**: Override OpenAI base URL for custom proxies
- **SQLite Database**: Store analysis results with AI provider tracking
- **Web Interface**: Simple HTML interface for text analysis

## New Features Added

### 1. Google Gemini Support
- Added support for Google's Gemini AI model
- Users can choose between OpenAI and Gemini in the web interface
- Fallback error handling for both providers

### 2. Custom OpenAI Proxy Support
- Override the default OpenAI base URL
- Useful for custom proxies or alternative endpoints
- Set via `OPENAI_BASE_URL` environment variable

### 3. Enhanced Database Schema
- Added `ai_provider` column to track which AI was used
- Updated web interface to display AI provider information
- Backward compatible with existing data

## Installation

### Option 1: Automatic Installation
```bash
python install_dependencies.py
```

### Option 2: Manual Installation
```bash
pip install -r requirements.txt
```

## Configuration

Update your `.env` file with the following variables:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_BASE_URL=https://your-custom-proxy.com/v1  # Optional

# Gemini Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# Application Settings
DEBUG=True
```

### Getting API Keys

#### OpenAI API Key
1. Visit [OpenAI Platform](https://platform.openai.com/)
2. Create an account or sign in
3. Go to API Keys section
4. Create a new API key

#### Gemini API Key
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Create a new API key

## Building C++ Extension

```bash
python setup.py build_ext --inplace
```

## Running the Application

```bash
python main.py
```

The application will be available at `http://localhost:8000`

## API Endpoints

### POST /analyze
Analyze text with C++ processing and optional AI enhancement.

**Request Body:**
```json
{
    "text": "Your text to analyze",
    "use_ai": true,
    "ai_provider": "openai"  // or "gemini"
}
```

**Response:**
```json
{
    "cpp_analysis": {
        "word_count": 10,
        "sentence_count": 2,
        "readability_score": 0.8,
        "sentiment_score": 0.5
    },
    "ai_suggestions": "AI-generated suggestions...",
    "ai_provider": "openai",
    "analysis_id": 1
}
```

### GET /database
Retrieve recent analysis results from the database.

## Docker Support

Build and run with Docker:

```bash
docker-compose up --build
```

## Troubleshooting

### Common Issues

1. **Import Error for google.generativeai**
   - Run: `pip install google-generativeai`

2. **C++ Module Not Found**
   - Build the extension: `python setup.py build_ext --inplace`

3. **API Key Errors**
   - Ensure your API keys are correctly set in the `.env` file
   - Check that the keys are valid and have sufficient credits

4. **Custom Proxy Issues**
   - Verify the `OPENAI_BASE_URL` format includes the full path (e.g., `/v1`)
   - Test the proxy endpoint separately

## Development

### Project Structure
```
├── main.py                 # FastAPI application
├── text_analyzer.cpp       # C++ text analysis module
├── setup.py               # Pybind11 build configuration
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables
├── install_dependencies.py # Installation script
└── README.md              # This file
```

### Adding New AI Providers

To add support for additional AI providers:

1. Add the provider to the `Literal` type in `TextInput.ai_provider`
2. Create a new helper function (e.g., `get_claude_suggestions`)
3. Add the provider case in the `analyze_text` endpoint
4. Update the frontend dropdown options

## License

This project is open source and available under the MIT License.

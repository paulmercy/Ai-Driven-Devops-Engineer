// analyzer.cpp
#include <pybind11/pybind11.h>
#include <pybind11/stl.h> // Needed for converting std::map to Python dict
#include <string>
#include <sstream>
#include <vector>
#include <set>
#include <algorithm>
#include <cctype>

namespace py = pybind11;

// A very basic text analysis function
std::map<std::string, double> analyze_text(const std::string& text) {
    if (text.empty()) {
        return {
            {"word_count", 0},
            {"sentence_count", 0},
            {"readability_score", 0},
            {"sentiment_score", 0.5}
        };
    }

    // 1. Word Count
    std::stringstream ss(text);
    std::string word;
    int word_count = 0;
    while (ss >> word) {
        word_count++;
    }

    // 2. Sentence Count (simple approach)
    int sentence_count = 0;
    for (char c : text) {
        if (c == '.' || c == '!' || c == '?') {
            sentence_count++;
        }
    }
    if (sentence_count == 0 && word_count > 0) {
        sentence_count = 1; // Assume at least one sentence if there's text
    }

    // 3. Simple Readability Score (based on average words per sentence)
    double readability_score = 0.5;
    if (sentence_count > 0) {
        double avg_words_per_sentence = static_cast<double>(word_count) / sentence_count;
        // Score is 1.0 for short sentences (<=5 words), 0.0 for long ones (>=25 words)
        readability_score = std::max(0.0, std::min(1.0, (25.0 - avg_words_per_sentence) / 20.0));
    }

    // 4. Simple Sentiment Analysis
    std::set<std::string> positive_words = {"good", "great", "excellent", "amazing", "love", "happy", "success", "beautiful", "perfect"};
    std::set<std::string> negative_words = {"bad", "terrible", "awful", "hate", "sad", "negative", "failure", "wrong", "problem"};
    
    std::string lower_text = text;
    std::transform(lower_text.begin(), lower_text.end(), lower_text.begin(), ::tolower);

    std::stringstream text_stream(lower_text);
    int positive_count = 0;
    int negative_count = 0;
    
    while(text_stream >> word) {
        // Remove punctuation from word
        word.erase(std::remove_if(word.begin(), word.end(), ispunct), word.end());
        if (positive_words.count(word)) positive_count++;
        if (negative_words.count(word)) negative_count++;
    }

    double sentiment_score = 0.5; // Neutral
    if (positive_count + negative_count > 0) {
        sentiment_score = static_cast<double>(positive_count) / (positive_count + negative_count);
    }
    
    std::map<std::string, double> result;
    result["word_count"] = word_count;
    result["sentence_count"] = sentence_count;
    result["readability_score"] = readability_score;
    result["sentiment_score"] = sentiment_score;

    return result;
}

// Pybind11 module definition
PYBIND11_MODULE(text_analyzer, m) {
    m.doc() = "A basic C++ text analyzer module for Python";
    m.def("analyze_text", &analyze_text, "Analyzes a string and returns a dictionary of metrics");
}
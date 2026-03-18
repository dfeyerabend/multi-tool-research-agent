"""
Tools for the Analysis Agent.
Every Tool has a function and a schema.
"""

import json

# === TOOL SCHEMAS ===

analysis_tools = [
    {
        "name": "text_analysis",
        "description": (
            "Analyzes a text and returns detailed statistics: "
            "word count, character count, sentence count, "
            "average word length, and the 5 most frequent words. "
            "Use this tool when the user wants to analyze, count, "
            "or statistically evaluate a text."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "The text to analyzed.",
                },
            },
            "required": ["text"],
        }
    },

    {
        "name": "sentiment_analysis",
        "description": (
            "Counts the number of words with positive and negative connotations respectively."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "The text to analyzed.",
                }
            },
            "required": ["text"],
        }
    }
]

# === TOOL EXECUTION ===
def run_text_analysis_tool(name: str, tool_input: dict) -> str:
    """
    Runs text analysis tools
    """

    if name == "text_analysis":
        import nltk
        nltk.download('stopwords', quiet=True)
        from nltk.corpus import stopwords

        german_stopwords = set(stopwords.words('german'))

        try:
            text = tool_input["text"]
            words = text.split()
            sentences = text.count('.') + text.count('!') + text.count('?') # vergessen
            symbols = len(text)
            avg_word_length = sum(len(w) for w in words) / len(words) if words else 0

            # Count most common words
            count = {}
            for word in words:
                clean = word.lower().strip('.,!?;:()[]"\'')
                if len(clean) > 2 and clean not in german_stopwords: # Exclude words with less than 2 letters AND Stop Words (e.g. "die", "ist", "und", "ein")
                    count[clean] = count.get(clean, 0) + 1
            top_5 = sorted(count.items(), key=lambda x: x[1], reverse=True)[:5]

            return json.dumps({
                "word count": len(words),
                "sentence count": sentences,
                "symbol count": symbols,
                "average word length": round(avg_word_length, 1),
                "top 5 words": [{"wort": w, "anzahl": c} for w, c in top_5],
            }, ensure_ascii=False)

        except Exception as e:
            return json.dumps({"error": f"Text analysis tool failed: {str(e)}"})

    elif name == "sentiment_analysis":
        try:
            text = tool_input["text"]
            words = text.lower().split()

            positive_words = {
                "gut", "super", "toll", "positiv", "erfolgreich", "fantastisch",
                "hervorragend", "ausgezeichnet", "vorteil", "fortschritt", "wachstum",
                "good", "great", "excellent", "positive", "success", "benefit",
                "progress", "growth", "innovative", "improvement", "advantage",
            }

            negative_words = {
                "schlecht", "negativ", "problem", "fehler", "risiko", "gefahr",
                "nachteil", "kritik", "verlust", "schwach", "mangel",
                "bad", "poor", "negative", "risk", "danger", "failure",
                "problem", "loss", "weak", "threat", "decline", "concern",
            }

            positive_found = []
            negative_found = []

            for word in words:
                clean_word = word.strip('.,!?;:()[]"\'')
                if clean_word in positive_words:
                    positive_found.append(clean_word)
                elif clean_word in negative_words:
                    negative_found.append(clean_word)

            total_sentiment_words = len(positive_found) + len(negative_found)
            if total_sentiment_words > 0:
                score = (len(positive_found) - len(negative_found)) / total_sentiment_words
            else:
                score = 0.0

            return json.dumps({
                "positive_count": len(positive_found),
                "negative_count": len(negative_found),
                "positive_words": positive_found,
                "negative_words": negative_found,
                "score": round(score, 2),  # -1.0 (very negative) to 1.0 (very positive)
            }, ensure_ascii=False)


        except Exception as e:
            return json.dumps({"error": f"Sentiment analysis tool failed: {str(e)}"})

    else:
        return json.dumps({"error": f"Unknown text analysis tool called: {name}"})



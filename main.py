from flask import Flask, request, jsonify, render_template_string
from translatepy import Translator
from translatepy.exceptions import TranslatepyException

app = Flask(__name__)
translator = Translator()

# Define supported languages
LANGUAGES = {
    "auto": "Auto-detect",
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "hi": "Hindi",
    "ta": "Tamil",
    "te": "Telugu",
    "bn": "Bengali",
    "ml": "Malayalam",
    "mr": "Marathi",
    "gu": "Gujarati",
    "kn": "Kannada",
    "pa": "Punjabi",
    "or": "Odia",
    "as": "Assamese",
    "bo": "Bhojpuri",
    "ne": "Nepali",
    "si": "Sinhala",
    "bs": "Bosnian",
}

# Filtered languages for the target dropdown (removing auto-detect)
TARGET_LANGUAGES = {k: v for k, v in LANGUAGES.items() if k != "auto"}

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ExhaTranslator</title>
    <style>
        /* Global Styles */
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background: #f3f4f6;
            color: #333;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }

        /* Main Container */
        .translator-container {
            width: 90%;
            max-width: 900px;
            background: #fff;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
        }

        /* Header Styling */
        .header {
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 30px;
            gap: 15px;
        }

        .logo {
            width: 60px;
            height: 60px;
            background: url('static/images/ExhaTranslator.png') no-repeat center center; /* Path to logo */
            background-size: contain;
        }

        .title {
            font-size: 32px;
            font-weight: bold;
            color: #007bff;
        }

        /* Translator Boxes */
        .translator-row {
            display: flex;
            justify-content: space-between;
            gap: 20px;
        }

        .translator-box {
            flex: 1;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            border: 1px solid #ddd;
            border-radius: 10px;
            padding: 20px;
            background: #f8f9fa;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }

        textarea {
            width: 100%;
            height: 200px;
            border: none;
            background: transparent;
            font-size: 18px;
            text-align: center;
            resize: none;
            outline: none;
            color: #333;
        }

        select {
            margin: 10px 0;
            padding: 10px;
            font-size: 16px;
            border: 1px solid #ddd;
            border-radius: 5px;
            width: 100%;
            text-align: center;
        }

        /* Footer */
        footer {
            text-align: center;
            font-size: 14px;
            color: #888;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="translator-container">
        <!-- Header Section -->
        <div class="header">
            <div class="logo"></div>
            <div class="title">ExhaTranslator</div>
        </div>

        <!-- Translator Section -->
        <div class="translator-row">
            <div class="translator-box">
                <select id="source-language">
                    <option value="auto">Auto-detect</option>
                    {% for code, name in languages.items() %}
                    <option value="{{ code }}">{{ name }}</option>
                    {% endfor %}
                </select>
                <textarea id="source-text" placeholder="Enter text"></textarea>
            </div>
            <div class="translator-box">
                <select id="target-language">
                    {% for code, name in target_languages.items() %}
                    <option value="{{ code }}">{{ name }}</option>
                    {% endfor %}
                </select>
                <textarea id="translated-text" placeholder="Translation" readonly></textarea>
            </div>
        </div>
    </div>
    <footer>
        Powered by TranslatePy API
    </footer>

    <script>
        const sourceText = document.getElementById('source-text');
        const sourceLanguage = document.getElementById('source-language');
        const targetLanguage = document.getElementById('target-language');
        const translatedText = document.getElementById('translated-text');

        let previousText = '';

        function translateText() {
            const text = sourceText.value.trim();
            const sourceLang = sourceLanguage.value;
            const targetLang = targetLanguage.value;

            if (!text || text === previousText) return;

            previousText = text; // Update the previous text for comparison

            fetch('/translate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    text: text,
                    source_language: sourceLang,
                    target_language: targetLang,
                }),
            })
                .then((res) => res.json())
                .then((data) => {
                    if (data.error) {
                        translatedText.value = `Error: ${data.error}`;
                    } else {
                        translatedText.value = data.translated_text || '';
                    }
                })
                .catch((err) => {
                    translatedText.value = `Error: ${err.message}`;
                    console.error(err);
                });
        }

        // Check for changes every 0.5 seconds
        setInterval(translateText, 500);
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, languages=LANGUAGES, target_languages=TARGET_LANGUAGES)

@app.route('/translate', methods=['POST'])
def translate_text():
    data = request.json
    source_text = data.get('text', '').strip()
    source_lang = data.get('source_language', 'auto')  # Default to auto-detect
    target_lang = data.get('target_language', 'en')  # Default to English

    if not source_text:
        return jsonify({'translated_text': ''})

    try:
        # Translate the text using translatepy
        if source_lang == "auto":
            translation = translator.translate(source_text, target_lang)
        else:
            translation = translator.translate(source_text, target_lang, source_lang)

        translated_text = translation.result
        return jsonify({'translated_text': translated_text})
    except TranslatepyException as e:
        return jsonify({'error': f"Translation failed: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
    

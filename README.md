# Web Scraping with LLM (OpenAI GPT-4o)

This project demonstrates how to use OpenAI's GPT-4o model to extract article information from the Hacker News website.

## How It Works

1. The application fetches the HTML content from the Hacker News website using the `requests` library
2. It uses `BeautifulSoup` to parse the HTML (but only to get the HTML as a string, not for extraction)
3. The HTML is sent to OpenAI's GPT-4o model, which extracts article information (title, author, link)
4. The extracted information is displayed in a web interface using Flask

## Setup Instructions

### 1. Create a Virtual Environment (Optional but Recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Requirements

```bash
pip install -r requirements.txt
```

### 3. Set Up OpenAI API Key

You need to get an OpenAI API key from [OpenAI Platform](https://platform.openai.com/api-keys).

Create a `.env` file in the project root directory and add your API key:

```
OPENAI_API_KEY="your-api-key-here"
```

### 4. Run the Application

```bash
python app.py
```

The application will start a web server at http://localhost:5000 where you can view the extracted article information.

## JavaScript/TypeScript Concepts

This application demonstrates several concepts that are similar to JavaScript/TypeScript patterns:

- **API Requests**: Similar to using `fetch()` in JavaScript to make HTTP requests
- **JSON Parsing**: Similar to `JSON.parse()` in JavaScript
- **HTML Parsing**: Similar to using the DOM API or libraries like Cheerio in JavaScript
- **Error Handling**: Try/catch patterns similar to JavaScript exception handling

## Notes

- The application uses OpenAI's GPT-4o model which has a high token limit, allowing it to process large HTML documents
- Setting `temperature=0` ensures more deterministic and consistent JSON output
- The `response_format={"type": "json_object"}` parameter ensures the model returns valid JSON
import requests
from bs4 import BeautifulSoup
import json
import os
from flask import Flask, render_template, jsonify
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

# Configure the OpenAI API client
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("Error: OPENAI_API_KEY not found in environment variables.")
    # You might want to exit or raise an error here depending on requirements

# Initialize the OpenAI client
client = OpenAI(api_key=api_key)

# Create a Flask application
app = Flask(__name__)

# Function to get HTML from a website and extract article information using OpenAI GPT-4o
def scrape_articles():
    # URL to scrape - using Hacker News as it's more accessible
    url = "https://news.ycombinator.com/"

    # Send HTTP request with headers to mimic a browser
    # In JavaScript, this would be similar to using the fetch API with headers option
    # Example: fetch(url, { headers: { 'User-Agent': '...' } })
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-US,en;q=0.9'
    }

    try:
        # Get the HTML content - similar to JavaScript's fetch() function
        print(f"Attempting to fetch content from {url}...")
        response = requests.get(url, headers=headers)

        # Print status code for debugging
        # In JavaScript, you would check response.status
        print(f"Response status code: {response.status_code}")

        # Check if we got a successful response
        # In JavaScript: if (!response.ok) { throw new Error(`HTTP error! Status: ${response.status}`); }
        if response.status_code != 200:
            print(f"Error: Received status code {response.status_code}")
            return [{'title': f'Error fetching content: {response.status_code}',
                     'author': 'System',
                     'link': '#'}]

        # Use BeautifulSoup to parse the HTML - similar to JavaScript's DOMParser
        # In JavaScript: const parser = new DOMParser(); const doc = parser.parseFromString(htmlString, "text/html");
        soup = BeautifulSoup(response.text, 'html.parser')
        html_content = str(soup) # Get the full HTML as a string
        print(f"Successfully fetched HTML content (length: {len(html_content)} characters)")

        # For debugging, save the HTML to a file
        # In JavaScript, you would use the FileSystem API or localStorage
        with open('hn_content.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        print("Saved HTML content to hn_content.html for inspection")

        # Using OpenAI's GPT-4o to extract information from the HTML
        try:
            print("Setting up OpenAI GPT-4o request...")
            
            # Create the system prompt for GPT-4o
            # This is like setting up instructions for the AI model
            system_prompt = """
            You are a helpful assistant that extracts structured data from HTML content.
            Extract information in JSON format exactly as specified, with no additional text or explanation.
            """
            
            # Create the user prompt with the HTML content
            user_prompt = f"""
            Extract article information from the Hacker News homepage HTML below.
            For each article, provide the following information in a JSON array:
            1. title: The title of the article
            2. author: The username of who posted it (if available, otherwise 'Unknown')
            3. link: The URL to the article (make sure it's a complete URL)
            
            Return ONLY a valid JSON array of objects with these fields, nothing else.
            
            HTML Content:
            {html_content}
            """
            
            # In JavaScript, this would be similar to creating an object with the request parameters
            # const requestData = { model: 'gpt-4o', messages: [...], temperature: 0.2 };
            print("Sending request to OpenAI GPT-4o...")
            
            # Make the API call to OpenAI
            # In JavaScript, this would be a fetch POST request to the OpenAI API
            response = client.chat.completions.create(
                model="gpt-4o",  # Using GPT-4o model
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0,  # Lower temperature for more deterministic JSON output
                response_format={"type": "json_object"}  # Request JSON response
            )
            
            print("Received response from OpenAI GPT-4o")
            
            # Get the response content
            # In JavaScript: const responseContent = response.json().choices[0].message.content;
            response_text = response.choices[0].message.content
            print(f"Response text length: {len(response_text)}")
            
            # Parse the JSON response
            # In JavaScript: const articles = JSON.parse(responseContent);
            try:
                # Parse the JSON
                parsed_data = json.loads(response_text)
                
                # Extract the articles array from the response
                # The response might be wrapped in an object with an 'articles' key
                if isinstance(parsed_data, dict) and 'articles' in parsed_data:
                    articles = parsed_data['articles']
                elif isinstance(parsed_data, list):
                    articles = parsed_data
                else:
                    # If it's neither a list nor an object with 'articles' key
                    print("Error: Unexpected response format")
                    raise ValueError("Unexpected response format")
                
                print(f"Successfully parsed JSON. Extracted {len(articles)} articles.")
                
                # Basic validation: Check if it's a list
                # In JavaScript: if (!Array.isArray(articles)) { throw new Error("Parsed JSON is not an array"); }
                if not isinstance(articles, list):
                    print("Error: Parsed JSON is not a list.")
                    raise ValueError("Parsed JSON is not a list.")
                
                # Deeper validation (check for keys like 'title', 'author', 'link')
                # In JavaScript: articles.forEach(item => { if (!item.title || !item.author || !item.link) {...} });
                for item in articles:
                    if not all(k in item for k in ('title', 'author', 'link')):
                        print(f"Warning: Article missing expected keys: {item}")
                
                return articles
                
            except json.JSONDecodeError as e:
                # In JavaScript: try { JSON.parse(text) } catch(e) { console.error("JSON parse error", e); }
                print(f"Error decoding JSON response: {e}")
                print(f"Raw response causing error:\n---\n{response_text[:500]}\n---")
                return [{'title': 'Error: Could not parse AI response', 'author': 'System', 'link': '#'}]
            except ValueError as e:
                print(f"Validation Error: {e}")
                return [{'title': f'Error: {e}', 'author': 'System', 'link': '#'}]
                
        except Exception as e:
            # In JavaScript: try {...} catch(e) { console.error("API error", e); }
            print(f"Error calling OpenAI API: {e}")
            import traceback
            print(f"Detailed error: {traceback.format_exc()}")
            return [{'title': f'Error calling OpenAI API: {str(e)}', 'author': 'System', 'link': '#'}]

    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
        return [{'title': f'Error fetching URL: {e}', 'author': 'System', 'link': '#'}]
    except Exception as e:
        print(f"Unexpected error in scrape_articles: {e}")
        import traceback
        print(f"Detailed error: {traceback.format_exc()}")
        return [{'title': f'Unexpected Error: {str(e)}', 'author': 'System', 'link': '#'}]

# Create a template directory and an HTML template file
@app.route('/')
def index():
    # Get articles from the website
    articles = scrape_articles()
    
    # Render the template with the articles
    return render_template('index.html', articles=articles)

# API endpoint to get articles as JSON
@app.route('/api/articles')
def get_articles():
    articles = scrape_articles()
    return jsonify(articles)

# Run the application
if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    import os
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    # Create a basic HTML template file
    with open('templates/index.html', 'w') as f:
        f.write('''
<!DOCTYPE html>
<html>
<head>
    <title>Hacker News Article Scraper</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        h1 {
            color: #333;
            border-bottom: 1px solid #ddd;
            padding-bottom: 10px;
        }
        .article {
            margin-bottom: 20px;
            padding: 15px;
            border: 1px solid #ddd;
            border-radius: 5px;
        }
        .article h2 {
            margin-top: 0;
        }
        .article p {
            margin: 5px 0;
        }
        .article a {
            color: #0066cc;
            text-decoration: none;
        }
        .article a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <h1>Hacker News Articles</h1>
    
    {% if articles %}
        {% for article in articles %}
            <div class="article">
                <h2>{{ article.title }}</h2>
                <p><strong>Author:</strong> {{ article.author }}</p>
                <p><a href="{{ article.link }}" target="_blank">Read Article</a></p>
            </div>
        {% endfor %}
    {% else %}
        <p>No articles found.</p>
    {% endif %}
</body>
</html>
''')
    
    # Run the Flask app
    app.run(debug=True, port=5000)

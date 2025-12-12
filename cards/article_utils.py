import os
import requests
from anthropic import Anthropic

class ArticleSummarizer:
    def __init__(self):
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        if api_key:
            self.client = Anthropic(api_key=api_key)
        else:
            self.client = None
    
    def summarize_article(self, url):
        if not self.client:
            return None
        
        try:
            response = requests.get(url, timeout=10, headers={'User-Agent': 'Debrief/1.0'})
            response.raise_for_status()
            
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            for script in soup(["script", "style"]):
                script.decompose()
            
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            text = text[:8000]
            
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=500,
                messages=[{
                    "role": "user",
                    "content": f"Summarize this article in 2-3 paragraphs, focusing on key points:\n\n{text}"
                }]
            )
            
            return message.content[0].text
            
        except Exception as e:
            print(f"Summarization error: {e}")
            return None

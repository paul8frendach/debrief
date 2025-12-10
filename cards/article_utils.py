"""Article extraction and summarization utilities"""
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse


def is_valid_url(url):
    """Check if URL is valid"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False


def fetch_article_text(url):
    """Fetch article text from URL"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # Try to find main content
        article = soup.find('article')
        if not article:
            article = soup.find('main')
        if not article:
            article = soup.find('div', class_=re.compile('content|article|post'))
        if not article:
            article = soup.body
        
        if article:
            # Get text from paragraphs
            paragraphs = article.find_all('p')
            text = ' '.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
            return text
        
        return None
    except Exception as e:
        print(f"Error fetching article: {e}")
        return None


def summarize_article(text, max_sentences=5):
    """Create a simple extractive summary"""
    if not text:
        return None
    
    # Clean up text
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Split into sentences
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
    
    if len(sentences) <= max_sentences:
        return '. '.join(sentences) + '.'
    
    # Simple scoring: prefer sentences with common keywords
    scored_sentences = []
    words = text.lower().split()
    word_freq = {}
    for word in words:
        if len(word) > 3:
            word_freq[word] = word_freq.get(word, 0) + 1
    
    for sentence in sentences:
        score = sum(word_freq.get(word.lower(), 0) for word in sentence.split() if len(word) > 3)
        scored_sentences.append((score, sentence))
    
    # Get top sentences
    scored_sentences.sort(reverse=True)
    top_sentences = [s[1] for s in scored_sentences[:max_sentences]]
    
    # Return in original order
    result_sentences = []
    for sentence in sentences:
        if sentence in top_sentences:
            result_sentences.append(sentence)
        if len(result_sentences) == max_sentences:
            break
    
    summary = '. '.join(result_sentences)
    if not summary.endswith('.'):
        summary += '.'
    
    return summary

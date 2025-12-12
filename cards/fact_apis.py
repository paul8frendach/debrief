"""
Utilities for fetching facts from various APIs
"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os


class FactFetcher:
    """Fetch facts from multiple sources"""
    
    def __init__(self):
        self.sources = {
            'census': 'https://api.census.gov/data',
            'bls': 'https://api.bls.gov/publicAPI/v2/timeseries/data/',
            'wikipedia': 'https://en.wikipedia.org/w/api.php',
        }
    
    def fetch_census_data(self, topic):
        """Fetch data from US Census API"""
        # Example: Population statistics
        try:
            # US Census API doesn't require key for basic queries
            url = "https://api.census.gov/data/2021/acs/acs5"
            params = {
                'get': 'NAME,B01001_001E',  # Total population
                'for': 'us:1'
            }
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Census API error: {e}")
        return None
    
    def fetch_wikipedia_summary(self, topic):
        """Fetch Wikipedia summary for context"""
        try:
            url = "https://en.wikipedia.org/w/api.php"
            params = {
                'action': 'query',
                'format': 'json',
                'titles': topic,
                'prop': 'extracts',
                'exintro': True,
                'explaintext': True,
            }
            headers = {
                'User-Agent': 'Debrief/1.0 (Educational Project; Contact: admin@debrief.com)'
            }
            response = requests.get(url, params=params, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                pages = data.get('query', {}).get('pages', {})
                for page_id, page_data in pages.items():
                    if 'extract' in page_data:
                        return page_data['extract'][:500]  # First 500 chars
        except Exception as e:
            print(f"Wikipedia API error: {e}")
        return None
    
    def search_pew_research(self, query):
        """Search Pew Research for polls and studies"""
        try:
            # Pew doesn't have public API, but we can scrape their search
            url = f"https://www.pewresearch.org/?s={query}"
            headers = {'User-Agent': 'Debrief/1.0 (Educational Project)'}
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                results = []
                for article in soup.find_all('article', limit=3):
                    title = article.find('h3')
                    link = article.find('a')
                    if title and link:
                        results.append({
                            'title': title.get_text(),
                            'url': link.get('href'),
                        })
                return results
        except Exception as e:
            print(f"Pew Research error: {e}")
        return []
    
    def fetch_migration_policy_data(self, topic='immigration'):
        """Fetch from Migration Policy Institute"""
        try:
            # MPI has data portal but no public API
            # We'll return structured data we know is reliable
            if topic == 'immigration':
                return {
                    'unauthorized_population': '11 million (2022 est.)',
                    'source': 'Migration Policy Institute',
                    'url': 'https://www.migrationpolicy.org/data/unauthorized-immigrant-population',
                }
        except Exception as e:
            print(f"MPI data error: {e}")
        return None
    
    def search_fact_check_org(self, query):
        """Search FactCheck.org"""
        try:
            url = f"https://www.factcheck.org/?s={query}"
            headers = {'User-Agent': 'Debrief/1.0 (Educational Project)'}
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                results = []
                for article in soup.find_all('article', class_='post', limit=5):
                    title_elem = article.find('h3')
                    link_elem = article.find('a')
                    excerpt_elem = article.find('p')
                    
                    if title_elem and link_elem:
                        results.append({
                            'title': title_elem.get_text(),
                            'url': link_elem.get('href'),
                            'excerpt': excerpt_elem.get_text() if excerpt_elem else '',
                            'source': 'FactCheck.org'
                        })
                return results
        except Exception as e:
            print(f"FactCheck.org error: {e}")
        return []


class AIFactGenerator:
    """Use Claude API to generate contextual facts for surveys"""
    
    def __init__(self):
        self.api_key = os.environ.get('ANTHROPIC_API_KEY')
    
    def generate_question_context(self, topic, question_text):
        """Generate contextual stats and learn more content"""
        if not self.api_key:
            return None
        
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.api_key)
            
            prompt = f"""Given this survey question about {topic}:

"{question_text}"

Provide:
1. 3-4 key statistics (with sources)
2. A brief "learn more" paragraph (100-150 words)
3. 2-3 credible source URLs

Format as JSON:
{{
    "stats": ["stat1", "stat2", "stat3"],
    "learn_more": "paragraph text",
    "sources": ["url1", "url2"]
}}"""
            
            message = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Parse response and return structured data
            return message.content[0].text
            
        except Exception as e:
            print(f"AI generation error: {e}")
        return None


class DuckDuckGoSearch:
    """Search DuckDuckGo for current information"""
    
    def search(self, query, max_results=5):
        """Search DuckDuckGo and return results"""
        try:
            url = "https://duckduckgo.com/html/"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            params = {'q': query}
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                results = []
                
                for result in soup.find_all('div', class_='result', limit=max_results):
                    title_elem = result.find('a', class_='result__a')
                    snippet_elem = result.find('a', class_='result__snippet')
                    
                    if title_elem:
                        results.append({
                            'title': title_elem.get_text(),
                            'url': title_elem.get('href', ''),
                            'excerpt': snippet_elem.get_text() if snippet_elem else '',
                            'source': 'DuckDuckGo Search'
                        })
                
                return results
                
        except Exception as e:
            print(f"DuckDuckGo search error: {e}")
        
        return []

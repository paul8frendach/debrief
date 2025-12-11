"""
Ground News API integration for bias-aware news aggregation
"""
import requests
import os


class GroundNewsAPI:
    """Interface with Ground News API"""
    
    def __init__(self):
        self.api_key = os.environ.get('GROUND_NEWS_API_KEY')
        self.base_url = 'https://api.groundnews.com/api/public/v1'
    
    def search_stories(self, query, limit=10):
        """
        Search for news stories related to a query
        Returns stories with bias ratings and multiple source perspectives
        """
        if not self.api_key:
            return None
        
        try:
            url = f"{self.base_url}/search"
            headers = {
                'X-API-KEY': self.api_key,
                'Content-Type': 'application/json'
            }
            params = {
                'q': query,
                'limit': limit,
                'sort': 'relevance'
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return self.format_stories(data)
            
        except Exception as e:
            print(f"Ground News API error: {e}")
        
        return None
    
    def format_stories(self, data):
        """Format Ground News response for display"""
        stories = []
        
        for item in data.get('articles', []):
            story = {
                'title': item.get('title'),
                'excerpt': item.get('description', '')[:200],
                'url': item.get('url'),
                'source': 'Ground News',
                'date': item.get('publishedAt'),
                'bias_info': {
                    'left_sources': item.get('leftSourceCount', 0),
                    'center_sources': item.get('centerSourceCount', 0),
                    'right_sources': item.get('rightSourceCount', 0),
                },
                'perspectives': item.get('sourceCount', 0),  # Total sources covering story
            }
            stories.append(story)
        
        return stories
    
    def get_story_details(self, story_id):
        """Get detailed coverage of a specific story including all sources"""
        if not self.api_key:
            return None
        
        try:
            url = f"{self.base_url}/story/{story_id}"
            headers = {'X-API-KEY': self.api_key}
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                return response.json()
                
        except Exception as e:
            print(f"Ground News story error: {e}")
        
        return None

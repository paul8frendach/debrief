from newsapi import NewsApiClient
from django.conf import settings
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)


def get_trending_topics():
    """
    Get trending political topics from NewsAPI
    Caches results for 1 hour to avoid hitting rate limits
    """
    # Check cache first
    cached_topics = cache.get('trending_topics')
    if cached_topics:
        return cached_topics
    
    # If no API key, return mock data
    if not settings.NEWSAPI_KEY:
        return get_mock_trending_topics()
    
    try:
        newsapi = NewsApiClient(api_key=settings.NEWSAPI_KEY)
        
        # Get top headlines for US politics
        headlines = newsapi.get_top_headlines(
            country='us',
            category='politics',
            page_size=10
        )
        
        if headlines['status'] == 'ok' and headlines['articles']:
            topics = []
            seen_titles = set()
            
            for article in headlines['articles']:
                title = article.get('title', '')
                description = article.get('description', '')
                url = article.get('url', '')
                source = article.get('source', {}).get('name', 'Unknown')
                
                # Skip duplicates and articles without titles
                if not title or title in seen_titles:
                    continue
                
                seen_titles.add(title)
                
                # Extract key topic (simplified - you could use NLP here)
                topic = {
                    'title': title,
                    'description': description[:150] + '...' if description and len(description) > 150 else description,
                    'source': source,
                    'url': url,
                }
                
                topics.append(topic)
                
                if len(topics) >= 5:
                    break
            
            # Cache for 1 hour
            cache.set('trending_topics', topics, 3600)
            return topics
        
    except Exception as e:
        logger.error(f"Error fetching trending topics: {e}")
    
    # Fallback to mock data if API fails
    return get_mock_trending_topics()


def get_mock_trending_topics():
    """
    Mock trending topics for testing/fallback
    """
    return [
        {
            'title': 'Congressional Budget Debate',
            'description': 'Congress debates new budget proposals amid economic concerns and partisan divisions.',
            'source': 'Political News',
            'url': '#',
        },
        {
            'title': 'Federal Immigration Policy Update',
            'description': 'New executive orders reshape federal immigration enforcement priorities.',
            'source': 'Policy Watch',
            'url': '#',
        },
        {
            'title': 'Supreme Court Decision Expected',
            'description': 'Major ruling anticipated on constitutional rights case with nationwide implications.',
            'source': 'Legal News',
            'url': '#',
        },
        {
            'title': 'State Healthcare Reforms',
            'description': 'Multiple states propose healthcare policy changes affecting millions of residents.',
            'source': 'Health Policy',
            'url': '#',
        },
        {
            'title': 'Election Security Measures',
            'description': 'New bipartisan legislation aims to strengthen election infrastructure and security.',
            'source': 'Election News',
            'url': '#',
        },
    ]


def get_trending_keywords():
    """
    Extract keywords from trending topics for search suggestions
    """
    topics = get_trending_topics()
    keywords = []
    
    # Extract important words from titles
    for topic in topics:
        words = topic['title'].split()
        # Filter out common words
        important_words = [w for w in words if len(w) > 4 and w.lower() not in 
                          ['about', 'their', 'which', 'where', 'these', 'those']]
        keywords.extend(important_words[:2])  # Take top 2 words from each title
    
    return list(set(keywords))[:10]  # Return unique keywords

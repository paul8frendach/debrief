"""
AI-powered search query enhancement and result curation
Uses Claude to understand vague queries and suggest better searches
"""
import os
import json


class AISearchHelper:
    """Use Claude to enhance user searches"""
    
    def __init__(self):
        self.api_key = os.environ.get('ANTHROPIC_API_KEY')
    
    def enhance_query(self, user_query, topic):
        """
        Take vague user input and generate:
        1. Better search queries
        2. Suggested specific questions
        3. Key terms to look for
        """
        if not self.api_key:
            return None
        
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.api_key)
            
            prompt = f"""The user is researching {topic} and typed: "{user_query}"

This query might be vague or incomplete. Help them by:

1. Generating 3 specific, searchable queries based on what they probably want to know
2. Suggesting 2-3 key aspects of this topic they should research
3. Identifying important terms/concepts to understand

Respond in JSON format:
{{
    "search_queries": ["query1", "query2", "query3"],
    "research_suggestions": ["suggestion1", "suggestion2"],
    "key_terms": ["term1", "term2", "term3"]
}}"""
            
            message = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Parse response
            response_text = message.content[0].text
            
            # Extract JSON from response
            if '```json' in response_text:
                response_text = response_text.split('```json')[1].split('```')[0]
            elif '```' in response_text:
                response_text = response_text.split('```')[1].split('```')[0]
            
            return json.loads(response_text.strip())
            
        except Exception as e:
            print(f"AI enhancement error: {e}")
            return None
    
    def curate_results(self, query, results, topic):
        """
        Use AI to:
        1. Rank results by relevance
        2. Identify key facts
        3. Suggest which to save to notebook
        """
        if not self.api_key or not results:
            return results
        
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.api_key)
            
            # Prepare results summary
            results_summary = []
            for i, result in enumerate(results[:10]):
                results_summary.append({
                    'index': i,
                    'title': result.get('title', ''),
                    'source': result.get('source', ''),
                })
            
            prompt = f"""User is researching {topic} with query: "{query}"

Here are search results:
{json.dumps(results_summary, indent=2)}

Help the user by:
1. Ranking these by relevance (return indices in order)
2. Identifying which 2-3 are most important to save
3. Explaining WHY each recommended result is valuable

Respond in JSON:
{{
    "ranked_indices": [2, 0, 5, ...],
    "must_save": [2, 5],
    "explanations": {{
        "2": "This source provides...",
        "5": "Critical because..."
    }}
}}"""
            
            message = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=800,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = message.content[0].text
            
            # Extract JSON
            if '```json' in response_text:
                response_text = response_text.split('```json')[1].split('```')[0]
            elif '```' in response_text:
                response_text = response_text.split('```')[1].split('```')[0]
            
            curation = json.loads(response_text.strip())
            
            # Reorder results
            ranked_results = []
            for idx in curation.get('ranked_indices', []):
                if idx < len(results):
                    result = results[idx].copy()
                    result['ai_recommended'] = idx in curation.get('must_save', [])
                    result['ai_explanation'] = curation.get('explanations', {}).get(str(idx), '')
                    ranked_results.append(result)
            
            return ranked_results
            
        except Exception as e:
            print(f"AI curation error: {e}")
            return results

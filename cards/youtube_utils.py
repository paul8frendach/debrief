"""YouTube transcript extraction and summarization utilities"""
import re
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound


def extract_video_id(url):
    """Extract YouTube video ID from various URL formats"""
    patterns = [
        r'(?:youtube\.com\/watch\?v=)([a-zA-Z0-9_-]+)',
        r'(?:youtu\.be\/)([a-zA-Z0-9_-]+)',
        r'(?:youtube\.com\/embed\/)([a-zA-Z0-9_-]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def get_youtube_transcript(video_id):
    """Fetch transcript for a YouTube video"""
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        # Combine all text
        full_text = ' '.join([item['text'] for item in transcript_list])
        return full_text
    except (TranscriptsDisabled, NoTranscriptFound):
        return None
    except Exception as e:
        print(f"Error fetching transcript: {e}")
        return None


def summarize_transcript(transcript_text, max_length=500):
    """Create a simple summary of the transcript"""
    if not transcript_text:
        return None
    
    # Clean up the text
    text = transcript_text.replace('\n', ' ')
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Simple extractive summary - take first sentences up to max_length
    sentences = text.split('. ')
    summary = []
    current_length = 0
    
    for sentence in sentences:
        if current_length + len(sentence) > max_length:
            break
        summary.append(sentence)
        current_length += len(sentence)
    
    result = '. '.join(summary)
    if result and not result.endswith('.'):
        result += '...'
    
    return result if result else text[:max_length] + '...'

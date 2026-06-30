import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6")

# CORS - update with your deployed frontend URL later
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")

# RSS feeds to aggregate from. Mix of general + India-focused since the
# original idea mentioned local/area safety awareness. Add/remove freely.
RSS_FEEDS = [
    {"name": "BBC News", "url": "http://feeds.bbci.co.uk/news/rss.xml", "category": "general"},
    {"name": "Reuters World", "url": "https://www.reutersagency.com/feed/?best-topics=world&post_type=best", "category": "world"},
    {"name": "NDTV Top Stories", "url": "https://feeds.feedburner.com/ndtvnews-top-stories", "category": "india"},
    {"name": "Times of India", "url": "https://timesofindia.indiatimes.com/rssfeedstopstories.cms", "category": "india"},
    {"name": "Al Jazeera", "url": "https://www.aljazeera.com/xml/rss/all.xml", "category": "world"},
    {"name": "The Hindu", "url": "https://www.thehindu.com/news/national/feeder/default.rss", "category": "india"},
]

# How similar two headlines need to be (0-1) to be considered "the same story"
SIMILARITY_THRESHOLD = 0.35

# Cache aggregated feed for this many seconds before re-fetching
FEED_CACHE_SECONDS = 600

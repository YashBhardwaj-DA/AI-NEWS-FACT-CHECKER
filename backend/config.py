import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")

RSS_FEEDS = [
    {"name": "BBC News", "url": "http://feeds.bbci.co.uk/news/rss.xml", "category": "general"},
    {"name": "Reuters World", "url": "https://www.reutersagency.com/feed/?best-topics=world&post_type=best", "category": "world"},
    {"name": "NDTV Top Stories", "url": "https://feeds.feedburner.com/ndtvnews-top-stories", "category": "india"},
    {"name": "Times of India", "url": "https://timesofindia.indiatimes.com/rssfeedstopstories.cms", "category": "india"},
    {"name": "Al Jazeera", "url": "https://www.aljazeera.com/xml/rss/all.xml", "category": "world"},
    {"name": "The Hindu", "url": "https://www.thehindu.com/news/national/feeder/default.rss", "category": "india"},
]

SIMILARITY_THRESHOLD = 0.35
FEED_CACHE_SECONDS = 600

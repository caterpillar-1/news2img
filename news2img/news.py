import feedparser
from typing import Optional

class News:
    """Get news in RSS feed.

    Example:
        ::

            url = "https://example.com/rss.xml"
            feedreader = News(url)
            first_news = list(iter(feedreader))[0]
    """


    def __init__(self, url: str, min_len=60, max_len=1000):
        self._min_len = min_len
        self._max_len = max_len
        self.update(url)

    def __iter__(self):
        return iter(self._news.copy())

    def update(self, url: Optional[str]=None):
        if url:
            self._url = url
        self._news = [
            e for e in feedparser.parse(self._url)['entries'] 
            if self._min_len <= len(e['summary']) <= self._max_len
        ]

__all__ = [News]

"""
News fetching module for SimVestor
Handles yfinance news API calls with rate limiting
"""

import yfinance as yf
import time
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


def get_stock_news(ticker: str, limit: int = 5) -> List[Dict]:
    """Get recent news for a stock ticker"""
    try:
        # Clean and validate ticker
        ticker = ticker.strip().upper()
        
        stock = yf.Ticker(ticker)
        
        # Try to get news with error handling and rate limit retry
        max_retries = 2
        for attempt in range(max_retries):
            try:
                news = stock.news
                break  # Success, exit retry loop
            except Exception as e:
                error_msg = str(e).lower()
                if any(phrase in error_msg for phrase in ["rate limit", "too many requests", "429", "throttled"]):
                    if attempt < max_retries - 1:
                        logger.warning(f"Rate limited fetching news for {ticker}, retrying in {2 ** attempt} seconds...")
                        time.sleep(2 ** attempt)  # 1s, then 2s delay
                        continue
                logger.error(f"Error fetching news from yfinance: {str(e)}")
                return []
        
        if not news or len(news) == 0:
            logger.info(f"No news found for ticker {ticker}")
            return []
        
        # Format news data with better error handling
        formatted_news = []
        for i, article in enumerate(news[:limit]):
            try:
                formatted_article = {
                    'title': article.get('title', f'News Article {i+1}'),
                    'publisher': article.get('publisher', 'Unknown Publisher'),
                    'link': article.get('link', ''),
                    'published': article.get('providerPublishTime', 0),
                    'summary': article.get('summary', 'No summary available')[:500] + '...' if len(article.get('summary', '')) > 500 else article.get('summary', 'No summary available')
                }
                formatted_news.append(formatted_article)
            except Exception as e:
                logger.error(f"Error formatting article {i}: {str(e)}")
                continue
        
        logger.info(f"Successfully fetched {len(formatted_news)} news articles for {ticker}")
        return formatted_news
        
    except Exception as e:
        logger.error(f"Error fetching news for {ticker}: {str(e)}")
        return []

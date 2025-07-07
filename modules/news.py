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
    """Get recent news for a stock ticker with improved error handling"""
    try:
        # Clean and validate ticker
        ticker = ticker.strip().upper()
        logger.info(f"Fetching news for ticker: {ticker}")
        
        stock = yf.Ticker(ticker)
        
        # Try to get news with progressive retry strategy
        max_retries = 3
        news = None
        
        for attempt in range(max_retries):
            try:
                logger.info(f"News fetch attempt {attempt + 1} for {ticker}")
                news = stock.news
                if news and len(news) > 0:
                    logger.info(f"Successfully fetched {len(news)} news items on attempt {attempt + 1}")
                    break
                else:
                    logger.warning(f"Empty news response on attempt {attempt + 1}")
                    if attempt < max_retries - 1:
                        time.sleep(1 + attempt)  # Progressive delay
                        continue
                    
            except Exception as e:
                error_msg = str(e).lower()
                logger.error(f"Attempt {attempt + 1} failed: {str(e)}")
                
                if any(phrase in error_msg for phrase in ["rate limit", "too many requests", "429", "throttled"]):
                    if attempt < max_retries - 1:
                        delay = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                        logger.warning(f"Rate limited, retrying in {delay} seconds...")
                        time.sleep(delay)
                        continue
                elif "unauthorized" in error_msg or "forbidden" in error_msg:
                    logger.error(f"Authorization error for {ticker}: {str(e)}")
                    return []
                else:
                    logger.error(f"Unexpected error: {str(e)}")
                    if attempt < max_retries - 1:
                        time.sleep(1)
                        continue
        
        if not news or len(news) == 0:
            logger.warning(f"No news found for ticker {ticker} after {max_retries} attempts")
            return []
        
        # Format news data with better error handling
        formatted_news = []
        for i, article in enumerate(news[:limit]):
            try:
                # Validate required fields
                title = article.get('title', '').strip()
                if not title:
                    title = f'News Article {i+1}'
                
                publisher = article.get('publisher', 'Unknown Publisher').strip()
                link = article.get('link', '').strip()
                summary = article.get('summary', '').strip()
                
                # Handle summary length
                if len(summary) > 500:
                    summary = summary[:497] + '...'
                elif not summary:
                    summary = 'No summary available'
                
                # Handle publish time
                published_time = article.get('providerPublishTime', 0)
                if not isinstance(published_time, (int, float)) or published_time <= 0:
                    published_time = 0
                
                formatted_article = {
                    'title': title,
                    'publisher': publisher,
                    'link': link,
                    'published': published_time,
                    'summary': summary
                }
                formatted_news.append(formatted_article)
                
            except Exception as e:
                logger.error(f"Error formatting article {i} for {ticker}: {str(e)}")
                continue
        
        logger.info(f"Successfully formatted {len(formatted_news)} news articles for {ticker}")
        return formatted_news
        
    except Exception as e:
        logger.error(f"Critical error fetching news for {ticker}: {str(e)}")
        return []

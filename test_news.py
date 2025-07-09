#!/usr/bin/env python3
"""
Test script for news fetching functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.news import get_stock_news
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_news_fetching():
    """Test news fetching for popular tickers"""
    test_tickers = ['AAPL', 'MSFT', 'GOOGL', 'TSLA']
    
    for ticker in test_tickers:
        print(f"\n{'='*50}")
        print(f"Testing news for {ticker}")
        print('='*50)
        
        try:
            news = get_stock_news(ticker, limit=3)
            print(f"✅ Found {len(news)} articles for {ticker}")
            
            for i, article in enumerate(news):
                print(f"\n{i+1}. {article.get('title', 'No title')[:60]}...")
                print(f"   Publisher: {article.get('publisher', 'Unknown')}")
                print(f"   Published: {article.get('published', 'Unknown')}")
                summary = article.get('summary', 'No summary')
                print(f"   Summary: {summary[:100]}...")
                
        except Exception as e:
            print(f"❌ Error fetching news for {ticker}: {str(e)}")
    
    print(f"\n{'='*50}")
    print("News fetching test completed")
    print('='*50)

if __name__ == "__main__":
    test_news_fetching()

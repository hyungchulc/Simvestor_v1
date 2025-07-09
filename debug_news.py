"""
Quick news debugging script for Streamlit
"""

import streamlit as st
import yfinance as yf
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.title("News Debugging Tool")

ticker = st.text_input("Enter ticker:", value="AAPL")

if st.button("Test News Fetch"):
    try:
        st.write(f"Testing news fetch for {ticker}...")
        stock = yf.Ticker(ticker)
        news = stock.news
        
        st.write(f"Raw news data type: {type(news)}")
        st.write(f"Number of articles: {len(news) if news else 0}")
        
        if news and len(news) > 0:
            st.write("First article keys:")
            st.write(list(news[0].keys()))
            
            st.write("First article data:")
            st.json(news[0])
            
            st.write("All articles (limited view):")
            for i, article in enumerate(news[:3]):
                st.write(f"**Article {i+1}:**")
                st.write(f"- Title: {article.get('title', 'NO TITLE')}")
                st.write(f"- Publisher: {article.get('publisher', 'NO PUBLISHER')}")
                st.write(f"- Summary: {str(article.get('summary', 'NO SUMMARY'))[:100]}...")
                st.write("---")
        else:
            st.write("No news data returned")
            
    except Exception as e:
        st.error(f"Error: {str(e)}")
        logger.error(f"News fetch error: {str(e)}", exc_info=True)

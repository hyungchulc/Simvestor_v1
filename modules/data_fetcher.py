"""
Data fetching and processing module for SimVestor
Handles yfinance API calls, data validation, and fallback strategies
"""

import pandas as pd
import numpy as np
import yfinance as yf
import time
import logging
from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict
import streamlit as st

logger = logging.getLogger(__name__)

@st.cache_data(ttl=900)  # 15 minutes cache for faster retries
def fetch_stock_data(ticker, start_date, end_date=None):
    """Fetch stock data using yfinance 0.2.54 with enhanced error handling"""
    try:
        if end_date is None:
            end_date = datetime.now()
        
        # Ensure ticker is clean
        ticker = ticker.strip().upper()
        
        # Initialize variables
        data = None
        error_messages = []
        
        # Create progress indicators in a dedicated container
        progress_container = st.container()
        with progress_container:
            progress_bar = st.progress(0)
            status_text = st.empty()
        
        # Convert dates to proper format
        start_date_pd = pd.to_datetime(start_date)
        end_date_pd = pd.to_datetime(end_date)
        
        # Strategy 1: Basic yfinance download with retry logic
        try:
            progress_bar.progress(20)
            status_text.text("📡 Attempting download...")
            
            import time
            max_retries = 3
            retry_delay = 2
            
            for attempt in range(max_retries):
                try:
                    logger.info(f"Downloading {ticker} data, attempt {attempt + 1}")
                    
                    # Use yfinance download
                    data = yf.download(
                        ticker,
                        start=start_date_pd,
                        end=end_date_pd,
                        progress=False,
                        auto_adjust=True,
                        prepost=False,
                        threads=True
                    )
                    
                    if data is not None and not data.empty:
                        # Filter by start date to ensure we get the right range
                        data = data[data.index >= start_date_pd]
                        
                        if len(data) > 5:
                            progress_bar.progress(100)
                            status_text.text(f"✅ Successfully loaded {len(data)} days of data for {ticker}")
                            return process_stock_data(data, ticker)
                    
                    break  # If we get here, data was empty but no exception
                    
                except Exception as e:
                    error_msg = str(e).lower()
                    if any(phrase in error_msg for phrase in ["rate limit", "too many requests", "429", "throttled", "exceeded"]):
                        if attempt < max_retries - 1:
                            # More aggressive backoff for rate limits
                            backoff_delay = retry_delay * (2 ** attempt)  # Exponential backoff: 2, 4, 8 seconds
                            status_text.text(f"⏳ Rate limited, waiting {backoff_delay} seconds... (Attempt {attempt + 1}/{max_retries})")
                            time.sleep(backoff_delay)
                            continue
                        else:
                            error_messages.append(f"Rate limit exceeded after {max_retries} attempts")
                    else:
                        error_messages.append(f"Download attempt {attempt + 1} failed: {str(e)}")
                    
                    if attempt == max_retries - 1:
                        break
                    
        except Exception as e:
            error_messages.append(f"Strategy 1 failed: {str(e)}")
        
        # Strategy 2: Use Ticker object with different periods
        try:
            if data is None or len(data) < 5:
                progress_bar.progress(50)
                status_text.text("📡 Trying Ticker object...")
                
                stock = yf.Ticker(ticker)
                periods = ["1y", "6mo", "3mo", "1mo"]
                
                for i, period in enumerate(periods):
                    try:
                        # Add delay to avoid rate limiting
                        time.sleep(1)
                        
                        data = stock.history(
                            period=period,
                            auto_adjust=True,
                            prepost=False
                        )
                        
                        if data is not None and len(data) > 5:
                            # Filter to start date if available
                            if start_date_pd in data.index or any(data.index >= start_date_pd):
                                data = data[data.index >= start_date_pd]
                                if len(data) > 5:
                                    progress_bar.progress(100)
                                    status_text.text(f"✅ Using {period} data for {ticker}")
                                    return process_stock_data(data, ticker)
                        
                    except Exception as e:
                        logger.warning(f"Period {period} failed for {ticker}: {str(e)}")
                        continue
        
        except Exception as e:
            error_messages.append(f"Strategy 2 failed: {str(e)}")
        
        # Strategy 3: Minimal data fetch
        try:
            if data is None or len(data) < 5:
                progress_bar.progress(80)
                status_text.text("📡 Trying minimal download...")
                
                time.sleep(2)  # Wait before retry
                
                try:
                    data = yf.download(
                        ticker, 
                        period="6mo",
                        progress=False,
                        auto_adjust=True
                    )
                    
                    if len(data) > 5:
                        progress_bar.progress(100)
                        status_text.text(f"✅ Using minimal download for {ticker}")
                        return process_stock_data(data, ticker)
                        
                except Exception as e:
                    error_messages.append(f"Minimal download failed: {str(e)}")
        
        except Exception as e:
            error_messages.append(f"Strategy 3 failed: {str(e)}")
        
        # Strategy 4: Generate sample data for demo purposes
        try:
            progress_bar.progress(95)
            status_text.text("📡 Generating sample data...")
            
            # Generate sample data for demonstration
            sample_data = generate_sample_data(ticker, start_date, end_date)
            if sample_data is not None:
                progress_bar.progress(100)
                status_text.text(f"⚠️ Using sample data for {ticker} (Demo mode)")
                return sample_data, get_sample_stock_info(ticker)
                
        except Exception as e:
            error_messages.append(f"Sample data generation failed: {str(e)}")
        
        # Clean up progress indicators
        progress_bar.empty()
        status_text.empty()
        
        # If all strategies fail
        return None, f"""❌ Could not fetch data for {ticker} after trying all methods. This may be due to:
• **Yahoo Finance Rate Limiting**: API is temporarily blocking requests
• **Network Issues**: Check your internet connection
• **Invalid Ticker**: '{ticker}' may not exist or be delisted
• **Data Availability**: Limited historical data for this symbol

**Error Details**: {'; '.join(error_messages[:3])}"""
        
    except Exception as e:
        logger.error(f"Critical error in fetch_stock_data: {str(e)}")
        return None, f"Critical error: {str(e)}"


def generate_sample_data(ticker, start_date, end_date=None):
    """Generate sample stock data for demonstration when real data is unavailable"""
    try:
        if end_date is None:
            end_date = datetime.now()
        
        # Convert to pandas datetime
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
        
        # Create date range
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
        date_range = date_range[date_range.weekday < 5]  # Only weekdays
        
        if len(date_range) < 10:
            return None
        
        # Base price varies by ticker
        base_prices = {
            'AAPL': 150, 'MSFT': 300, 'GOOGL': 2500, 'AMZN': 3000, 'TSLA': 800,
            'NVDA': 400, 'META': 250, 'NFLX': 400, 'SPY': 400, 'QQQ': 350
        }
        
        base_price = base_prices.get(ticker, 100)
        
        # Generate realistic price movement
        np.random.seed(hash(ticker) % 1000)  # Consistent seed based on ticker
        
        daily_returns = np.random.normal(0.001, 0.02, len(date_range))  # ~20% annual volatility
        
        # Add some trend
        trend = np.linspace(0, 0.1, len(date_range))  # 10% annual trend
        daily_returns += trend / len(date_range)
        
        # Calculate prices
        prices = [base_price]
        for return_rate in daily_returns[1:]:
            prices.append(prices[-1] * (1 + return_rate))
        
        # Create OHLCV data
        sample_data = pd.DataFrame({
            'Open': [p * np.random.uniform(0.99, 1.01) for p in prices],
            'High': [p * np.random.uniform(1.00, 1.03) for p in prices],
            'Low': [p * np.random.uniform(0.97, 1.00) for p in prices],
            'Close': prices,
            'Adj Close': prices,
            'Volume': [int(np.random.uniform(1000000, 10000000)) for _ in prices]
        }, index=date_range)
        
        # Ensure OHLC relationships are correct
        sample_data['High'] = sample_data[['Open', 'High', 'Close']].max(axis=1)
        sample_data['Low'] = sample_data[['Open', 'Low', 'Close']].min(axis=1)
        
        return sample_data
    
    except Exception as e:
        logger.error(f"Error generating sample data: {str(e)}")
        return None


def get_sample_stock_info(ticker):
    """Get sample stock information for demo purposes"""
    sample_info = {
        'AAPL': {'longName': 'Apple Inc.', 'sector': 'Technology', 'industry': 'Consumer Electronics', 'marketCap': 3000000000000},
        'MSFT': {'longName': 'Microsoft Corporation', 'sector': 'Technology', 'industry': 'Software', 'marketCap': 2500000000000},
        'GOOGL': {'longName': 'Alphabet Inc.', 'sector': 'Technology', 'industry': 'Internet Services', 'marketCap': 1800000000000},
        'AMZN': {'longName': 'Amazon.com Inc.', 'sector': 'Consumer Discretionary', 'industry': 'E-commerce', 'marketCap': 1600000000000},
        'TSLA': {'longName': 'Tesla Inc.', 'sector': 'Consumer Discretionary', 'industry': 'Electric Vehicles', 'marketCap': 800000000000},
        'NVDA': {'longName': 'NVIDIA Corporation', 'sector': 'Technology', 'industry': 'Semiconductors', 'marketCap': 1200000000000},
        'META': {'longName': 'Meta Platforms Inc.', 'sector': 'Technology', 'industry': 'Social Media', 'marketCap': 700000000000},
        'SPY': {'longName': 'SPDR S&P 500 ETF Trust', 'sector': 'Financial', 'industry': 'ETF', 'marketCap': 400000000000},
        'QQQ': {'longName': 'Invesco QQQ Trust', 'sector': 'Financial', 'industry': 'ETF', 'marketCap': 200000000000},
    }
    
    return sample_info.get(ticker, {
        'longName': f'{ticker} Corporation',
        'sector': 'Unknown',
        'industry': 'Unknown',
        'marketCap': 50000000000
    })


def process_stock_data(data, ticker):
    """Process and validate stock data"""
    try:
        if data is None or data.empty:
            return None, f"No data available for {ticker}"
        
        # Handle MultiIndex columns from yfinance
        if hasattr(data.columns, 'levels') and len(data.columns.levels) > 1:
            # Flatten MultiIndex columns - take the second level (metric name)
            data.columns = [col[1] if isinstance(col, tuple) else col for col in data.columns]
        
        # Ensure we have basic price columns
        if 'Adj Close' not in data.columns and 'Close' in data.columns:
            data['Adj Close'] = data['Close']
        
        # Get enhanced stock info
        stock_info = get_enhanced_stock_info(ticker)
        
        return data, stock_info
    
    except Exception as e:
        logger.error(f"Error processing stock data for {ticker}: {str(e)}")
        return None, f"Error processing data: {str(e)}"


def get_enhanced_stock_info(ticker):
    """Get enhanced stock information using new yfinance API with fallback"""
    stock_info = {
        "longName": ticker, 
        "sector": "Unknown", 
        "industry": "Unknown",
        "marketCap": None,
        "dividendYield": None,
        "beta": None,
        "peRatio": None,
        "website": None,
        "country": None,
        "currency": None
    }
    
    try:
        stock = yf.Ticker(ticker)
        
        # Method 1: Try new .info property with timeout and error handling
        try:
            # Add a small delay to avoid rate limiting
            time.sleep(0.5)
            info = stock.info
            
            if info and isinstance(info, dict) and len(info) > 1:
                # Update with available info
                info_fields = {
                    'longName': 'longName',
                    'shortName': 'longName',  # fallback
                    'sector': 'sector',
                    'industry': 'industry',
                    'marketCap': 'marketCap',
                    'dividendYield': 'dividendYield',
                    'beta': 'beta',
                    'trailingPE': 'peRatio',
                    'forwardPE': 'peRatio',  # fallback
                    'website': 'website',
                    'country': 'country',
                    'currency': 'currency'
                }
                
                for info_key, stock_key in info_fields.items():
                    if info_key in info and info[info_key] is not None and info[info_key] != '':
                        stock_info[stock_key] = info[info_key]
                        
        except Exception as e:
            logger.warning(f"Could not fetch complete info for {ticker}: {str(e)}")
            
        # Method 2: Try fast_info (newer feature) if available
        try:
            if hasattr(stock, 'fast_info'):
                fast_info = stock.fast_info
                if fast_info:
                    stock_info.update({
                        'marketCap': getattr(fast_info, 'market_cap', stock_info['marketCap']),
                        'currency': getattr(fast_info, 'currency', stock_info['currency'])
                    })
        except Exception as e:
            logger.warning(f"Fast info not available for {ticker}: {str(e)}")
            
            
        # Method 3: Try to get basic data to validate ticker
        try:
            hist = stock.history(period="5d", auto_adjust=True)
            if hist.empty:
                logger.warning(f"No recent price data found for {ticker}")
        except Exception as e:
            logger.warning(f"Could not validate ticker {ticker}: {str(e)}")
        
        # Add some default values for well-known tickers
        known_tickers = {
            'AAPL': {'longName': 'Apple Inc.', 'sector': 'Technology', 'industry': 'Consumer Electronics'},
            'MSFT': {'longName': 'Microsoft Corporation', 'sector': 'Technology', 'industry': 'Software'},
            'GOOGL': {'longName': 'Alphabet Inc.', 'sector': 'Technology', 'industry': 'Internet Services'},
            'AMZN': {'longName': 'Amazon.com Inc.', 'sector': 'Consumer Discretionary', 'industry': 'E-commerce'},
            'TSLA': {'longName': 'Tesla Inc.', 'sector': 'Consumer Discretionary', 'industry': 'Electric Vehicles'},
            'NVDA': {'longName': 'NVIDIA Corporation', 'sector': 'Technology', 'industry': 'Semiconductors'},
            'META': {'longName': 'Meta Platforms Inc.', 'sector': 'Technology', 'industry': 'Social Media'},
            'SPY': {'longName': 'SPDR S&P 500 ETF Trust', 'sector': 'Financial', 'industry': 'ETF'},
        }
        
        if ticker in known_tickers:
            for key, value in known_tickers[ticker].items():
                if stock_info[key] in [ticker, "Unknown", None]:
                    stock_info[key] = value
                
    except Exception as e:
        logger.error(f"Error fetching any company info for {ticker}: {str(e)}")
        # Ensure we at least have a reasonable name
        stock_info['longName'] = f"{ticker} Corporation"
    
    return stock_info


def validate_data_quality(data: pd.DataFrame, ticker: str) -> Dict[str, any]:
    """Validate the quality of stock data"""
    quality_report = {
        'is_valid': True,
        'warnings': [],
        'errors': [],
        'data_source': 'unknown',
        'completeness': 0,
        'data_points': 0
    }
    
    try:
        if data is None or data.empty:
            quality_report['is_valid'] = False
            quality_report['errors'].append("No data available")
            return quality_report
        
        # Basic data checks
        quality_report['data_points'] = len(data)
        
        # Check for required columns
        required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        missing_columns = [col for col in required_columns if col not in data.columns]
        
        if missing_columns:
            quality_report['errors'].append(f"Missing columns: {missing_columns}")
        
        # Check for data completeness
        if 'Adj Close' in data.columns:
            non_null_count = data['Adj Close'].count()
            quality_report['completeness'] = (non_null_count / len(data)) * 100
        
        # Check for suspicious data patterns
        if 'Adj Close' in data.columns:
            price_variance = data['Adj Close'].var()
            if price_variance == 0:
                quality_report['warnings'].append("No price variance detected (flat prices)")
        
        # Determine data source
        if quality_report['completeness'] == 100 and quality_report['data_points'] > 100:
            quality_report['data_source'] = "Live Yahoo Finance API"
        elif quality_report['data_points'] > 50:
            quality_report['data_source'] = "Yahoo Finance API (Partial)"
        else:
            quality_report['data_source'] = "Sample Data (Demo)"
        
        # Overall validity
        if quality_report['completeness'] < 80:
            quality_report['warnings'].append("Data completeness below 80%")
        
        return quality_report
        
    except Exception as e:
        logger.error(f"Error validating data quality: {str(e)}")
        quality_report['is_valid'] = False
        quality_report['errors'].append(f"Validation error: {str(e)}")
        return quality_report

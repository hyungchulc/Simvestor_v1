"""
Analysis and calculation module for SimVestor
Handles returns calculation, technical indicators, and insights
"""

import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import streamlit as st

logger = logging.getLogger(__name__)

# Try to import ML libraries
try:
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.linear_model import LinearRegression
    from sklearn.preprocessing import MinMaxScaler
    from sklearn.metrics import mean_squared_error
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    logger.warning("Machine learning libraries not available. Predictions will be disabled.")


def get_price_column(data):
    """Get the appropriate price column from yfinance data"""
    if 'Adj Close' in data.columns:
        return 'Adj Close'
    elif 'Close' in data.columns:
        return 'Close'
    elif hasattr(data.columns, 'levels') and len(data.columns.levels) > 1:
        # Handle MultiIndex columns from yfinance
        for col in data.columns:
            if isinstance(col, tuple) and 'Adj Close' in col:
                return col
            elif isinstance(col, tuple) and 'Close' in col:
                return col
    
    # If none found, try the first numeric column
    for col in data.columns:
        try:
            if pd.api.types.is_numeric_dtype(data[col]):
                return col
        except:
            continue
    
    return None


def calculate_returns(data, investment_amount):
    """Calculate investment returns"""
    if data is None or data.empty:
        return None
    
    # Handle different yfinance data structures
    close_col = get_price_column(data)
    
    if close_col is None:
        logger.error(f"Could not find price column in data. Available columns: {list(data.columns)}")
        return None
    
    try:
        initial_price = data[close_col].iloc[0]
        final_price = data[close_col].iloc[-1]
        
        shares = investment_amount / initial_price
        final_value = shares * final_price
        
        total_return = final_value - investment_amount
        percent_return = (final_value / investment_amount - 1) * 100
        
        # Calculate additional metrics
        daily_returns = data[close_col].pct_change().dropna()
        volatility = daily_returns.std() * np.sqrt(252) * 100  # Annualized volatility
        
        # Calculate max drawdown
        cumulative = (1 + daily_returns).cumprod()
        rolling_max = cumulative.cummax()
        drawdown = (cumulative - rolling_max) / rolling_max
        max_drawdown = drawdown.min() * 100
        
        return {
            'initial_investment': investment_amount,
            'final_value': final_value,
            'total_return': total_return,
            'percent_return': percent_return,
            'shares': shares,
            'initial_price': initial_price,
            'final_price': final_price,
            'volatility': volatility,
            'max_drawdown': max_drawdown,
            'days_invested': len(data)
        }
    
    except Exception as e:
        logger.error(f"Error calculating returns: {str(e)}")
        return None


def calculate_rsi(prices, window=14):
    """Calculate RSI indicator"""
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def calculate_technical_indicators(data: pd.DataFrame) -> Dict:
    """Calculate technical indicators for stock analysis"""
    try:
        if data is None or data.empty:
            return {}
        
        # Get the appropriate price column
        close_col = get_price_column(data)
        if close_col is None:
            return {}
        
        # Calculate various technical indicators
        indicators = {}
        
        # Moving averages
        indicators['MA_20'] = data[close_col].rolling(window=20).mean().iloc[-1]
        indicators['MA_50'] = data[close_col].rolling(window=50).mean().iloc[-1]
        indicators['MA_200'] = data[close_col].rolling(window=200).mean().iloc[-1]
        
        # Current price
        current_price = data[close_col].iloc[-1]
        indicators['current_price'] = current_price
        
        # Price vs Moving Averages
        indicators['price_vs_ma20'] = ((current_price - indicators['MA_20']) / indicators['MA_20']) * 100 if indicators['MA_20'] else 0
        indicators['price_vs_ma50'] = ((current_price - indicators['MA_50']) / indicators['MA_50']) * 100 if indicators['MA_50'] else 0
        indicators['price_vs_ma200'] = ((current_price - indicators['MA_200']) / indicators['MA_200']) * 100 if indicators['MA_200'] else 0
        
        # RSI
        indicators['RSI'] = calculate_rsi(data[close_col]).iloc[-1]
        
        # Bollinger Bands
        rolling_mean = data[close_col].rolling(window=20).mean()
        rolling_std = data[close_col].rolling(window=20).std()
        indicators['BB_upper'] = (rolling_mean + (rolling_std * 2)).iloc[-1]
        indicators['BB_lower'] = (rolling_mean - (rolling_std * 2)).iloc[-1]
        indicators['BB_width'] = indicators['BB_upper'] - indicators['BB_lower']
        
        # Volume analysis (if available)
        if 'Volume' in data.columns:
            indicators['avg_volume'] = data['Volume'].rolling(window=20).mean().iloc[-1]
            indicators['current_volume'] = data['Volume'].iloc[-1]
            indicators['volume_ratio'] = indicators['current_volume'] / indicators['avg_volume'] if indicators['avg_volume'] > 0 else 1
        else:
            indicators['avg_volume'] = 0
            indicators['current_volume'] = 0
            indicators['volume_ratio'] = 1
        
        # Trend analysis
        price_change_20d = ((current_price - data[close_col].iloc[-21]) / data[close_col].iloc[-21]) * 100 if len(data) > 21 else 0
        price_change_50d = ((current_price - data[close_col].iloc[-51]) / data[close_col].iloc[-51]) * 100 if len(data) > 51 else 0
        
        indicators['price_change_20d'] = price_change_20d
        indicators['price_change_50d'] = price_change_50d
        
        return indicators
    except Exception as e:
        logger.error(f"Error calculating technical indicators: {str(e)}")
        return {}


def generate_investment_insights(returns: Dict, indicators: Dict, stock_info: Dict) -> List[str]:
    """Generate AI-powered investment insights"""
    insights = []
    
    try:
        # Performance insights
        if returns['percent_return'] > 20:
            insights.append("🟢 **Strong Performance**: This investment has delivered exceptional returns above 20%.")
        elif returns['percent_return'] > 10:
            insights.append("🟡 **Good Performance**: Solid returns above 10%, beating most savings accounts.")
        elif returns['percent_return'] > 0:
            insights.append("🟡 **Positive Returns**: Modest gains, but still outperforming cash.")
        else:
            insights.append("🔴 **Negative Returns**: This investment has declined in value.")
        
        # Risk insights
        if returns['volatility'] > 40:
            insights.append("⚠️ **High Volatility**: This stock shows significant price swings. Consider position sizing.")
        elif returns['volatility'] > 25:
            insights.append("🟡 **Moderate Volatility**: Normal price fluctuations for growth stocks.")
        else:
            insights.append("🟢 **Low Volatility**: Relatively stable price movements.")
        
        # Technical insights
        if indicators:
            if indicators.get('RSI', 50) > 70:
                insights.append("📈 **Overbought Territory**: RSI above 70 suggests potential pullback ahead.")
            elif indicators.get('RSI', 50) < 30:
                insights.append("📉 **Oversold Territory**: RSI below 30 suggests potential bounce ahead.")
            
            if indicators.get('price_vs_ma20', 0) > 5:
                insights.append("🔥 **Above Moving Average**: Price is trending above 20-day average.")
            elif indicators.get('price_vs_ma20', 0) < -5:
                insights.append("❄️ **Below Moving Average**: Price is trending below 20-day average.")
        
        # Sector insights
        sector = stock_info.get('sector', '').lower()
        if 'technology' in sector:
            insights.append("💻 **Tech Sector**: Consider market cycles and innovation trends.")
        elif 'healthcare' in sector:
            insights.append("🏥 **Healthcare**: Defensive sector with steady demand.")
        elif 'financial' in sector:
            insights.append("🏦 **Financials**: Sensitive to interest rates and economic cycles.")
        
        # Drawdown warning
        if returns['max_drawdown'] < -30:
            insights.append("⚠️ **High Drawdown**: Maximum decline exceeded 30%. Review risk tolerance.")
        
        return insights
    except Exception as e:
        logger.error(f"Error generating insights: {str(e)}")
        return ["📊 Unable to generate insights at this time."]


def simple_prediction_model(data, days_ahead=30):
    """Simple prediction using linear regression and moving averages"""
    if not ML_AVAILABLE:
        return None
        
    if data is None or len(data) < 30:
        return None
    
    # Get the appropriate price column
    close_col = get_price_column(data)
    if close_col is None:
        return None
    
    # Prepare features
    df = data.copy()
    df['MA_7'] = df[close_col].rolling(window=7).mean()
    df['MA_21'] = df[close_col].rolling(window=21).mean()
    df['RSI'] = calculate_rsi(df[close_col])
    df['Price_Change'] = df[close_col].pct_change()
    
    # Drop NaN values
    df = df.dropna()
    
    if len(df) < 10:
        return None
    
    # Features and target
    features = ['MA_7', 'MA_21', 'RSI']
    X = df[features].values
    y = df[close_col].values
    
    # Split data
    split_idx = int(len(X) * 0.8)
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]
    
    # Scale features
    scaler = MinMaxScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train models
    models = {
        'Linear Regression': LinearRegression(),
        'Random Forest': RandomForestRegressor(n_estimators=50, random_state=42)
    }
    
    best_model = None
    best_score = float('inf')
    model_name = ''
    
    for name, model in models.items():
        model.fit(X_train_scaled, y_train)
        pred = model.predict(X_test_scaled)
        mse = mean_squared_error(y_test, pred)
        
        if mse < best_score:
            best_score = mse
            best_model = model
            model_name = name
    
    # Make predictions
    last_features = X[-days_ahead:]
    last_features_scaled = scaler.transform(last_features)
    predictions = best_model.predict(last_features_scaled)
    
    # Create future dates
    last_date = df.index[-1]
    future_dates = pd.date_range(start=last_date + timedelta(days=1), periods=days_ahead, freq='D')
    
    return {
        'predictions': predictions,
        'dates': future_dates,
        'model_name': model_name,
        'mse': best_score,
        'accuracy': 1 - (np.sqrt(best_score) / np.mean(y_test))
    }

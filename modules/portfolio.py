"""
Portfolio management module for SimVestor
Handles portfolio tracking, comparison, and benchmark analysis
"""

import pandas as pd
import logging
from datetime import datetime
from typing import Optional, Dict
import streamlit as st
import plotly.graph_objects as go

from .data_fetcher import fetch_stock_data
from .analysis import calculate_returns

logger = logging.getLogger(__name__)


def add_to_portfolio(ticker: str, data: pd.DataFrame, stock_info: dict, 
                    investment_amount: float, start_date: datetime) -> bool:
    """Add an investment to the portfolio for comparison"""
    try:
        returns = calculate_returns(data, investment_amount)
        if returns is None:
            return False
        
        portfolio_entry = {
            'ticker': ticker,
            'investment_amount': investment_amount,
            'start_date': start_date,
            'returns': returns,
            'stock_info': stock_info,
            'date_added': datetime.now()
        }
        
        # Add to portfolio
        st.session_state.portfolio[ticker] = portfolio_entry
        
        # Keep only last 10 entries
        if len(st.session_state.portfolio) > 10:
            oldest_key = min(st.session_state.portfolio.keys(), 
                           key=lambda k: st.session_state.portfolio[k]['date_added'])
            del st.session_state.portfolio[oldest_key]
        
        return True
    except Exception as e:
        logger.error(f"Error adding {ticker} to portfolio: {str(e)}")
        return False


def compare_portfolio_performance() -> Optional[pd.DataFrame]:
    """Compare performance of all stocks in portfolio"""
    if not st.session_state.portfolio:
        return None
    
    comparison_data = []
    
    for ticker, entry in st.session_state.portfolio.items():
        returns = entry['returns']
        stock_info = entry['stock_info']
        
        comparison_data.append({
            'Ticker': ticker,
            'Company': stock_info.get('longName', ticker),
            'Investment': f"${entry['investment_amount']:,.0f}",
            'Final Value': f"${returns['final_value']:,.0f}",
            'Total Return': f"${returns['total_return']:,.0f}",
            'Return %': f"{returns['percent_return']:.2f}%",
            'Volatility': f"{returns['volatility']:.2f}%",
            'Max Drawdown': f"{returns['max_drawdown']:.2f}%",
            'Days': returns['days_invested'],
            'Start Date': entry['start_date'].strftime('%Y-%m-%d')
        })
    
    return pd.DataFrame(comparison_data)


def create_portfolio_comparison_chart() -> Optional[go.Figure]:
    """Create a portfolio comparison chart"""
    if not st.session_state.portfolio:
        return None
    
    fig = go.Figure()
    
    for ticker, entry in st.session_state.portfolio.items():
        returns = entry['returns']
        fig.add_trace(go.Bar(
            x=[ticker],
            y=[returns['percent_return']],
            name=ticker,
            text=f"{returns['percent_return']:.1f}%",
            textposition='auto',
            marker_color='green' if returns['percent_return'] > 0 else 'red'
        ))
    
    fig.update_layout(
        title="Portfolio Performance Comparison",
        xaxis_title="Ticker",
        yaxis_title="Return (%)",
        showlegend=False,
        height=400
    )
    
    return fig


def get_market_benchmark_data(start_date: datetime) -> Optional[pd.DataFrame]:
    """Get S&P 500 data for benchmarking"""
    try:
        logger.info(f"Fetching SPY benchmark data from {start_date}")
        spy_data, spy_info = fetch_stock_data("SPY", start_date)
        if spy_data is not None and not spy_data.empty:
            logger.info(f"Successfully fetched {len(spy_data)} days of SPY data")
            return spy_data
        else:
            logger.error(f"Failed to fetch SPY data - no data returned")
            return None
    except Exception as e:
        logger.error(f"Error fetching benchmark data: {str(e)}")
        return None


def calculate_benchmark_comparison(returns: dict, benchmark_data: pd.DataFrame, 
                                investment_amount: float) -> dict:
    """Compare performance against S&P 500 benchmark"""
    try:
        if benchmark_data is None or benchmark_data.empty:
            logger.error("No benchmark data provided for comparison")
            return {}
        
        logger.info(f"Calculating benchmark comparison with {len(benchmark_data)} days of data")
        benchmark_returns = calculate_returns(benchmark_data, investment_amount)
        
        if benchmark_returns is None:
            logger.error("Could not calculate benchmark returns")
            return {}
        
        alpha = returns['percent_return'] - benchmark_returns['percent_return']
        
        result = {
            'benchmark_return': benchmark_returns['percent_return'],
            'alpha': alpha,
            'outperformed': alpha > 0,
            'benchmark_volatility': benchmark_returns['volatility'],
            'relative_volatility': returns['volatility'] - benchmark_returns['volatility'],
            'benchmark_initial_price': benchmark_returns['initial_price'],
            'benchmark_final_price': benchmark_returns['final_price'],
            'benchmark_final_value': benchmark_returns['final_value']
        }
        
        logger.info(f"Benchmark comparison completed: Alpha = {alpha:.2f}%")
        return result
        
    except Exception as e:
        logger.error(f"Error calculating benchmark comparison: {str(e)}")
        return {}

"""
Visualization module for SimVestor
Handles chart creation and data presentation
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import streamlit as st
import logging
from typing import Dict

logger = logging.getLogger(__name__)


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


def create_price_chart(data, ticker, investment_amount):
    """Create interactive price chart"""
    if data is None or data.empty:
        return None
    
    try:
        # Get the appropriate price column
        close_col = get_price_column(data)
        if close_col is None:
            st.error(f"Could not find price column in data for {ticker}")
            return None
        
        # Calculate investment value over time
        initial_price = data[close_col].iloc[0]
        if initial_price <= 0:
            st.error(f"Invalid initial price for {ticker}: {initial_price}")
            return None
            
        shares = investment_amount / initial_price
        data['Investment_Value'] = data[close_col] * shares
        
        fig = go.Figure()
        
        # Add price line (left y-axis)
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data[close_col],
            mode='lines',
            name=f'{ticker} Price',
            line=dict(color='#1f77b4', width=2),
            yaxis='y',
            hovertemplate='<b>%{fullData.name}</b><br>' +
                         'Date: %{x}<br>' +
                         'Price: $%{y:.2f}<extra></extra>'
        ))
        
        # Add investment value line (right y-axis)
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['Investment_Value'],
            mode='lines',
            name='Investment Value',
            line=dict(color='#ff7f0e', width=2),
            yaxis='y2',
            hovertemplate='<b>%{fullData.name}</b><br>' +
                         'Date: %{x}<br>' +
                         'Value: $%{y:.2f}<extra></extra>'
        ))
        
        # Calculate price range for better y-axis scaling
        price_range = data[close_col].max() - data[close_col].min()
        price_padding = price_range * 0.1
        
        investment_range = data['Investment_Value'].max() - data['Investment_Value'].min()
        investment_padding = investment_range * 0.1
        
        # Update layout with better formatting
        fig.update_layout(
            title=f'{ticker} Performance Analysis<br><sub>Initial Investment: ${investment_amount:,.0f} | Shares: {shares:.2f}</sub>',
            xaxis_title='Date',
            yaxis=dict(
                title=dict(
                    text='Stock Price ($)',
                    font=dict(color='#1f77b4', size=14)
                ),
                tickfont=dict(color='#1f77b4'),
                range=[data[close_col].min() - price_padding, data[close_col].max() + price_padding]
            ),
            yaxis2=dict(
                title=dict(
                    text='Investment Value ($)',
                    font=dict(color='#ff7f0e', size=14)
                ),
                tickfont=dict(color='#ff7f0e'),
                overlaying='y',
                side='right',
                range=[data['Investment_Value'].min() - investment_padding, data['Investment_Value'].max() + investment_padding]
            ),
            hovermode='x unified',
            height=500,
            showlegend=True,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
            ),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        # Add grid
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
        
        return fig
        
    except Exception as e:
        st.error(f"Error creating price chart for {ticker}: {str(e)}")
        return None


def create_data_quality_report(quality_report: Dict) -> None:
    """Display data quality report in Streamlit"""
    try:
        with st.expander("📊 Data Quality Report", expanded=False):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                status_color = "🟢" if quality_report['is_valid'] else "🔴"
                st.metric("Data Status", f"{status_color} {'Valid' if quality_report['is_valid'] else 'Invalid'}")
            
            with col2:
                st.metric("Data Points", quality_report['data_points'])
            
            with col3:
                st.metric("Completeness", f"{quality_report['completeness']:.1f}%")
            
            # Data source indicator
            source_emoji = "🟢" if "Live" in quality_report['data_source'] else "🟡" if "Partial" in quality_report['data_source'] else "🔴"
            st.write(f"**Data Source:** {source_emoji} {quality_report['data_source']}")
            
            # Show warnings and errors
            if quality_report['warnings']:
                st.warning("**Warnings:** " + "; ".join(quality_report['warnings']))
            
            if quality_report['errors']:
                st.error("**Errors:** " + "; ".join(quality_report['errors']))
            
            if not quality_report['warnings'] and not quality_report['errors']:
                st.success("No data quality issues detected!")
    
    except Exception as e:
        st.error(f"Error displaying data quality report: {str(e)}")


def format_technical_indicators(indicators: Dict) -> None:
    """Format and display technical indicators"""
    if not indicators:
        st.warning("Technical indicators could not be calculated.")
        return
    
    try:
        # Price and Moving Averages
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**📈 Price & Moving Averages**")
            price_data = {
                'Metric': ['Current Price', '20-Day MA', '50-Day MA', '200-Day MA'],
                'Value': [
                    f"${indicators.get('current_price', 0):.2f}",
                    f"${indicators.get('MA_20', 0):.2f}",
                    f"${indicators.get('MA_50', 0):.2f}",
                    f"${indicators.get('MA_200', 0):.2f}"
                ],
                'vs Price': [
                    "-",
                    f"{indicators.get('price_vs_ma20', 0):+.1f}%",
                    f"{indicators.get('price_vs_ma50', 0):+.1f}%",
                    f"{indicators.get('price_vs_ma200', 0):+.1f}%"
                ]
            }
            st.dataframe(pd.DataFrame(price_data), hide_index=True)
        
        with col2:
            st.write("**📊 Technical Indicators**")
            tech_data = {
                'Indicator': ['RSI (14)', 'Bollinger Upper', 'Bollinger Lower', 'BB Width'],
                'Value': [
                    f"{indicators.get('RSI', 0):.1f}",
                    f"${indicators.get('BB_upper', 0):.2f}",
                    f"${indicators.get('BB_lower', 0):.2f}",
                    f"${indicators.get('BB_width', 0):.2f}"
                ]
            }
            st.dataframe(pd.DataFrame(tech_data), hide_index=True)
        
        # Volume Analysis
        st.write("**📊 Volume Analysis**")
        vol_col1, vol_col2, vol_col3 = st.columns(3)
        
        with vol_col1:
            st.metric("Current Volume", f"{indicators.get('current_volume', 0):,.0f}")
        
        with vol_col2:
            st.metric("20-Day Avg Volume", f"{indicators.get('avg_volume', 0):,.0f}")
        
        with vol_col3:
            volume_ratio = indicators.get('volume_ratio', 1)
            st.metric("Volume Ratio", f"{volume_ratio:.2f}x", 
                     delta=f"{(volume_ratio - 1) * 100:+.0f}%")
        
        # Trend Analysis
        st.write("**📈 Price Trends**")
        trend_col1, trend_col2 = st.columns(2)
        
        with trend_col1:
            change_20d = indicators.get('price_change_20d', 0)
            st.metric("20-Day Change", f"{change_20d:+.2f}%",
                     delta=None if change_20d == 0 else f"{change_20d:+.2f}%")
        
        with trend_col2:
            change_50d = indicators.get('price_change_50d', 0)
            st.metric("50-Day Change", f"{change_50d:+.2f}%",
                     delta=None if change_50d == 0 else f"{change_50d:+.2f}%")
        
    except Exception as e:
        st.error(f"Error displaying technical indicators: {str(e)}")


def display_company_info(stock_info):
    """Display formatted company information"""
    try:
        if isinstance(stock_info, dict):
            info_data = {
                'Company': stock_info.get('longName', 'N/A'),
                'Sector': stock_info.get('sector', 'Unknown'),
                'Industry': stock_info.get('industry', 'Unknown'),
                'Market Cap': f"${stock_info.get('marketCap', 0):,.0f}" if stock_info.get('marketCap') else 'N/A',
                'P/E Ratio': f"{stock_info.get('peRatio', 0):.2f}" if stock_info.get('peRatio') else 'N/A',
                'Beta': f"{stock_info.get('beta', 0):.2f}" if stock_info.get('beta') else 'N/A'
            }
            
            for key, value in info_data.items():
                st.write(f"**{key}**: {value}")
        else:
            st.write("Company information not available")
    except Exception as e:
        st.error(f"Error displaying company info: {str(e)}")

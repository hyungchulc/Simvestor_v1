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
    """Create interactive price chart showing investment value over time"""
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
        
        # Add investment value line 
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['Investment_Value'],
            mode='lines',
            name=f'{ticker} Investment Value',
            line=dict(color='#2E8B57', width=3),
            connectgaps=False,
            hovertemplate='<b>%{fullData.name}</b><br>' +
                         'Date: %{x}<br>' +
                         'Value: $%{y:,.2f}<br>' +
                         'Return: %{customdata:.2f}%<extra></extra>',
            customdata=((data['Investment_Value'] / investment_amount - 1) * 100)
        ))
        
        # Update layout with clean styling
        fig.update_layout(
            title=dict(
                text=f'{ticker} Investment Performance<br><sub>Initial Investment: ${investment_amount:,.0f} | Shares: {shares:.4f}</sub>',
                font=dict(size=16),
                x=0.5
            ),
            xaxis=dict(
                title='Date',
                gridcolor='rgba(128,128,128,0.2)',
                showgrid=True
            ),
            yaxis=dict(
                title='Investment Value ($)',
                gridcolor='rgba(128,128,128,0.2)',
                showgrid=True
            ),
            hovermode='x unified',
            height=500,
            showlegend=False,  # Hide legend for cleaner look
            # Dark mode compatible styling
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='rgba(128,128,128,1)'),
            margin=dict(t=80, b=50, l=50, r=50)
        )
        
        # Responsive grid styling
        fig.update_xaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(128,128,128,0.2)',
            showline=True,
            linewidth=1,
            linecolor='rgba(128,128,128,0.3)'
        )
        fig.update_yaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(128,128,128,0.2)',
            showline=True,
            linewidth=1,
            linecolor='rgba(128,128,128,0.3)'
        )
        
        return fig
        
    except Exception as e:
        st.error(f"Error creating price chart for {ticker}: {str(e)}")
        return None


def create_comparison_chart(stock_data, benchmark_data, ticker, investment_amount):
    """Create comparison chart between stock and benchmark (S&P 500)"""
    if stock_data is None or stock_data.empty or benchmark_data is None or benchmark_data.empty:
        return None
    
    try:
        # Get price columns for both datasets
        stock_close_col = get_price_column(stock_data)
        benchmark_close_col = get_price_column(benchmark_data)
        
        if stock_close_col is None or benchmark_close_col is None:
            st.error("Could not find price columns for comparison")
            return None
        
        # Calculate normalized returns (starting from 100%)
        stock_initial = stock_data[stock_close_col].iloc[0]
        benchmark_initial = benchmark_data[benchmark_close_col].iloc[0]
        
        # Align dates by getting common date range
        common_dates = stock_data.index.intersection(benchmark_data.index)
        if len(common_dates) < 10:
            st.error("Not enough overlapping data for comparison")
            return None
        
        stock_aligned = stock_data.loc[common_dates]
        benchmark_aligned = benchmark_data.loc[common_dates]
        
        # Calculate percentage returns from start date
        stock_returns = ((stock_aligned[stock_close_col] / stock_aligned[stock_close_col].iloc[0]) - 1) * 100
        benchmark_returns = ((benchmark_aligned[benchmark_close_col] / benchmark_aligned[benchmark_close_col].iloc[0]) - 1) * 100
        
        fig = go.Figure()
        
        # Add stock performance
        fig.add_trace(go.Scatter(
            x=common_dates,
            y=stock_returns,
            mode='lines',
            name=f'{ticker}',
            line=dict(color='#2E8B57', width=3),
            connectgaps=False,
            hovertemplate='<b>%{fullData.name}</b><br>' +
                         'Date: %{x}<br>' +
                         'Return: %{y:.2f}%<extra></extra>'
        ))
        
        # Add benchmark performance
        fig.add_trace(go.Scatter(
            x=common_dates,
            y=benchmark_returns,
            mode='lines',
            name='S&P 500 (SPY)',
            line=dict(color='#DC143C', width=2, dash='dash'),
            connectgaps=False,
            hovertemplate='<b>%{fullData.name}</b><br>' +
                         'Date: %{x}<br>' +
                         'Return: %{y:.2f}%<extra></extra>'
        ))
        
        # Add zero line for reference
        fig.add_hline(y=0, line_dash="dot", line_color="gray", opacity=0.5)
        
        # Calculate final returns for subtitle
        final_stock_return = stock_returns.iloc[-1]
        final_benchmark_return = benchmark_returns.iloc[-1]
        outperformance = final_stock_return - final_benchmark_return
        
        fig.update_layout(
            title=dict(
                text=f'{ticker} vs S&P 500 Performance Comparison<br>' +
                     f'<sub>{ticker}: {final_stock_return:+.2f}% | S&P 500: {final_benchmark_return:+.2f}% | ' +
                     f'Alpha: {outperformance:+.2f}%</sub>',
                font=dict(size=16),
                x=0.5
            ),
            xaxis=dict(
                title='Date',
                gridcolor='rgba(128,128,128,0.2)',
                showgrid=True,
                zeroline=False
            ),
            yaxis=dict(
                title='Cumulative Return (%)',
                gridcolor='rgba(128,128,128,0.2)',
                showgrid=True,
                zeroline=True,
                zerolinecolor='rgba(128,128,128,0.5)',
                zerolinewidth=1
            ),
            hovermode='x unified',
            height=500,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5
            ),
            # Dark mode compatible styling
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='rgba(128,128,128,1)'),
            margin=dict(t=100, b=50, l=50, r=50)
        )
        
        # Responsive grid styling
        fig.update_xaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(128,128,128,0.2)',
            showline=True,
            linewidth=1,
            linecolor='rgba(128,128,128,0.3)'
        )
        fig.update_yaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(128,128,128,0.2)',
            showline=True,
            linewidth=1,
            linecolor='rgba(128,128,128,0.3)'
        )
        
        return fig
        
    except Exception as e:
        st.error(f"Error creating comparison chart: {str(e)}")
        return None


def create_yearly_comparison_chart(data, ticker):
    """Create year-over-year comparison chart (2024 vs 2025)"""
    if data is None or data.empty:
        return None
    
    try:
        close_col = get_price_column(data)
        if close_col is None:
            return None
        
        # Filter data for 2024 and 2025
        data_2024 = data[data.index.year == 2024]
        data_2025 = data[data.index.year == 2025]
        
        if len(data_2024) < 5 or len(data_2025) < 5:
            return None  # Not enough data for comparison
        
        fig = go.Figure()
        
        # Normalize data to show percentage change from year start
        if len(data_2024) > 0:
            data_2024_norm = ((data_2024[close_col] / data_2024[close_col].iloc[0]) - 1) * 100
            fig.add_trace(go.Scatter(
                x=data_2024.index.dayofyear,
                y=data_2024_norm,
                mode='lines',
                name='2024',
                line=dict(color='#1f77b4', width=2),
                hovertemplate='<b>2024</b><br>Day of Year: %{x}<br>Return: %{y:.2f}%<extra></extra>'
            ))
        
        if len(data_2025) > 0:
            data_2025_norm = ((data_2025[close_col] / data_2025[close_col].iloc[0]) - 1) * 100
            fig.add_trace(go.Scatter(
                x=data_2025.index.dayofyear,
                y=data_2025_norm,
                mode='lines',
                name='2025',
                line=dict(color='#ff7f0e', width=2),
                hovertemplate='<b>2025</b><br>Day of Year: %{x}<br>Return: %{y:.2f}%<extra></extra>'
            ))
        
        # Add zero line
        fig.add_hline(y=0, line_dash="dot", line_color="gray", opacity=0.5)
        
        fig.update_layout(
            title=f'{ticker} Year-over-Year Comparison (2024 vs 2025)',
            xaxis=dict(
                title='Day of Year',
                gridcolor='rgba(128,128,128,0.2)',
                showgrid=True
            ),
            yaxis=dict(
                title='Return from Year Start (%)',
                gridcolor='rgba(128,128,128,0.2)',
                showgrid=True
            ),
            height=400,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5
            ),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='rgba(128,128,128,1)'),
            margin=dict(t=60, b=50, l=50, r=50)
        )
        
        fig.update_xaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(128,128,128,0.2)'
        )
        fig.update_yaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(128,128,128,0.2)'
        )
        
        return fig
        
    except Exception as e:
        st.error(f"Error creating yearly comparison chart: {str(e)}")
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

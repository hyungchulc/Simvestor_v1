"""
SimVestor - AI-Powered Investment Simulation App
Modular version with improved maintainability
"""

import streamlit as st
import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
import plotly.graph_objects as go

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import custom modules
from modules.data_fetcher import fetch_stock_data, validate_data_quality
from modules.analysis import calculate_returns, calculate_technical_indicators, generate_investment_insights, simple_prediction_model, ML_AVAILABLE, get_price_column
from modules.news import get_stock_news
from modules.portfolio import add_to_portfolio, compare_portfolio_performance, create_portfolio_comparison_chart, get_market_benchmark_data, calculate_benchmark_comparison
from modules.visualization import create_price_chart, create_data_quality_report, format_technical_indicators, display_company_info
from modules.utils import get_theme_dictionary, export_results_to_json

# Page configuration
st.set_page_config(
    page_title="SimVestor - AI Investment Simulator",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'simulation_run' not in st.session_state:
    st.session_state.simulation_run = False
if 'last_ticker' not in st.session_state:
    st.session_state.last_ticker = None
if 'last_results' not in st.session_state:
    st.session_state.last_results = None
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = {}
if 'comparison_results' not in st.session_state:
    st.session_state.comparison_results = {}

# Main app title and description
st.title("📈 SimVestor")
st.markdown("**AI-Powered Investment Simulation & Analysis Platform**")

# Sidebar for user inputs
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Theme/Ticker selection
    theme_dict = get_theme_dictionary()
    
    # Create categorized themes
    theme_categories = {
        "💻 Technology & Innovation": [
            "artificial intelligence", "ai", "technology", "cloud computing", 
            "cybersecurity", "fintech", "semiconductor", "software", "internet",
            "data analytics", "quantum computing"
        ],
        "🔋 Energy & Environment": [
            "clean energy", "renewable energy", "solar", "electric vehicles", 
            "ev", "oil", "energy", "utilities", "wind energy"
        ],
        "🏥 Healthcare & Biotech": [
            "healthcare", "biotech", "pharmaceuticals", "medical", 
            "genomics", "telemedicine"
        ],
        "🛍️ Consumer & Lifestyle": [
            "gaming", "streaming", "social media", "ecommerce", "retail", 
            "travel", "food", "consumer discretionary", "consumer staples",
            "luxury goods", "fitness"
        ],
        "🏦 Financial Services": [
            "banking", "financial", "insurance", "real estate", 
            "cryptocurrency", "blockchain", "payments"
        ],
        "🏭 Industrial & Materials": [
            "aerospace", "defense", "infrastructure", "transportation", 
            "construction", "industrials", "robotics", "automation",
            "gold", "silver", "copper", "lithium", "materials"
        ],
        "📱 Communications & Media": [
            "communication", "media", "telecom", "advertising", "content creation"
        ],
        "📊 Market Indices": [
            "sp500", "nasdaq", "dow", "market", "index", "small cap", "mid cap"
        ],
        "🌍 Global Markets": [
            "emerging", "international", "europe", "asia", "china", "japan", "india"
        ],
        "⭐ Popular Stocks": [
            "apple", "microsoft", "amazon", "google", "tesla", "nvidia", 
            "meta", "netflix", "berkshire", "jpmorgan"
        ]
    }
    
    # Theme selection method
    st.subheader("🎯 Select Investment Theme")
    selection_method = st.radio(
        "Choose selection method:",
        ["Browse by Category", "Search All Themes"],
        horizontal=True
    )
    
    if selection_method == "Browse by Category":
        # Category-based selection
        selected_category = st.selectbox(
            "📂 Choose Category:",
            list(theme_categories.keys())
        )
        
        available_themes = theme_categories[selected_category]
        selected_theme = st.selectbox(
            "🎯 Choose Theme:",
            available_themes
        )
    else:
        # Search all themes
        search_term = st.text_input(
            "🔍 Search themes:",
            placeholder="e.g., apple, cloud, energy..."
        )
        
        if search_term:
            # Filter themes based on search
            matching_themes = [theme for theme in theme_dict.keys() 
                             if search_term.lower() in theme.lower()]
            
            if matching_themes:
                selected_theme = st.selectbox(
                    "🎯 Matching Themes:",
                    matching_themes
                )
            else:
                st.warning("No matching themes found. Try a different search term.")
                selected_theme = "apple"  # Default fallback
        else:
            selected_theme = "apple"  # Default
    
    # Get ticker from selected theme
    suggested_ticker = theme_dict[selected_theme]
    
    # Show theme-ticker mapping with better styling
    st.success(f"🎯 **{selected_theme.replace('_', ' ').title()}** → **{suggested_ticker}**")
    
    # Option 2: Custom ticker (with suggested ticker as default)
    st.subheader("📝 Customize Ticker (Optional)")
    
    custom_ticker = st.text_input(
        "Enter custom ticker symbol:", 
        value="",
        placeholder=f"Leave empty to use {suggested_ticker}",
        help=f"Current suggestion: {suggested_ticker}. Make sure to use correct ticker symbols!"
    )
    
    # Final ticker selection with validation
    if custom_ticker.strip():
        ticker = custom_ticker.strip().upper()
        if ticker != suggested_ticker:
            st.info(f"Using custom ticker: **{ticker}** (instead of {suggested_ticker})")
    else:
        ticker = suggested_ticker
    
    st.divider()
    
    # Investment parameters
    st.subheader("💰 Investment Parameters")
    
    # Date selection - Extended range for more historical data
    max_date = datetime.now() - timedelta(days=1)
    min_date = max_date - timedelta(days=365*10)  # 10 years of history
    
    start_date = st.date_input(
        "📅 Investment Start Date",
        value=max_date - timedelta(days=365*2),  # Default to 2 years ago
        min_value=min_date,
        max_value=max_date,
        help="Choose when you would have invested"
    )
    
    investment_amount = st.number_input(
        "💵 Investment Amount ($)",
        min_value=100,
        max_value=1000000,
        value=10000,
        step=100,
        help="How much would you have invested?"
    )
    
    st.divider()
    
    # Analysis options
    st.subheader("🔬 Analysis Options")
    show_prediction = st.checkbox("🔮 Show AI Price Prediction", value=True)
    
    if show_prediction:
        prediction_days = st.slider(
            "📈 Prediction Days", 
            min_value=7, 
            max_value=60, 
            value=30,
            help="How many days ahead to predict"
        )
    else:
        prediction_days = 30
    
    st.divider()
    
    # Control buttons
    col1, col2 = st.columns(2)
    
    with col1:
        # Run simulation button
        run_simulation = st.button(
            "🚀 Run Simulation", 
            type="primary",
            use_container_width=True,
            help=f"Analyze {ticker} investment performance"
        )
    
    with col2:
        # Reset button
        reset_app = st.button(
            "🔄 Reset",
            use_container_width=True,
            help="Clear all results and start fresh"
        )
    
    # Handle reset
    if reset_app:
        st.session_state.simulation_run = False
        st.session_state.last_ticker = None
        st.session_state.last_results = None
        st.session_state.portfolio = {}
        st.session_state.comparison_results = {}
        # Clear cache
        st.cache_data.clear()
        st.success("✅ App reset successfully!")
        st.rerun()

# Main content area
if run_simulation:
    st.session_state.simulation_run = True
    st.session_state.last_ticker = ticker
    
    st.subheader(f"📊 Analysis Results for {ticker}")
    
    # Fetch data - progress bar is handled within the function
    data, stock_info = fetch_stock_data(ticker, start_date)
    
    if data is None:
        st.error(f"❌ Could not fetch data for {ticker}. Please try:")
        st.info("• Check if the ticker symbol is correct")
        st.info("• Try a different ticker or theme")
        st.info("• Click 'Reset' to clear cache and try again")
        
        # Suggest alternative tickers
        st.subheader("💡 Try These Popular Tickers:")
        st.error("⚠️ **Common Issue**: Make sure you're using the correct ticker symbol!")
        st.markdown("""
        **🔍 Most Common Mistakes:**
        - Apple: Use **AAPL** (not APPL)
        - Google: Use **GOOGL** (not GOOG)
        - Amazon: Use **AMZN** (not AMZ or AMAZON)
        - Microsoft: Use **MSFT** (not MS)
        """)
        
        popular_tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "SPY", "QQQ"]
        cols = st.columns(len(popular_tickers))
        for i, alt_ticker in enumerate(popular_tickers):
            with cols[i]:
                if st.button(alt_ticker, key=f"alt_{alt_ticker}"):
                    st.session_state.temp_ticker = alt_ticker
                    st.rerun()
    else:
        # Store results in session state
        st.session_state.last_results = {
            'data': data,
            'stock_info': stock_info,
            'ticker': ticker,
            'investment_amount': investment_amount,
            'start_date': start_date
        }
        
        # Data quality check
        quality_report = validate_data_quality(data, ticker)
        create_data_quality_report(quality_report)
        
        # Calculate returns
        returns = calculate_returns(data, investment_amount)
        
        if returns is None:
            st.error("❌ Could not calculate returns. Data may be insufficient.")
        else:
            # Display key metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Total Return", 
                    f"{returns['percent_return']:.2f}%",
                    delta=f"${returns['total_return']:,.2f}"
                )
            
            with col2:
                st.metric(
                    "Final Value", 
                    f"${returns['final_value']:,.2f}",
                    delta=f"${returns['final_value'] - returns['initial_investment']:,.2f}"
                )
            
            with col3:
                st.metric(
                    "Volatility", 
                    f"{returns['volatility']:.2f}%"
                )
            
            with col4:
                st.metric(
                    "Max Drawdown", 
                    f"{returns['max_drawdown']:.2f}%"
                )
            
            # Action buttons row
            st.subheader("🔧 Actions")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📁 Add to Portfolio", help="Track this investment for comparison"):
                    if add_to_portfolio(ticker, data, stock_info, investment_amount, start_date):
                        st.success(f"✅ {ticker} added to portfolio!")
                    else:
                        st.error("❌ Failed to add to portfolio")
            
            with col2:
                if st.button("📊 Compare vs S&P 500", help="Compare performance against market benchmark"):
                    with st.spinner("Fetching S&P 500 benchmark data..."):
                        benchmark_data = get_market_benchmark_data(start_date)
                        if benchmark_data is not None:
                            comparison = calculate_benchmark_comparison(returns, benchmark_data, investment_amount)
                            st.session_state.comparison_results = comparison
                            st.success("✅ Benchmark comparison completed!")
                        else:
                            st.error("❌ Could not fetch benchmark data")
            
            with col3:
                if st.button("💾 Export Results", help="Download analysis as JSON"):
                    json_data = export_results_to_json(ticker, returns, stock_info, start_date, investment_amount)
                    st.download_button(
                        label="📥 Download JSON",
                        data=json_data,
                        file_name=f"{ticker}_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
            
            # Show benchmark comparison if available
            if st.session_state.comparison_results:
                st.subheader("📊 Benchmark Comparison")
                comp = st.session_state.comparison_results
                
                bench_col1, bench_col2, bench_col3 = st.columns(3)
                
                with bench_col1:
                    st.metric("S&P 500 Return", f"{comp.get('benchmark_return', 0):.2f}%")
                
                with bench_col2:
                    alpha = comp.get('alpha', 0)
                    st.metric("Alpha (Outperformance)", f"{alpha:+.2f}%", 
                             delta="Outperformed" if alpha > 0 else "Underperformed")
                
                with bench_col3:
                    rel_vol = comp.get('relative_volatility', 0)
                    st.metric("Relative Volatility", f"{rel_vol:+.2f}%")
            
            # Price chart
            st.subheader("📈 Price & Investment Performance")
            price_chart = create_price_chart(data, ticker, investment_amount)
            if price_chart:
                st.plotly_chart(price_chart, use_container_width=True, key="main_price_chart")
            
            # Advanced Analytics Section
            st.subheader("🔬 Advanced Analytics")
            
            # Calculate technical indicators
            technical_indicators = calculate_technical_indicators(data)
            
            # Create tabs for different analytics
            tab1, tab2, tab3, tab4 = st.tabs(["📊 Technical Indicators", "💡 AI Insights", "📰 Recent News", "📈 Detailed Metrics"])
            
            with tab1:
                format_technical_indicators(technical_indicators)
            
            with tab2:
                st.write("**🤖 AI-Generated Investment Insights**")
                insights = generate_investment_insights(returns, technical_indicators, stock_info)
                for insight in insights:
                    st.write(f"• {insight}")
            
            with tab3:
                if st.button("📰 Fetch Latest News", help="Get recent news for this stock", key="fetch_news"):
                    with st.spinner("Fetching news..."):
                        news_articles = get_stock_news(ticker, limit=5)
                        
                        if news_articles:
                            for i, article in enumerate(news_articles):
                                with st.expander(f"📰 {article['title'][:100]}..."):
                                    st.write(f"**Publisher:** {article['publisher']}")
                                    if article['published']:
                                        pub_date = datetime.fromtimestamp(article['published'])
                                        st.write(f"**Published:** {pub_date.strftime('%Y-%m-%d %H:%M')}")
                                    st.write(article['summary'])
                                    if article['link']:
                                        st.markdown(f"[Read more]({article['link']})")
                        else:
                            st.info("No recent news found for this ticker.")
                else:
                    st.info("Click the button above to fetch the latest news for this stock.")
            
            with tab4:
                st.write("**Detailed Performance Metrics**")
                
                # Create detailed metrics table
                detailed_metrics = {
                    'Investment Metrics': {
                        'Initial Price': f"${returns['initial_price']:.2f}",
                        'Final Price': f"${returns['final_price']:.2f}",
                        'Shares Purchased': f"{returns['shares']:.4f}",
                        'Total Return (Absolute)': f"${returns['total_return']:.2f}",
                        'Total Return (%)': f"{returns['percent_return']:.2f}%",
                        'Annualized Return': f"{((returns['final_value'] / returns['initial_investment']) ** (365 / returns['days_invested']) - 1) * 100:.2f}%"
                    },
                    'Risk Metrics': {
                        'Volatility (Annual)': f"{returns['volatility']:.2f}%",
                        'Max Drawdown': f"{returns['max_drawdown']:.2f}%",
                        'Sharpe Ratio': f"{(returns['percent_return'] / returns['volatility']):.2f}" if returns['volatility'] > 0 else "N/A",
                        'Days Invested': f"{returns['days_invested']} days",
                        'Risk-Adjusted Return': f"{returns['percent_return'] / (returns['volatility'] / 100):.2f}" if returns['volatility'] > 0 else "N/A"
                    }
                }
                
                for category, metrics in detailed_metrics.items():
                    st.write(f"**{category}**")
                    metrics_df = pd.DataFrame(list(metrics.items()), columns=['Metric', 'Value'])
                    st.dataframe(metrics_df, hide_index=True)
                    st.write("")
            
            # Company information
            col1, col2 = st.columns(2)
            
            with col2:
                st.subheader("ℹ️ Company Information")
                display_company_info(stock_info)
            
            # Prediction section
            if show_prediction and ML_AVAILABLE:
                st.subheader("🔮 Price Prediction")
                
                with st.spinner("Generating predictions..."):
                    prediction_result = simple_prediction_model(data, days_ahead=prediction_days)
                
                if prediction_result:
                    # Get the price column for consistency
                    price_col = get_price_column(data)
                    
                    # Create prediction chart
                    fig_pred = go.Figure()
                    
                    # Historical prices
                    fig_pred.add_trace(go.Scatter(
                        x=data.index[-60:],  # Last 60 days
                        y=data[price_col].iloc[-60:],
                        mode='lines',
                        name='Historical Price',
                        line=dict(color='blue')
                    ))
                    
                    # Predictions
                    fig_pred.add_trace(go.Scatter(
                        x=prediction_result['dates'],
                        y=prediction_result['predictions'],
                        mode='lines',
                        name=f'Predicted Price ({prediction_result["model_name"]})',
                        line=dict(color='red', dash='dash')
                    ))
                    
                    fig_pred.update_layout(
                        title=f'{ticker} Price Prediction - {prediction_result["model_name"]} Model',
                        xaxis_title='Date',
                        yaxis_title='Price ($)',
                        hovermode='x unified',
                        height=400
                    )
                    
                    st.plotly_chart(fig_pred, use_container_width=True, key="prediction_chart")
                    
                    # Show prediction metrics
                    pred_col1, pred_col2 = st.columns(2)
                    with pred_col1:
                        st.metric("Model Accuracy", f"{prediction_result['accuracy']*100:.1f}%")
                    with pred_col2:
                        avg_predicted_price = np.mean(prediction_result['predictions'])
                        current_price = data[price_col].iloc[-1]
                        predicted_change = ((avg_predicted_price - current_price) / current_price) * 100
                        st.metric("Predicted Change", f"{predicted_change:+.1f}%")
                    
                    # Warning about predictions
                    st.warning("⚠️ Predictions are for educational purposes only and should not be used for actual investment decisions. Past performance does not guarantee future results.")
                
                else:
                    st.error("Could not generate predictions. Insufficient data or model error.")
            
            elif show_prediction and not ML_AVAILABLE:
                st.error("Machine learning libraries not available. Please install scikit-learn to enable predictions.")

# Portfolio comparison section
elif st.session_state.portfolio:
    st.subheader("📊 Portfolio Performance Comparison")
    
    # Create tabs for different views
    tab1, tab2 = st.tabs(["📈 Performance Chart", "📋 Detailed Table"])
    
    with tab1:
        # Portfolio comparison chart
        comparison_chart = create_portfolio_comparison_chart()
        if comparison_chart:
            st.plotly_chart(comparison_chart, use_container_width=True, key="portfolio_comparison_chart")
        
        # Portfolio summary metrics
        col1, col2, col3 = st.columns(3)
        
        total_invested = sum(entry['investment_amount'] for entry in st.session_state.portfolio.values())
        total_value = sum(entry['returns']['final_value'] for entry in st.session_state.portfolio.values())
        total_return = ((total_value - total_invested) / total_invested) * 100
        
        with col1:
            st.metric("Total Portfolio Value", f"${total_value:,.0f}")
        
        with col2:
            st.metric("Total Invested", f"${total_invested:,.0f}")
        
        with col3:
            st.metric("Portfolio Return", f"{total_return:.1f}%")
    
    with tab2:
        # Detailed comparison table
        comparison_df = compare_portfolio_performance()
        if comparison_df is not None:
            st.dataframe(comparison_df, use_container_width=True)
            
            # Download portfolio data
            csv = comparison_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Portfolio Data",
                data=csv,
                file_name=f"portfolio_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

else:
    # Welcome screen
    st.markdown("""
    ## Welcome to SimVestor! 🚀
    
    ### Features:
    - **📊 Historical Analysis**: Simulate past investments with real market data
    - **🎯 Thematic Investing**: Choose from 80+ investment themes across 10 categories
    - **🔮 AI Predictions**: ML-powered price forecasting with accuracy metrics
    - **📈 Risk Analysis**: Comprehensive risk metrics and visualizations
    - **💡 Smart Insights**: Automated investment analysis and company information
    - **🌍 Global Coverage**: US stocks, ETFs, and international markets
    - **📁 Portfolio Tracking**: Add investments to track and compare performance
    - **📊 Benchmark Comparison**: Compare your investments against S&P 500
    - **💾 Export Results**: Download detailed analysis as JSON or CSV
    
    ### How to Use:
    1. **Select Theme**: Browse by category or search all themes
    2. **Set Parameters**: Choose investment date and amount
    3. **Run Simulation**: Click "Run Simulation" to see results
    4. **Analyze Results**: Review returns, risks, and AI predictions
    5. **Track Portfolio**: Add investments to compare performance
    
    **Ready to start?** Configure your simulation in the sidebar and click 'Run Simulation'!
    """)

# Footer
st.markdown("---")
st.markdown("📈 **SimVestor** - AI-Powered Investment Simulation | Built with Streamlit")

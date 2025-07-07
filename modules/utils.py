"""
Utility functions for SimVestor
Handles themes, export, and miscellaneous helper functions
"""

import json
from datetime import datetime
from typing import Dict


def get_theme_dictionary():
    """Get mapping of investment themes to ticker symbols"""
    return {
        # Technology & Innovation
        "artificial intelligence": "NVDA",
        "ai": "NVDA", 
        "technology": "AAPL",
        "cloud computing": "MSFT",
        "cybersecurity": "CRWD",
        "fintech": "SQ",
        "semiconductor": "NVDA", 
        "software": "MSFT",
        "internet": "GOOGL",
        "data analytics": "PLTR",
        "quantum computing": "IBM",
        
        # Energy & Environment
        "clean energy": "ICLN",
        "renewable energy": "NEE",
        "solar": "ENPH",
        "electric vehicles": "TSLA",
        "ev": "TSLA",
        "oil": "XOM",
        "energy": "XLE",
        "utilities": "XLU",
        "wind energy": "NEE",
        
        # Healthcare & Biotech
        "healthcare": "JNJ",
        "biotech": "GILD",
        "pharmaceuticals": "PFE",
        "medical": "ABT",
        "genomics": "ARKG",
        "telemedicine": "TDOC",
        
        # Consumer & Lifestyle
        "gaming": "ATVI",
        "streaming": "NFLX",
        "social media": "META",
        "ecommerce": "AMZN", 
        "retail": "WMT",
        "travel": "ABNB",
        "food": "KO",
        "consumer discretionary": "XLY",
        "consumer staples": "XLP",
        "luxury goods": "LVMUY",
        "fitness": "NKE",
        
        # Financial Services
        "banking": "JPM",
        "financial": "XLF",
        "insurance": "BRK-B",
        "real estate": "VNQ",
        "cryptocurrency": "COIN",
        "blockchain": "MSTR",
        "payments": "V",
        
        # Industrial & Materials
        "aerospace": "BA",
        "defense": "LMT",
        "infrastructure": "PAVE",
        "transportation": "XTN",
        "construction": "CAT",
        "industrials": "XLI",
        "robotics": "BOTZ",
        "automation": "ROK",
        "gold": "GLD",
        "silver": "SLV",
        "copper": "CPER",
        "lithium": "LIT",
        "materials": "XLB",
        
        # Communications & Media
        "communication": "XLC",
        "media": "DIS",
        "telecom": "VZ",
        "advertising": "GOOGL",
        "content creation": "NFLX",
        
        # Market Indices
        "sp500": "SPY",
        "nasdaq": "QQQ",
        "dow": "DIA",
        "market": "SPY",
        "index": "SPY",
        "small cap": "IWM",
        "mid cap": "MDY",
        
        # Global Markets
        "emerging": "EEM",
        "international": "VXUS",
        "europe": "VGK",
        "asia": "VEA",
        "china": "FXI",
        "japan": "EWJ",
        "india": "INDA",
        
        # Popular Individual Stocks
        "apple": "AAPL",
        "microsoft": "MSFT",
        "amazon": "AMZN",
        "google": "GOOGL",
        "tesla": "TSLA",
        "nvidia": "NVDA",
        "meta": "META",
        "netflix": "NFLX",
        "berkshire": "BRK-B",
        "jpmorgan": "JPM"
    }


def export_results_to_json(ticker: str, returns: dict, stock_info: dict, 
                          start_date: datetime, investment_amount: float) -> str:
    """Export results to JSON format"""
    try:
        results = {
            'ticker': ticker,
            'analysis_date': datetime.now().isoformat(),
            'investment_start_date': start_date.isoformat(),
            'investment_amount': investment_amount,
            'returns': returns,
            'stock_info': stock_info
        }
        
        return json.dumps(results, indent=2, default=str)
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error exporting results: {str(e)}")
        return "{}"


def format_currency(amount: float) -> str:
    """Format currency with proper commas and symbol"""
    return f"${amount:,.2f}"


def format_percentage(value: float) -> str:
    """Format percentage with proper sign and decimal places"""
    return f"{value:+.2f}%"


def calculate_annualized_return(total_return_pct: float, days: int) -> float:
    """Calculate annualized return from total return and days"""
    if days <= 0:
        return 0
    return ((1 + total_return_pct / 100) ** (365 / days) - 1) * 100

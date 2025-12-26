# Silver Price Movement Analysis

This project retrieves daily silver price data and ranks the biggest movements (positive and negative) over the last 10 years.

## Overview

The analysis script fetches historical silver price data (using SLV - iShares Silver Trust ETF as a proxy) and identifies:
- Top 50 biggest single-day gains
- Top 50 biggest single-day losses
- Summary statistics including max gain/loss, average daily change, and volatility

## Files Generated

After running the analysis, the following files are created:

- **silver_analysis_report.txt** - Human-readable report with formatted tables
- **silver_price_analysis.json** - Structured JSON data for programmatic access
- **silver_price_data_full.csv** - Complete dataset with all daily prices and movements
- **silver_top_gains.csv** - Top 50 biggest gains
- **silver_top_losses.csv** - Top 50 biggest losses

## Usage

### Quick Start (Sample Data)

To run the analysis with sample data for demonstration:

```bash
python3 analyze_silver_prices_v3.py
```

⚠️ **Note**: This generates realistic sample data, NOT actual silver prices.

### Getting Real Data

To analyze actual silver price data:

1. **Get a free Alpha Vantage API key**:
   - Visit: https://www.alphavantage.co/support/#api-key
   - Sign up (free, no credit card required)
   - Copy your API key

2. **Run with your API key**:
   ```bash
   python3 analyze_silver_prices_v3.py YOUR_API_KEY
   ```

### API Limits

Alpha Vantage free tier:
- 25 API requests per day
- 500 API requests per month
- Full historical data (10+ years)

## Sample Output

```
==========================================================================================
SUMMARY STATISTICS
==========================================================================================
Maximum Single-Day Gain: +5.63% on 2016-09-08
Maximum Single-Day Loss: -4.94% on 2019-01-18
Average Daily Change: +0.0033%
Volatility (Std Dev): 1.48%

==========================================================================================
TOP 10 BIGGEST GAINS
==========================================================================================
 1. 2016-09-08 - +5.63% (Close: $11.45, Change: $+0.61)
 2. 2022-10-13 - +4.64% (Close: $22.54, Change: $+1.00)
 3. 2022-11-25 - +4.45% (Close: $22.04, Change: $+0.94)
 ...
```

## Requirements

- Python 3.x
- No external libraries required (uses only Python standard library)

## Data Source

- **Primary**: Alpha Vantage API (https://www.alphavantage.co/)
- **Symbol**: SLV (iShares Silver Trust ETF)
- **Period**: Last 10 years of daily trading data

## Analysis Details

The script calculates:

1. **Daily Change ($)**: Absolute dollar change from previous day's close
2. **Daily Change (%)**: Percentage change from previous day's close
3. **Volatility**: Standard deviation of daily percentage changes
4. **Rankings**: Sorted by percentage change (not absolute dollar change)

## Alternative Scripts

The repository includes multiple versions:

- **analyze_silver_prices.py** - Original version using yfinance (requires dependencies)
- **analyze_silver_prices_v2.py** - Direct Yahoo Finance CSV download
- **analyze_silver_prices_v3.py** - Alpha Vantage API with sample data fallback (recommended)

## Notes

- **Trading Days Only**: Analysis includes only trading days (excludes weekends and holidays)
- **Adjusted Close**: Uses closing prices (not adjusted for splits/dividends)
- **ETF Proxy**: SLV ETF closely tracks silver spot prices with high liquidity
- **Historical Accuracy**: Real data from Alpha Vantage is actual historical prices

## Example Use Cases

- Identify periods of high volatility in silver markets
- Research market reactions to economic events
- Analyze silver price behavior over different time periods
- Backtest trading strategies
- Study correlations with other assets

## Troubleshooting

### "No time series data found"
- You're using the demo API key with limited access
- Get a free API key from Alpha Vantage

### "API Limit" message
- Free tier has 25 requests/day limit
- Wait 24 hours or upgrade to paid tier

### "HTTP Error 401: Unauthorized"
- This occurs with direct Yahoo Finance access
- Use the Alpha Vantage version (v3) instead

## License

This is a data analysis tool for educational and research purposes.

## Contributing

To add features or improvements:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## Future Enhancements

Potential improvements:
- Support for multiple commodities (gold, platinum, copper)
- Interactive charts and visualizations
- Correlation analysis with other assets
- Moving averages and technical indicators
- Export to additional formats (Excel, PDF)
- Web dashboard interface

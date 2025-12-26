#!/usr/bin/env python3
"""
Silver Price Analysis Script
Retrieves daily silver price data and ranks biggest movements (positive and negative)
over the last 10 years.
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import json

def fetch_silver_data(years=10):
    """
    Fetch silver price data for the specified number of years.
    Using SLV (iShares Silver Trust ETF) as a proxy for silver prices.
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=years*365)

    print(f"Fetching silver price data from {start_date.date()} to {end_date.date()}...")

    # SLV is the iShares Silver Trust ETF, widely used as silver price proxy
    slv = yf.Ticker("SLV")
    df = slv.history(start=start_date, end=end_date)

    if df.empty:
        print("No data retrieved. Trying silver futures (SI=F)...")
        silver = yf.Ticker("SI=F")
        df = silver.history(start=start_date, end=end_date)

    return df

def calculate_movements(df):
    """
    Calculate daily price movements (absolute and percentage).
    """
    df['Daily_Change'] = df['Close'].diff()
    df['Daily_Change_Pct'] = df['Close'].pct_change() * 100

    # Remove first row with NaN
    df = df.dropna(subset=['Daily_Change', 'Daily_Change_Pct'])

    return df

def rank_movements(df, top_n=50):
    """
    Rank the biggest movements (positive and negative).
    """
    # Sort by percentage change
    df_sorted = df.sort_values('Daily_Change_Pct', ascending=False)

    top_gains = df_sorted.head(top_n)
    top_losses = df_sorted.tail(top_n).iloc[::-1]  # Reverse to show worst first

    return top_gains, top_losses

def format_results(df, title):
    """
    Format results for display.
    """
    results = []
    for idx, row in df.iterrows():
        results.append({
            'Date': idx.strftime('%Y-%m-%d'),
            'Close_Price': f"${row['Close']:.2f}",
            'Daily_Change': f"${row['Daily_Change']:.2f}",
            'Daily_Change_Pct': f"{row['Daily_Change_Pct']:.2f}%",
            'Volume': f"{int(row['Volume']):,}"
        })
    return results

def save_results(top_gains, top_losses, df):
    """
    Save results to files.
    """
    # Save to JSON
    results = {
        'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'data_period': {
            'start': df.index.min().strftime('%Y-%m-%d'),
            'end': df.index.max().strftime('%Y-%m-%d'),
            'total_days': len(df)
        },
        'top_gains': format_results(top_gains, 'Top Gains'),
        'top_losses': format_results(top_losses, 'Top Losses'),
        'statistics': {
            'max_gain_pct': f"{df['Daily_Change_Pct'].max():.2f}%",
            'max_loss_pct': f"{df['Daily_Change_Pct'].min():.2f}%",
            'avg_daily_change_pct': f"{df['Daily_Change_Pct'].mean():.2f}%",
            'volatility_std': f"{df['Daily_Change_Pct'].std():.2f}%"
        }
    }

    with open('silver_price_analysis.json', 'w') as f:
        json.dump(results, f, indent=2)

    # Save to CSV
    df.to_csv('silver_price_data_full.csv')
    top_gains.to_csv('silver_top_gains.csv')
    top_losses.to_csv('silver_top_losses.csv')

    # Create readable report
    with open('silver_analysis_report.txt', 'w') as f:
        f.write("=" * 80 + "\n")
        f.write("SILVER PRICE MOVEMENT ANALYSIS\n")
        f.write("=" * 80 + "\n\n")

        f.write(f"Analysis Date: {results['analysis_date']}\n")
        f.write(f"Data Period: {results['data_period']['start']} to {results['data_period']['end']}\n")
        f.write(f"Total Trading Days: {results['data_period']['total_days']}\n\n")

        f.write("STATISTICS\n")
        f.write("-" * 80 + "\n")
        f.write(f"Maximum Single-Day Gain: {results['statistics']['max_gain_pct']}\n")
        f.write(f"Maximum Single-Day Loss: {results['statistics']['max_loss_pct']}\n")
        f.write(f"Average Daily Change: {results['statistics']['avg_daily_change_pct']}\n")
        f.write(f"Volatility (Std Dev): {results['statistics']['volatility_std']}\n\n")

        f.write("=" * 80 + "\n")
        f.write("TOP 50 BIGGEST GAINS (by percentage)\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"{'Rank':<6}{'Date':<15}{'Close':<12}{'Change $':<15}{'Change %':<12}{'Volume':<15}\n")
        f.write("-" * 80 + "\n")

        for i, result in enumerate(results['top_gains'], 1):
            f.write(f"{i:<6}{result['Date']:<15}{result['Close_Price']:<12}"
                   f"{result['Daily_Change']:<15}{result['Daily_Change_Pct']:<12}"
                   f"{result['Volume']:<15}\n")

        f.write("\n" + "=" * 80 + "\n")
        f.write("TOP 50 BIGGEST LOSSES (by percentage)\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"{'Rank':<6}{'Date':<15}{'Close':<12}{'Change $':<15}{'Change %':<12}{'Volume':<15}\n")
        f.write("-" * 80 + "\n")

        for i, result in enumerate(results['top_losses'], 1):
            f.write(f"{i:<6}{result['Date']:<15}{result['Close_Price']:<12}"
                   f"{result['Daily_Change']:<15}{result['Daily_Change_Pct']:<12}"
                   f"{result['Volume']:<15}\n")

    print("\n✓ Results saved to:")
    print("  - silver_analysis_report.txt (human-readable report)")
    print("  - silver_price_analysis.json (structured data)")
    print("  - silver_price_data_full.csv (complete dataset)")
    print("  - silver_top_gains.csv (top gains)")
    print("  - silver_top_losses.csv (top losses)")

def main():
    print("Silver Price Movement Analysis")
    print("=" * 80)

    # Fetch data
    df = fetch_silver_data(years=10)

    if df.empty:
        print("Error: Could not retrieve silver price data.")
        return

    print(f"✓ Retrieved {len(df)} days of data")
    print(f"  Date range: {df.index.min().date()} to {df.index.max().date()}")

    # Calculate movements
    df = calculate_movements(df)
    print(f"✓ Calculated daily movements")

    # Rank movements
    top_gains, top_losses = rank_movements(df, top_n=50)
    print(f"✓ Ranked biggest movements")

    # Display summary
    print("\n" + "=" * 80)
    print("SUMMARY STATISTICS")
    print("=" * 80)
    print(f"Maximum Single-Day Gain: {df['Daily_Change_Pct'].max():.2f}%")
    print(f"  Date: {df['Daily_Change_Pct'].idxmax().date()}")
    print(f"Maximum Single-Day Loss: {df['Daily_Change_Pct'].min():.2f}%")
    print(f"  Date: {df['Daily_Change_Pct'].idxmin().date()}")
    print(f"Average Daily Change: {df['Daily_Change_Pct'].mean():.2f}%")
    print(f"Volatility (Std Dev): {df['Daily_Change_Pct'].std():.2f}%")

    print("\n" + "=" * 80)
    print("TOP 10 BIGGEST GAINS")
    print("=" * 80)
    for i, (idx, row) in enumerate(top_gains.head(10).iterrows(), 1):
        print(f"{i:2d}. {idx.date()} - {row['Daily_Change_Pct']:+.2f}% "
              f"(Close: ${row['Close']:.2f})")

    print("\n" + "=" * 80)
    print("TOP 10 BIGGEST LOSSES")
    print("=" * 80)
    for i, (idx, row) in enumerate(top_losses.head(10).iterrows(), 1):
        print(f"{i:2d}. {idx.date()} - {row['Daily_Change_Pct']:+.2f}% "
              f"(Close: ${row['Close']:.2f})")

    # Save results
    print("\n" + "=" * 80)
    save_results(top_gains, top_losses, df)
    print("\n✓ Analysis complete!")

if __name__ == "__main__":
    main()

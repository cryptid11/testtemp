#!/usr/bin/env python3
"""
Silver Price Analysis Script (Version 2 - Using direct CSV download)
Retrieves daily silver price data and ranks biggest movements (positive and negative)
over the last 10 years.
"""

import urllib.request
import csv
import json
from datetime import datetime, timedelta
from io import StringIO
from collections import defaultdict

def fetch_silver_data_csv(years=10):
    """
    Fetch silver price data by downloading CSV from Yahoo Finance.
    Using SLV (iShares Silver Trust ETF) as a proxy for silver prices.
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=years*365)

    # Convert to Unix timestamps
    start_ts = int(start_date.timestamp())
    end_ts = int(end_date.timestamp())

    # Yahoo Finance historical data URL
    symbol = "SLV"
    url = f"https://query1.finance.yahoo.com/v7/finance/download/{symbol}?period1={start_ts}&period2={end_ts}&interval=1d&events=history"

    print(f"Fetching silver price data from {start_date.date()} to {end_date.date()}...")
    print(f"URL: {url}")

    try:
        # Add headers to mimic browser request
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

        with urllib.request.urlopen(req) as response:
            data = response.read().decode('utf-8')

        # Parse CSV
        csv_reader = csv.DictReader(StringIO(data))
        rows = list(csv_reader)

        print(f"✓ Retrieved {len(rows)} days of data")
        return rows

    except Exception as e:
        print(f"Error fetching data: {e}")
        return []

def process_data(rows):
    """
    Process raw CSV data and calculate movements.
    """
    data = []

    for i, row in enumerate(rows):
        try:
            date = row['Date']
            close = float(row['Close'])
            adj_close = float(row['Adj Close']) if row.get('Adj Close') else close
            volume = int(float(row['Volume'])) if row.get('Volume') and row['Volume'] != 'null' else 0

            daily_change = None
            daily_change_pct = None

            if i > 0:
                prev_close = data[-1]['close']
                daily_change = close - prev_close
                daily_change_pct = (daily_change / prev_close) * 100

            data.append({
                'date': date,
                'close': close,
                'adj_close': adj_close,
                'volume': volume,
                'daily_change': daily_change,
                'daily_change_pct': daily_change_pct
            })
        except (ValueError, KeyError) as e:
            print(f"Warning: Skipping row {i} due to error: {e}")
            continue

    # Remove first entry (no change data)
    if data:
        data = data[1:]

    return data

def rank_movements(data, top_n=50):
    """
    Rank the biggest movements (positive and negative).
    """
    # Sort by percentage change
    sorted_data = sorted(data, key=lambda x: x['daily_change_pct'] if x['daily_change_pct'] is not None else 0, reverse=True)

    top_gains = sorted_data[:top_n]
    top_losses = sorted_data[-top_n:][::-1]  # Reverse to show worst first

    return top_gains, top_losses

def calculate_statistics(data):
    """
    Calculate summary statistics.
    """
    changes = [d['daily_change_pct'] for d in data if d['daily_change_pct'] is not None]

    if not changes:
        return {}

    max_gain = max(changes)
    max_loss = min(changes)
    avg_change = sum(changes) / len(changes)

    # Calculate standard deviation
    variance = sum((x - avg_change) ** 2 for x in changes) / len(changes)
    std_dev = variance ** 0.5

    # Find dates for max/min
    max_gain_date = next(d['date'] for d in data if d['daily_change_pct'] == max_gain)
    max_loss_date = next(d['date'] for d in data if d['daily_change_pct'] == max_loss)

    return {
        'max_gain_pct': max_gain,
        'max_gain_date': max_gain_date,
        'max_loss_pct': max_loss,
        'max_loss_date': max_loss_date,
        'avg_daily_change_pct': avg_change,
        'volatility_std': std_dev,
        'total_days': len(changes)
    }

def save_results(top_gains, top_losses, data, stats):
    """
    Save results to files.
    """
    # Prepare results
    results = {
        'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'data_period': {
            'start': data[0]['date'] if data else 'N/A',
            'end': data[-1]['date'] if data else 'N/A',
            'total_days': stats.get('total_days', 0)
        },
        'top_gains': [
            {
                'Date': d['date'],
                'Close_Price': f"${d['close']:.2f}",
                'Daily_Change': f"${d['daily_change']:.2f}" if d['daily_change'] is not None else 'N/A',
                'Daily_Change_Pct': f"{d['daily_change_pct']:.2f}%" if d['daily_change_pct'] is not None else 'N/A',
                'Volume': f"{d['volume']:,}"
            } for d in top_gains
        ],
        'top_losses': [
            {
                'Date': d['date'],
                'Close_Price': f"${d['close']:.2f}",
                'Daily_Change': f"${d['daily_change']:.2f}" if d['daily_change'] is not None else 'N/A',
                'Daily_Change_Pct': f"{d['daily_change_pct']:.2f}%" if d['daily_change_pct'] is not None else 'N/A',
                'Volume': f"{d['volume']:,}"
            } for d in top_losses
        ],
        'statistics': {
            'max_gain_pct': f"{stats.get('max_gain_pct', 0):.2f}%",
            'max_gain_date': stats.get('max_gain_date', 'N/A'),
            'max_loss_pct': f"{stats.get('max_loss_pct', 0):.2f}%",
            'max_loss_date': stats.get('max_loss_date', 'N/A'),
            'avg_daily_change_pct': f"{stats.get('avg_daily_change_pct', 0):.2f}%",
            'volatility_std': f"{stats.get('volatility_std', 0):.2f}%"
        }
    }

    # Save to JSON
    with open('silver_price_analysis.json', 'w') as f:
        json.dump(results, f, indent=2)

    # Save full data to CSV
    with open('silver_price_data_full.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['date', 'close', 'adj_close', 'volume', 'daily_change', 'daily_change_pct'])
        writer.writeheader()
        writer.writerows(data)

    # Save top gains to CSV
    with open('silver_top_gains.csv', 'w', newline='') as f:
        if top_gains:
            writer = csv.DictWriter(f, fieldnames=top_gains[0].keys())
            writer.writeheader()
            writer.writerows(top_gains)

    # Save top losses to CSV
    with open('silver_top_losses.csv', 'w', newline='') as f:
        if top_losses:
            writer = csv.DictWriter(f, fieldnames=top_losses[0].keys())
            writer.writeheader()
            writer.writerows(top_losses)

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
        f.write(f"Maximum Single-Day Gain: {results['statistics']['max_gain_pct']} on {results['statistics']['max_gain_date']}\n")
        f.write(f"Maximum Single-Day Loss: {results['statistics']['max_loss_pct']} on {results['statistics']['max_loss_date']}\n")
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

    print("\nResults saved to:")
    print("  - silver_analysis_report.txt (human-readable report)")
    print("  - silver_price_analysis.json (structured data)")
    print("  - silver_price_data_full.csv (complete dataset)")
    print("  - silver_top_gains.csv (top gains)")
    print("  - silver_top_losses.csv (top losses)")

def main():
    print("=" * 80)
    print("SILVER PRICE MOVEMENT ANALYSIS")
    print("=" * 80)
    print()

    # Fetch data
    rows = fetch_silver_data_csv(years=10)

    if not rows:
        print("Error: Could not retrieve silver price data.")
        return

    # Process data
    data = process_data(rows)
    print(f"✓ Processed {len(data)} days of data with price movements")

    if not data:
        print("Error: No valid data to analyze.")
        return

    print(f"  Date range: {data[0]['date']} to {data[-1]['date']}")

    # Calculate statistics
    stats = calculate_statistics(data)
    print(f"✓ Calculated statistics")

    # Rank movements
    top_gains, top_losses = rank_movements(data, top_n=50)
    print(f"✓ Ranked biggest movements")

    # Display summary
    print("\n" + "=" * 80)
    print("SUMMARY STATISTICS")
    print("=" * 80)
    print(f"Maximum Single-Day Gain: {stats['max_gain_pct']:.2f}% on {stats['max_gain_date']}")
    print(f"Maximum Single-Day Loss: {stats['max_loss_pct']:.2f}% on {stats['max_loss_date']}")
    print(f"Average Daily Change: {stats['avg_daily_change_pct']:.2f}%")
    print(f"Volatility (Std Dev): {stats['volatility_std']:.2f}%")

    print("\n" + "=" * 80)
    print("TOP 10 BIGGEST GAINS")
    print("=" * 80)
    for i, d in enumerate(top_gains[:10], 1):
        pct = d['daily_change_pct'] if d['daily_change_pct'] is not None else 0
        print(f"{i:2d}. {d['date']} - {pct:+.2f}% (Close: ${d['close']:.2f})")

    print("\n" + "=" * 80)
    print("TOP 10 BIGGEST LOSSES")
    print("=" * 80)
    for i, d in enumerate(top_losses[:10], 1):
        pct = d['daily_change_pct'] if d['daily_change_pct'] is not None else 0
        print(f"{i:2d}. {d['date']} - {pct:+.2f}% (Close: ${d['close']:.2f})")

    # Save results
    print("\n" + "=" * 80)
    save_results(top_gains, top_losses, data, stats)
    print("\nAnalysis complete!")

if __name__ == "__main__":
    main()

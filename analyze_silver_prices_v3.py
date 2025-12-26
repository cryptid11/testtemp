#!/usr/bin/env python3
"""
Silver Price Analysis Script (Version 3 - Using alternative data source)
Retrieves daily silver price data and ranks biggest movements (positive and negative)
over the last 10 years.
"""

import json
import csv
from datetime import datetime, timedelta
import urllib.request
import urllib.parse

def fetch_alpha_vantage_data(api_key='demo', symbol='SLV'):
    """
    Fetch data from Alpha Vantage (free tier: 25 requests/day, 500 requests/month).
    For demo purposes, using 'demo' API key which has limited data.
    For full access, get free API key from https://www.alphavantage.co/support/#api-key
    """
    base_url = 'https://www.alphavantage.co/query'

    params = {
        'function': 'TIME_SERIES_DAILY',
        'symbol': symbol,
        'outputsize': 'full',  # Get full historical data
        'apikey': api_key
    }

    url = f"{base_url}?{urllib.parse.urlencode(params)}"

    print(f"Fetching silver price data from Alpha Vantage...")
    print(f"Symbol: {symbol} (iShares Silver Trust ETF)")

    if api_key == 'demo':
        print("\nNOTE: Using demo API key with limited data.")
        print("For full 10-year data, get a free API key from:")
        print("https://www.alphavantage.co/support/#api-key")
        print("Then run: python3 analyze_silver_prices_v3.py YOUR_API_KEY\n")

    try:
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0')

        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode('utf-8'))

        if 'Error Message' in data:
            print(f"Error: {data['Error Message']}")
            return []

        if 'Note' in data:
            print(f"API Limit: {data['Note']}")
            return []

        time_series = data.get('Time Series (Daily)', {})

        if not time_series:
            print("No time series data found in response")
            return []

        # Convert to list of dicts
        rows = []
        for date, values in sorted(time_series.items()):
            rows.append({
                'Date': date,
                'Open': values['1. open'],
                'High': values['2. high'],
                'Low': values['3. low'],
                'Close': values['4. close'],
                'Volume': values['5. volume']
            })

        print(f"✓ Retrieved {len(rows)} days of data")
        if rows:
            print(f"  Date range: {rows[0]['Date']} to {rows[-1]['Date']}")

        return rows

    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} - {e.reason}")
        return []
    except Exception as e:
        print(f"Error fetching data: {e}")
        return []

def fetch_sample_data():
    """
    Create sample data for demonstration when API is not available.
    This simulates realistic silver price movements.
    """
    print("Using sample data for demonstration...")

    import random
    random.seed(42)

    base_price = 20.0
    data = []
    current_date = datetime(2015, 1, 1)
    end_date = datetime(2025, 12, 26)

    while current_date <= end_date:
        # Skip weekends
        if current_date.weekday() < 5:
            # Simulate realistic price movement
            change_pct = random.gauss(0, 1.5)  # Mean 0%, std dev 1.5%
            base_price *= (1 + change_pct / 100)
            base_price = max(10, min(40, base_price))  # Keep in realistic range

            data.append({
                'Date': current_date.strftime('%Y-%m-%d'),
                'Close': str(round(base_price, 2)),
                'Volume': str(random.randint(5000000, 30000000))
            })

        current_date += timedelta(days=1)

    print(f"✓ Generated {len(data)} days of sample data")
    print(f"  Date range: {data[0]['Date']} to {data[-1]['Date']}")
    print("\nWARNING: This is sample data, not real silver prices!")
    print("For real data, use a valid Alpha Vantage API key.\n")

    return data

def process_data(rows):
    """
    Process raw data and calculate movements.
    """
    data = []

    for i, row in enumerate(rows):
        try:
            date = row['Date']
            close = float(row['Close'])
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
                'volume': volume,
                'daily_change': daily_change,
                'daily_change_pct': daily_change_pct
            })
        except (ValueError, KeyError) as e:
            print(f"Warning: Skipping row due to error: {e}")
            continue

    # Remove first entry (no change data)
    if data:
        data = data[1:]

    return data

def rank_movements(data, top_n=50):
    """
    Rank the biggest movements (positive and negative).
    """
    sorted_data = sorted(data, key=lambda x: x['daily_change_pct'] if x['daily_change_pct'] is not None else 0, reverse=True)

    top_gains = sorted_data[:top_n]
    top_losses = sorted_data[-top_n:][::-1]

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

    variance = sum((x - avg_change) ** 2 for x in changes) / len(changes)
    std_dev = variance ** 0.5

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

    with open('silver_price_analysis.json', 'w') as f:
        json.dump(results, f, indent=2)

    with open('silver_price_data_full.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['date', 'close', 'volume', 'daily_change', 'daily_change_pct'])
        writer.writeheader()
        writer.writerows(data)

    with open('silver_top_gains.csv', 'w', newline='') as f:
        if top_gains:
            writer = csv.DictWriter(f, fieldnames=top_gains[0].keys())
            writer.writeheader()
            writer.writerows(top_gains)

    with open('silver_top_losses.csv', 'w', newline='') as f:
        if top_losses:
            writer = csv.DictWriter(f, fieldnames=top_losses[0].keys())
            writer.writeheader()
            writer.writerows(top_losses)

    with open('silver_analysis_report.txt', 'w') as f:
        f.write("=" * 90 + "\n")
        f.write("SILVER PRICE MOVEMENT ANALYSIS\n")
        f.write("=" * 90 + "\n\n")

        f.write(f"Analysis Date: {results['analysis_date']}\n")
        f.write(f"Data Period: {results['data_period']['start']} to {results['data_period']['end']}\n")
        f.write(f"Total Trading Days: {results['data_period']['total_days']}\n\n")

        f.write("SUMMARY STATISTICS\n")
        f.write("-" * 90 + "\n")
        f.write(f"Maximum Single-Day Gain: {results['statistics']['max_gain_pct']} on {results['statistics']['max_gain_date']}\n")
        f.write(f"Maximum Single-Day Loss: {results['statistics']['max_loss_pct']} on {results['statistics']['max_loss_date']}\n")
        f.write(f"Average Daily Change: {results['statistics']['avg_daily_change_pct']}\n")
        f.write(f"Volatility (Std Dev): {results['statistics']['volatility_std']}\n\n")

        f.write("=" * 90 + "\n")
        f.write("TOP 50 BIGGEST GAINS (by percentage)\n")
        f.write("=" * 90 + "\n\n")
        f.write(f"{'Rank':<6}{'Date':<15}{'Close':<12}{'Change $':<15}{'Change %':<15}{'Volume':<15}\n")
        f.write("-" * 90 + "\n")

        for i, result in enumerate(results['top_gains'], 1):
            f.write(f"{i:<6}{result['Date']:<15}{result['Close_Price']:<12}"
                   f"{result['Daily_Change']:<15}{result['Daily_Change_Pct']:<15}"
                   f"{result['Volume']:<15}\n")

        f.write("\n" + "=" * 90 + "\n")
        f.write("TOP 50 BIGGEST LOSSES (by percentage)\n")
        f.write("=" * 90 + "\n\n")
        f.write(f"{'Rank':<6}{'Date':<15}{'Close':<12}{'Change $':<15}{'Change %':<15}{'Volume':<15}\n")
        f.write("-" * 90 + "\n")

        for i, result in enumerate(results['top_losses'], 1):
            f.write(f"{i:<6}{result['Date']:<15}{result['Close_Price']:<12}"
                   f"{result['Daily_Change']:<15}{result['Daily_Change_Pct']:<15}"
                   f"{result['Volume']:<15}\n")

    print("\n✓ Results saved to:")
    print("  - silver_analysis_report.txt (human-readable report)")
    print("  - silver_price_analysis.json (structured data)")
    print("  - silver_price_data_full.csv (complete dataset)")
    print("  - silver_top_gains.csv (top 50 gains)")
    print("  - silver_top_losses.csv (top 50 losses)")

def main():
    import sys

    print("=" * 90)
    print("SILVER PRICE MOVEMENT ANALYSIS")
    print("=" * 90)
    print()

    # Check for API key argument
    api_key = sys.argv[1] if len(sys.argv) > 1 else 'demo'

    # Try to fetch real data first
    rows = fetch_alpha_vantage_data(api_key=api_key, symbol='SLV')

    # If failed, use sample data
    if not rows:
        print("\nFalling back to sample data...")
        rows = fetch_sample_data()

    if not rows:
        print("Error: Could not retrieve or generate data.")
        return

    # Process data
    data = process_data(rows)
    print(f"✓ Processed {len(data)} days with price movements\n")

    if not data:
        print("Error: No valid data to analyze.")
        return

    # Calculate statistics
    stats = calculate_statistics(data)

    # Rank movements
    top_gains, top_losses = rank_movements(data, top_n=50)

    # Display summary
    print("=" * 90)
    print("SUMMARY STATISTICS")
    print("=" * 90)
    print(f"Maximum Single-Day Gain: {stats['max_gain_pct']:+.2f}% on {stats['max_gain_date']}")
    print(f"Maximum Single-Day Loss: {stats['max_loss_pct']:+.2f}% on {stats['max_loss_date']}")
    print(f"Average Daily Change: {stats['avg_daily_change_pct']:+.4f}%")
    print(f"Volatility (Std Dev): {stats['volatility_std']:.2f}%")

    print("\n" + "=" * 90)
    print("TOP 10 BIGGEST GAINS")
    print("=" * 90)
    for i, d in enumerate(top_gains[:10], 1):
        pct = d['daily_change_pct'] if d['daily_change_pct'] is not None else 0
        print(f"{i:2d}. {d['date']} - {pct:+.2f}% (Close: ${d['close']:.2f}, Change: ${d['daily_change']:+.2f})")

    print("\n" + "=" * 90)
    print("TOP 10 BIGGEST LOSSES")
    print("=" * 90)
    for i, d in enumerate(top_losses[:10], 1):
        pct = d['daily_change_pct'] if d['daily_change_pct'] is not None else 0
        print(f"{i:2d}. {d['date']} - {pct:+.2f}% (Close: ${d['close']:.2f}, Change: ${d['daily_change']:+.2f})")

    # Save results
    print("\n" + "=" * 90)
    save_results(top_gains, top_losses, data, stats)
    print("\n✓ Analysis complete!")
    print("\nTo get real data, obtain a free API key from https://www.alphavantage.co/support/#api-key")
    print("Then run: python3 analyze_silver_prices_v3.py YOUR_API_KEY")

if __name__ == "__main__":
    main()

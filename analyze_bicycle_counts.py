#!/usr/bin/env python3
"""
NYC Bicycle Ridership Analysis
Analyzes bicycle count data and creates visualizations showing ridership trends over time.
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import numpy as np

def load_and_process_data(csv_path):
    """Load bicycle count data and aggregate by day."""
    print("Loading bicycle count data...")
    
    # Read the CSV with proper date parsing
    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df):,} records")
    
    # Convert date column to datetime
    df['date'] = pd.to_datetime(df['date'])
    
    # Extract just the date (no time) for daily aggregation
    df['date_only'] = df['date'].dt.date
    
    # Group by date and sum the counts
    daily_counts = df.groupby('date_only')['counts'].sum().reset_index()
    daily_counts['date_only'] = pd.to_datetime(daily_counts['date_only'])
    
    # Sort by date
    daily_counts = daily_counts.sort_values('date_only')
    
    print(f"Aggregated to {len(daily_counts)} days of data")
    print(f"Date range: {daily_counts['date_only'].min().strftime('%Y-%m-%d')} to {daily_counts['date_only'].max().strftime('%Y-%m-%d')}")
    
    return daily_counts

def create_ridership_chart(daily_counts):
    """Create a comprehensive ridership visualization."""
    
    # Calculate 7-day and 30-day moving averages
    daily_counts['ma_7'] = daily_counts['counts'].rolling(window=7, center=True).mean()
    daily_counts['ma_30'] = daily_counts['counts'].rolling(window=30, center=True).mean()
    
    # Create the visualization
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10))
    
    # Main time series plot
    ax1.plot(daily_counts['date_only'], daily_counts['counts'], 
             alpha=0.3, color='lightblue', linewidth=0.5, label='Daily counts')
    ax1.plot(daily_counts['date_only'], daily_counts['ma_7'], 
             color='blue', linewidth=1.5, label='7-day moving average')
    ax1.plot(daily_counts['date_only'], daily_counts['ma_30'], 
             color='red', linewidth=2, label='30-day moving average')
    
    ax1.set_title('NYC Bicycle Ridership Over Time', fontsize=16, fontweight='bold')
    ax1.set_ylabel('Daily Bicycle Count', fontsize=12)
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Format x-axis
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
    
    # Monthly aggregation for second plot
    monthly_counts = daily_counts.set_index('date_only').resample('M')['counts'].sum().reset_index()
    
    ax2.bar(monthly_counts['date_only'], monthly_counts['counts'], 
            width=25, alpha=0.7, color='green')
    ax2.set_title('Monthly Total Bicycle Ridership', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Date', fontsize=12)
    ax2.set_ylabel('Monthly Total Count', fontsize=12)
    ax2.grid(True, alpha=0.3)
    
    # Format x-axis for monthly plot
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax2.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)
    
    plt.tight_layout()
    return fig, daily_counts, monthly_counts

def print_statistics(daily_counts, monthly_counts):
    """Print summary statistics."""
    print("\n" + "="*60)
    print("BICYCLE RIDERSHIP STATISTICS")
    print("="*60)
    
    # Overall statistics
    total_rides = daily_counts['counts'].sum()
    avg_daily = daily_counts['counts'].mean()
    median_daily = daily_counts['counts'].median()
    
    print(f"Total bicycle rides recorded: {total_rides:,}")
    print(f"Average daily ridership: {avg_daily:,.0f}")
    print(f"Median daily ridership: {median_daily:,.0f}")
    print(f"Peak daily ridership: {daily_counts['counts'].max():,} on {daily_counts.loc[daily_counts['counts'].idxmax(), 'date_only'].strftime('%Y-%m-%d')}")
    print(f"Lowest daily ridership: {daily_counts['counts'].min():,} on {daily_counts.loc[daily_counts['counts'].idxmin(), 'date_only'].strftime('%Y-%m-%d')}")
    
    # Monthly statistics
    print(f"\nMonthly Statistics:")
    print(f"Average monthly ridership: {monthly_counts['counts'].mean():,.0f}")
    print(f"Peak monthly ridership: {monthly_counts['counts'].max():,} in {monthly_counts.loc[monthly_counts['counts'].idxmax(), 'date_only'].strftime('%Y-%m')}")
    
    # Seasonal analysis
    daily_counts['month'] = daily_counts['date_only'].dt.month
    monthly_avg = daily_counts.groupby('month')['counts'].mean()
    print(f"\nSeasonal Patterns (Average Daily Ridership by Month):")
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    for month in range(1, 13):
        if month in monthly_avg.index:
            print(f"  {month_names[month-1]}: {monthly_avg[month]:,.0f}")

def main():
    csv_path = "Bicycle_Counts_20250824.csv"
    
    try:
        # Load and process data
        daily_counts = load_and_process_data(csv_path)
        
        # Create visualization
        print("\nCreating ridership visualization...")
        fig, daily_counts, monthly_counts = create_ridership_chart(daily_counts)
        
        # Save the chart
        output_file = "bicycle_ridership_over_time.png"
        fig.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"Chart saved as: {output_file}")
        
        # Display statistics
        print_statistics(daily_counts, monthly_counts)
        
        # Show the plot
        plt.show()
        
    except FileNotFoundError:
        print(f"Error: Could not find {csv_path}")
        print("Please make sure the bicycle counts CSV file is in the current directory.")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
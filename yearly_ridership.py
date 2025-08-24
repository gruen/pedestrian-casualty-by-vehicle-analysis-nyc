#!/usr/bin/env python3
"""
NYC Bicycle Ridership - Yearly Analysis with 2025 Projection
Creates a bar chart showing total ridership by year with projection for 2025.
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, date

def load_and_process_yearly_data(csv_path):
    """Load bicycle count data and aggregate by year."""
    print("Loading bicycle count data...")
    
    # Read the CSV
    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df):,} records")
    
    # Convert date column to datetime
    df['date'] = pd.to_datetime(df['date'])
    
    # Extract year
    df['year'] = df['date'].dt.year
    
    # Group by year and sum the counts
    yearly_counts = df.groupby('year')['counts'].sum().reset_index()
    yearly_counts = yearly_counts.sort_values('year')
    
    print(f"Data spans {yearly_counts['year'].min()} to {yearly_counts['year'].max()}")
    
    return yearly_counts

def project_2025_ridership(yearly_counts):
    """Project full year 2025 ridership based on current data and trend."""
    
    # Get 2025 data so far
    ridership_2025_ytd = yearly_counts[yearly_counts['year'] == 2025]['counts'].iloc[0]
    
    # Calculate what day of year Aug 24 is (current date)
    current_date = date(2025, 8, 24)
    day_of_year = current_date.timetuple().tm_yday
    days_remaining = 365 - day_of_year
    
    # Calculate average daily rate for 2025 so far
    daily_rate_2025 = ridership_2025_ytd / day_of_year
    
    # Get trend from recent complete years (2022-2024)
    recent_years = yearly_counts[yearly_counts['year'].isin([2022, 2023, 2024])]
    if len(recent_years) >= 2:
        # Calculate year-over-year growth rate
        growth_rates = []
        for i in range(1, len(recent_years)):
            prev_year = recent_years.iloc[i-1]['counts']
            curr_year = recent_years.iloc[i]['counts']
            growth_rate = (curr_year - prev_year) / prev_year
            growth_rates.append(growth_rate)
        
        avg_growth_rate = np.mean(growth_rates)
    else:
        avg_growth_rate = 0  # fallback if not enough data
    
    # Method 1: Simple projection based on daily rate
    projection_simple = ridership_2025_ytd + (daily_rate_2025 * days_remaining)
    
    # Method 2: Trend-adjusted projection
    # Apply seasonal adjustment - remaining months (Sep-Dec) typically have lower ridership
    seasonal_factor = 0.85  # Based on observed seasonal patterns
    projection_seasonal = ridership_2025_ytd + (daily_rate_2025 * days_remaining * seasonal_factor)
    
    # Use the seasonal-adjusted projection as our estimate
    projection_2025 = projection_seasonal
    
    print(f"\n2025 Projection Analysis:")
    print(f"Current date: August 24, 2025 (Day {day_of_year} of 365)")
    print(f"Ridership through Aug 24: {ridership_2025_ytd:,}")
    print(f"Daily average so far: {daily_rate_2025:,.0f}")
    print(f"Days remaining: {days_remaining}")
    print(f"Recent years growth rate: {avg_growth_rate:.1%}")
    print(f"Projected 2025 total (seasonal adjusted): {projection_2025:,.0f}")
    
    return projection_2025, ridership_2025_ytd

def create_yearly_chart(yearly_counts, projection_2025, ridership_2025_ytd):
    """Create yearly ridership bar chart with 2025 projection."""
    
    # Prepare data for plotting
    years = yearly_counts['year'].tolist()
    counts = yearly_counts['counts'].tolist()
    
    # Replace 2025 partial data with projection
    if 2025 in years:
        idx_2025 = years.index(2025)
        counts[idx_2025] = projection_2025
    
    # Create the plot
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Create bars with different colors for actual vs projected
    colors = ['steelblue' if year != 2025 else 'orange' for year in years]
    bars = ax.bar(years, counts, color=colors, alpha=0.8, edgecolor='black', linewidth=0.5)
    
    # Add value labels on top of bars
    for bar, count in zip(bars, counts):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + max(counts)*0.01,
                f'{count/1000000:.1f}M', ha='center', va='bottom', fontweight='bold')
    
    # Highlight 2025 projection
    if 2025 in years:
        idx_2025 = years.index(2025)
        ax.text(2025, projection_2025/2, f'Projected\n(through Aug 24:\n{ridership_2025_ytd/1000000:.1f}M)', 
                ha='center', va='center', fontweight='bold', 
                bbox=dict(boxstyle="round,pad=0.3", facecolor="orange", alpha=0.7))
    
    ax.set_title('NYC Bicycle Ridership by Year', fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('Total Annual Ridership', fontsize=12)
    ax.grid(True, alpha=0.3, axis='y')
    
    # Format y-axis to show millions
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x/1000000:.1f}M'))
    
    # Add legend
    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor='steelblue', alpha=0.8, label='Actual'),
                       Patch(facecolor='orange', alpha=0.8, label='2025 Projection')]
    ax.legend(handles=legend_elements, loc='upper left')
    
    plt.tight_layout()
    return fig

def print_yearly_statistics(yearly_counts, projection_2025):
    """Print yearly statistics."""
    print("\n" + "="*50)
    print("YEARLY BICYCLE RIDERSHIP STATISTICS")
    print("="*50)
    
    # Update 2025 with projection for stats
    yearly_stats = yearly_counts.copy()
    if 2025 in yearly_stats['year'].values:
        yearly_stats.loc[yearly_stats['year'] == 2025, 'counts'] = projection_2025
    
    print(f"Peak year: {yearly_stats.loc[yearly_stats['counts'].idxmax(), 'year']} ({yearly_stats['counts'].max()/1000000:.1f}M rides)")
    print(f"Lowest year: {yearly_stats.loc[yearly_stats['counts'].idxmin(), 'year']} ({yearly_stats['counts'].min()/1000000:.1f}M rides)")
    
    # Calculate growth from first to projected last year
    first_year_count = yearly_stats.iloc[0]['counts']
    last_year_count = yearly_stats.iloc[-1]['counts']
    total_growth = (last_year_count - first_year_count) / first_year_count * 100
    years_span = yearly_stats.iloc[-1]['year'] - yearly_stats.iloc[0]['year']
    avg_annual_growth = ((last_year_count / first_year_count) ** (1/years_span) - 1) * 100
    
    print(f"Total growth ({yearly_stats.iloc[0]['year']}-{yearly_stats.iloc[-1]['year']}): {total_growth:.1f}%")
    print(f"Average annual growth rate: {avg_annual_growth:.1f}%")

def main():
    csv_path = "Bicycle_Counts_20250824.csv"
    
    try:
        # Load and process data
        yearly_counts = load_and_process_yearly_data(csv_path)
        
        # Project 2025 ridership
        projection_2025, ridership_2025_ytd = project_2025_ridership(yearly_counts)
        
        # Create visualization
        print("\nCreating yearly ridership chart...")
        fig = create_yearly_chart(yearly_counts, projection_2025, ridership_2025_ytd)
        
        # Save the chart
        output_file = "bicycle_ridership_by_year.png"
        fig.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"Chart saved as: {output_file}")
        
        # Display statistics
        print_yearly_statistics(yearly_counts, projection_2025)
        
        # Show the plot
        plt.show()
        
    except FileNotFoundError:
        print(f"Error: Could not find {csv_path}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
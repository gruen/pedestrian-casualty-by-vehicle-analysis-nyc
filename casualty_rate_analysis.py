#!/usr/bin/env python3
"""
NYC Bicycle Casualty Rate Analysis

Calculates pedestrian casualty rates per bicycle ridership to show actual risk levels.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from collections import defaultdict
from typing import Dict, List, Any, Tuple
import os
import sys
from datetime import datetime

# Ridership data from NYC_Bicycle_Ridership_Analysis.md
RIDERSHIP_DATA = {
    2012: 1611856,
    2013: 323533,  # Note: likely incomplete data
    2014: 9261909,
    2015: 13797937,
    2016: 16005658,
    2017: 14481794,
    2018: 12544736,
    2019: 12346460,
    2020: 13577322,
    2021: 13690962,
    2022: 14621312,
    2023: 17466861,
    2024: 21064730,
    2025: 20783683  # Projected
}

def get_bike_casualty_data_by_year():
    """Load bike casualty data from the previous analysis."""
    # This matches the data from bike_vs_ebike_analysis for all years
    return {
        'Traditional Bicycle': {
            2012: {'injured': 0, 'killed': 0},
            2013: {'injured': 2, 'killed': 0},
            2014: {'injured': 0, 'killed': 0},
            2015: {'injured': 1, 'killed': 0},
            2016: {'injured': 39, 'killed': 0},
            2017: {'injured': 79, 'killed': 4},
            2018: {'injured': 88, 'killed': 0},
            2019: {'injured': 96, 'killed': 3},
            2020: {'injured': 187, 'killed': 0},
            2021: {'injured': 194, 'killed': 0},
            2022: {'injured': 228, 'killed': 3},
            2023: {'injured': 264, 'killed': 0},
            2024: {'injured': 298, 'killed': 2},
            2025: {'injured': 243, 'killed': 2}  # Projected
        },
        'E-Bike': {
            2015: {'injured': 0, 'killed': 0},
            2016: {'injured': 188, 'killed': 0},
            2017: {'injured': 186, 'killed': 0},
            2018: {'injured': 123, 'killed': 0},
            2019: {'injured': 132, 'killed': 0},
            2020: {'injured': 62, 'killed': 0},  # 2020+ data from focused analysis
            2021: {'injured': 165, 'killed': 3},
            2022: {'injured': 209, 'killed': 2},
            2023: {'injured': 205, 'killed': 3},
            2024: {'injured': 166, 'killed': 0},
            2025: {'injured': 125, 'killed': 3}  # Projected
        },
        'E-Scooter': {
            2019: {'injured': 53, 'killed': 0},
            2020: {'injured': 71, 'killed': 2},
            2021: {'injured': 100, 'killed': 0},
            2022: {'injured': 117, 'killed': 1},
            2023: {'injured': 118, 'killed': 0},
            2024: {'injured': 99, 'killed': 1},
            2025: {'injured': 53, 'killed': 0}  # Projected
        }
    }

def calculate_casualty_rates():
    """Calculate casualty rates per million rides."""
    bike_casualties = get_bike_casualty_data_by_year()
    
    # Calculate total bike casualties per year (all bike types combined)
    yearly_totals = defaultdict(lambda: {'injured': 0, 'killed': 0, 'total': 0})
    
    for bike_type, year_data in bike_casualties.items():
        for year, casualties in year_data.items():
            yearly_totals[year]['injured'] += casualties['injured']
            yearly_totals[year]['killed'] += casualties['killed']
            yearly_totals[year]['total'] += casualties['injured'] + casualties['killed']
    
    # Calculate rates per million rides
    casualty_rates = []
    
    for year in sorted(RIDERSHIP_DATA.keys()):
        if year in yearly_totals and RIDERSHIP_DATA[year] > 0:
            rides = RIDERSHIP_DATA[year]
            casualties = yearly_totals[year]['total']
            injured = yearly_totals[year]['injured']
            killed = yearly_totals[year]['killed']
            
            # Rate per million rides
            casualty_rate = (casualties / rides) * 1000000
            injury_rate = (injured / rides) * 1000000
            fatality_rate = (killed / rides) * 1000000
            
            casualty_rates.append({
                'year': year,
                'rides': rides,
                'casualties': casualties,
                'injured': injured,
                'killed': killed,
                'casualty_rate_per_million': casualty_rate,
                'injury_rate_per_million': injury_rate,
                'fatality_rate_per_million': fatality_rate,
                'is_projected': year == 2025
            })
    
    return casualty_rates

def create_casualty_rate_chart(casualty_rates):
    """Create casualty rate per ridership chart."""
    
    # Convert to DataFrame for easier plotting
    df = pd.DataFrame(casualty_rates)
    
    # Exclude 2013 due to incomplete ridership data
    df = df[df['year'] != 2013].copy()
    
    # Set up the plotting style to match charts 5/6
    plt.style.use('default')
    sns.set_palette("husl")
    
    # Create single chart
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    fig.suptitle('NYC Pedestrian Casualty Rate per Million Bicycle Rides', 
                 fontsize=14, fontweight='bold', y=0.95)
    
    years = df['year'].values
    casualty_rates_values = df['casualty_rate_per_million'].values
    
    # Color code projected vs actual (matching chart5/6 style)
    colors = ['darkred' if projected else 'steelblue' for projected in df['is_projected']]
    
    bars = ax.bar(years, casualty_rates_values, color=colors, alpha=0.8, width=0.6)
    
    # Add value labels (matching chart5/6 style)
    for i, (year, rate, projected) in enumerate(zip(years, casualty_rates_values, df['is_projected'])):
        if rate > max(casualty_rates_values) * 0.05:  # Only label if significant
            label = f'{rate:.1f}{"*" if projected else ""}'
            ax.text(year, rate + max(casualty_rates_values) * 0.02, label, 
                   ha='center', va='bottom', fontweight='bold', fontsize=9)
    
    ax.set_xlabel('Year')
    ax.set_ylabel('Casualties per Million Rides')
    ax.set_title('Pedestrian Safety Risk by Year', fontweight='bold', pad=15)
    
    # Match grid style from other charts
    ax.grid(True, alpha=0.3)
    
    # Set x-axis to show all years
    ax.set_xticks(years)
    ax.set_xticklabels([str(int(y)) for y in years], rotation=0)
    
    plt.tight_layout()
    
    # Add projection note (matching other charts)
    fig.text(0.02, 0.02, '*2025 data projected to full year', fontsize=10, style='italic')
    
    plt.savefig('chart7_casualty_rates_vs_ridership.png', dpi=300, bbox_inches='tight')
    print("Saved: chart7_casualty_rates_vs_ridership.png")
    plt.close()

def generate_casualty_rate_report(casualty_rates):
    """Generate console report with casualty rate analysis."""
    
    print("\n" + "="*80)
    print("NYC BICYCLE CASUALTY RATE ANALYSIS")
    print("="*80)
    
    print(f"\nCASSUALTY RATES PER MILLION RIDES:")
    print("-" * 70)
    print(f"{'Year':<6} {'Rides (M)':<10} {'Casualties':<11} {'Rate/M':<8} {'Status':<10}")
    print("-" * 70)
    
    for data in casualty_rates:
        if data['year'] == 2013:  # Skip 2013 due to bad data
            continue
            
        status = "Projected" if data['is_projected'] else "Actual"
        print(f"{data['year']:<6} {data['rides']/1000000:<10.1f} "
              f"{data['casualties']:<11.0f} {data['casualty_rate_per_million']:<8.1f} {status:<10}")
    
    # Calculate key insights
    # Exclude 2013 and 2025 for trend analysis, and years with 0 casualties for meaningful trends
    trend_data = [d for d in casualty_rates if d['year'] not in [2013, 2025] and d['casualties'] > 0]
    
    if len(trend_data) >= 2:
        first_year = trend_data[0]
        last_year = trend_data[-1]
        
        ridership_change = ((last_year['rides'] - first_year['rides']) / first_year['rides']) * 100
        
        # Handle division by zero for casualty change
        if first_year['casualties'] > 0:
            casualty_change = ((last_year['casualties'] - first_year['casualties']) / first_year['casualties']) * 100
        else:
            casualty_change = float('inf') if last_year['casualties'] > 0 else 0
            
        # Handle division by zero for rate change
        if first_year['casualty_rate_per_million'] > 0:
            rate_change = ((last_year['casualty_rate_per_million'] - first_year['casualty_rate_per_million']) / 
                          first_year['casualty_rate_per_million']) * 100
        else:
            rate_change = float('inf') if last_year['casualty_rate_per_million'] > 0 else 0
        
        print(f"\nKEY INSIGHTS ({first_year['year']}-{last_year['year']}):")
        print("-" * 40)
        print(f"Ridership Growth: {ridership_change:+.1f}%")
        
        if casualty_change == float('inf'):
            print(f"Total Casualties Change: From 0 to {last_year['casualties']} (infinite increase)")
        else:
            print(f"Total Casualties Change: {casualty_change:+.1f}%")
            
        if rate_change == float('inf'):
            print(f"Casualty Rate Change: From 0 to {last_year['casualty_rate_per_million']:.1f}/M rides")
        else:
            print(f"Casualty Rate Change: {rate_change:+.1f}%")
        
        # Safety trend
        if rate_change < 0:
            print(f"✓ Cycling has become SAFER per ride ({rate_change:.1f}% rate decrease)")
        else:
            print(f"⚠ Cycling has become MORE DANGEROUS per ride ({rate_change:.1f}% rate increase)")
    
    # Find safest and most dangerous years
    valid_data = [d for d in casualty_rates if d['year'] != 2013]  # Exclude 2013
    
    if valid_data:
        safest = min(valid_data, key=lambda x: x['casualty_rate_per_million'])
        most_dangerous = max(valid_data, key=lambda x: x['casualty_rate_per_million'])
        
        print(f"\nSAFETY EXTREMES:")
        print(f"Safest Year: {safest['year']} ({safest['casualty_rate_per_million']:.1f} casualties/M rides)")
        print(f"Most Dangerous: {most_dangerous['year']} ({most_dangerous['casualty_rate_per_million']:.1f} casualties/M rides)")
        
        if safest['casualty_rate_per_million'] > 0:
            safety_ratio = most_dangerous['casualty_rate_per_million'] / safest['casualty_rate_per_million']
            print(f"Risk Ratio: {safety_ratio:.1f}x higher in worst vs best year")
        else:
            print(f"Risk Ratio: Infinite (safest year had 0 casualties)")
    
    print("="*80)

def main():
    # Calculate casualty rates
    casualty_rates = calculate_casualty_rates()
    
    # Create visualization
    print("Creating casualty rate visualization...")
    create_casualty_rate_chart(casualty_rates)
    
    # Generate report
    generate_casualty_rate_report(casualty_rates)
    
    print(f"\nCasualty rate analysis complete!")

if __name__ == '__main__':
    main()
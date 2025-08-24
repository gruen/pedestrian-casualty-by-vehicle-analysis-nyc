#!/usr/bin/env python3
"""
NYC Pedestrian Casualties: Bicycles vs E-Bikes Analysis

Focused analysis comparing traditional bicycles vs e-bikes in pedestrian collisions over time.
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

def load_and_preprocess_data(filename: str) -> pd.DataFrame:
    """Load CSV data and filter for pedestrian casualties involving bikes."""
    print("Loading collision data...")
    
    # Check if file exists
    if not os.path.exists(filename):
        print(f"Error: File '{filename}' not found.")
        sys.exit(1)
    
    try:
        df = pd.read_csv(filename, low_memory=False)
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        sys.exit(1)
    
    # Check required columns exist
    required_columns = ['CRASH DATE', 'NUMBER OF PEDESTRIANS INJURED', 'NUMBER OF PEDESTRIANS KILLED',
                       'VEHICLE TYPE CODE 1', 'VEHICLE TYPE CODE 2', 'VEHICLE TYPE CODE 3',
                       'VEHICLE TYPE CODE 4', 'VEHICLE TYPE CODE 5']
    
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        print(f"Error: Missing required columns: {missing_columns}")
        sys.exit(1)
    
    # Parse dates and extract year
    try:
        df['CRASH DATE'] = pd.to_datetime(df['CRASH DATE'], errors='coerce')
        df['YEAR'] = df['CRASH DATE'].dt.year
    except Exception as e:
        print(f"Error parsing dates: {e}")
        sys.exit(1)
    
    # Filter for valid dates and pedestrian casualties
    df = df[df['YEAR'].notna()].copy()
    pedestrian_collisions = df[
        (df['NUMBER OF PEDESTRIANS INJURED'] > 0) | 
        (df['NUMBER OF PEDESTRIANS KILLED'] > 0)
    ].copy()
    
    # Filter for bike-involved collisions
    vehicle_cols = ['VEHICLE TYPE CODE 1', 'VEHICLE TYPE CODE 2', 'VEHICLE TYPE CODE 3',
                   'VEHICLE TYPE CODE 4', 'VEHICLE TYPE CODE 5']
    
    bike_types = ['Bike', 'BIKE', 'E-Bike', 'E-BIKE', 'E-Scooter', 'E-SCOOTER']
    
    bike_mask = False
    for col in vehicle_cols:
        bike_mask |= pedestrian_collisions[col].isin(bike_types)
    
    bike_collisions = pedestrian_collisions[bike_mask].copy()
    
    print(f"Total collision records: {len(df):,}")
    print(f"Collisions with pedestrian casualties: {len(pedestrian_collisions):,}")
    print(f"Bike-involved pedestrian casualties: {len(bike_collisions):,}")
    print(f"Date range: {bike_collisions['YEAR'].min():.0f} - {bike_collisions['YEAR'].max():.0f}")
    
    return bike_collisions

def extract_bike_data_by_year(df: pd.DataFrame) -> Dict[str, Dict[int, Dict[str, float]]]:
    """Extract yearly casualty data by specific bike type."""
    # Structure: {bike_type: {year: {injured: count, killed: count}}}
    yearly_data = defaultdict(lambda: defaultdict(lambda: {'injured': 0, 'killed': 0}))
    
    # Calculate 2025 projection factor
    latest_date = df['CRASH DATE'].max()
    days_in_2025 = (latest_date - pd.Timestamp("2025-01-01")).days + 1
    projection_factor = 365 / days_in_2025 if days_in_2025 > 0 else 1.0
    
    # Vehicle type columns
    vehicle_cols = ['VEHICLE TYPE CODE 1', 'VEHICLE TYPE CODE 2', 'VEHICLE TYPE CODE 3', 
                   'VEHICLE TYPE CODE 4', 'VEHICLE TYPE CODE 5']
    
    # Bike type mapping
    bike_mapping = {
        'Bike': 'Traditional Bicycle',
        'BIKE': 'Traditional Bicycle',
        'E-Bike': 'E-Bike',
        'E-BIKE': 'E-Bike',
        'E-Scooter': 'E-Scooter',
        'E-SCOOTER': 'E-Scooter'
    }
    
    for _, row in df.iterrows():
        # Safe conversion of casualty numbers and year
        try:
            injured = int(pd.to_numeric(row['NUMBER OF PEDESTRIANS INJURED'], errors='coerce') or 0)
            killed = int(pd.to_numeric(row['NUMBER OF PEDESTRIANS KILLED'], errors='coerce') or 0)
            year = int(row['YEAR'])
        except (ValueError, TypeError):
            continue
        
        # Only process data from 2020 onwards for better data quality
        if year < 2020:
            continue
            
        # Apply projection factor for 2025 data
        if year == 2025:
            injured *= projection_factor
            killed *= projection_factor
        
        # Get all bike types involved in this collision
        bikes_in_collision = []
        for col in vehicle_cols:
            vehicle = row[col]
            if pd.notna(vehicle) and str(vehicle).strip() in bike_mapping:
                bike_type = bike_mapping[str(vehicle).strip()]
                bikes_in_collision.append(bike_type)
        
        # If no valid bike types found, skip this collision
        if not bikes_in_collision:
            continue
            
        # Remove duplicates while preserving order
        unique_bikes = list(dict.fromkeys(bikes_in_collision))
        
        # Distribute casualties among unique bike types in collision
        casualty_per_bike_injured = injured / len(unique_bikes)
        casualty_per_bike_killed = killed / len(unique_bikes)
        
        for bike_type in unique_bikes:
            yearly_data[bike_type][year]['injured'] += casualty_per_bike_injured
            yearly_data[bike_type][year]['killed'] += casualty_per_bike_killed
    
    return dict(yearly_data)

def create_bike_comparison_charts(yearly_data: Dict[str, Dict[int, Dict[str, float]]]) -> None:
    """Create comparison charts for bicycles vs e-bikes."""
    
    # Get all years in the data
    all_years = set()
    for bike_data in yearly_data.values():
        all_years.update(bike_data.keys())
    all_years = sorted(list(all_years))
    
    # Create figure with single chart
    fig, ax1 = plt.subplots(1, 1, figsize=(12, 8))
    fig.suptitle('NYC Pedestrian Casualties: Traditional Bicycles vs E-Bikes (2020-2025)', 
                 fontsize=18, fontweight='bold', y=0.95)
    
    # Colors for different bike types
    colors = {
        'Traditional Bicycle': 'forestgreen',
        'E-Bike': 'darkorange', 
        'E-Scooter': 'purple'
    }
    
    # 1. Total casualties over time (line chart)
    ax1.set_title('Total Pedestrian Casualties Over Time', fontweight='bold', pad=15)
    
    for bike_type, year_data in yearly_data.items():
        years = []
        totals = []
        
        for year in all_years:
            years.append(year)
            data = year_data.get(year, {'injured': 0, 'killed': 0})
            total = data['injured'] + data['killed']
            totals.append(total)
        
        ax1.plot(years, totals, marker='o', linewidth=2, markersize=6, 
                label=bike_type, color=colors.get(bike_type, 'gray'))
        
        # Add data labels for non-zero points
        for x, y in zip(years, totals):
            if y > 0:
                label = f'{int(y)}'
                if x == 2025:  # Mark projected data
                    label += '*'
                ax1.annotate(label, (x, y), textcoords="offset points", 
                           xytext=(0,10), ha='center', fontsize=8)
    
    ax1.set_xlabel('Year')
    ax1.set_ylabel('Total Casualties')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Add projection note
    plt.figtext(0.02, 0.02, '*2025 data projected to full year', fontsize=10, style='italic')
    
    plt.savefig('chart6_bike_vs_ebike_trends.png', dpi=300, bbox_inches='tight')
    print("Saved: chart6_bike_vs_ebike_trends.png")
    plt.close()

def generate_bike_analysis_data(yearly_data: Dict[str, Dict[int, Dict[str, float]]]) -> Dict[str, Any]:
    """Generate analysis data for markdown report."""
    
    # Get all years
    all_years = set()
    for bike_data in yearly_data.values():
        all_years.update(bike_data.keys())
    all_years = sorted(list(all_years))
    
    analysis = {
        'years_covered': f"{min(all_years):.0f}-{max(all_years):.0f}",
        'bike_types': {},
        'yearly_totals': {},
        'key_insights': []
    }
    
    # Calculate totals and trends for each bike type
    for bike_type, year_data in yearly_data.items():
        total_injured = sum(data['injured'] for data in year_data.values())
        total_killed = sum(data['killed'] for data in year_data.values())
        total_casualties = total_injured + total_killed
        fatality_rate = (total_killed / total_casualties * 100) if total_casualties > 0 else 0
        
        # Find first and last years with data
        years_with_data = [year for year, data in year_data.items() 
                          if data['injured'] + data['killed'] > 0]
        
        first_year = min(years_with_data) if years_with_data else None
        last_year = max(years_with_data) if years_with_data else None
        
        # Calculate growth if possible
        growth_rate = None
        if first_year and last_year and first_year != last_year:
            first_total = year_data[first_year]['injured'] + year_data[first_year]['killed']
            last_total = year_data[last_year]['injured'] + year_data[last_year]['killed']
            if first_total > 0:
                growth_rate = ((last_total - first_total) / first_total) * 100
        
        analysis['bike_types'][bike_type] = {
            'total_injured': total_injured,
            'total_killed': total_killed,
            'total_casualties': total_casualties,
            'fatality_rate': fatality_rate,
            'first_year': first_year,
            'last_year': last_year,
            'growth_rate': growth_rate,
            'yearly_data': dict(year_data)
        }
    
    # Calculate yearly totals across all bike types
    for year in all_years:
        year_injured = sum(yearly_data[bt].get(year, {'injured': 0})['injured'] 
                          for bt in yearly_data.keys())
        year_killed = sum(yearly_data[bt].get(year, {'killed': 0})['killed'] 
                         for bt in yearly_data.keys())
        analysis['yearly_totals'][year] = {
            'injured': year_injured,
            'killed': year_killed,
            'total': year_injured + year_killed
        }
    
    # Generate key insights
    bike_types_by_casualties = sorted(analysis['bike_types'].items(), 
                                    key=lambda x: x[1]['total_casualties'], reverse=True)
    
    if bike_types_by_casualties:
        top_type = bike_types_by_casualties[0]
        analysis['key_insights'].append(
            f"{top_type[0]} causes the most pedestrian casualties ({top_type[1]['total_casualties']:.0f} total)"
        )
    
    # E-bike emergence insight
    if 'E-Bike' in analysis['bike_types'] and analysis['bike_types']['E-Bike']['first_year']:
        ebike_first = analysis['bike_types']['E-Bike']['first_year']
        analysis['key_insights'].append(
            f"E-Bikes first appeared in casualty data in {ebike_first:.0f}"
        )
    
    # Growth rate insights
    for bike_type, data in analysis['bike_types'].items():
        if data['growth_rate'] is not None:
            if data['growth_rate'] > 50:
                analysis['key_insights'].append(
                    f"{bike_type} casualties have grown significantly ({data['growth_rate']:+.0f}% since {data['first_year']:.0f})"
                )
    
    return analysis

def main() -> None:
    filename = 'Motor_Vehicle_Collisions_-_Crashes_20250824.csv'
    
    # Load and preprocess data
    bike_collisions = load_and_preprocess_data(filename)
    
    # Extract bike data by year
    print("\nExtracting bike casualty data by year...")
    yearly_data = extract_bike_data_by_year(bike_collisions)
    
    # Create visualizations
    print("Creating bike comparison visualizations...")
    create_bike_comparison_charts(yearly_data)
    
    # Generate analysis data for markdown
    analysis_data = generate_bike_analysis_data(yearly_data)
    
    print(f"\nBike vs E-bike analysis complete!")
    return analysis_data

if __name__ == '__main__':
    main()
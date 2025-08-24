#!/usr/bin/env python3
"""
NYC Pedestrian Casualty Yearly Trends Analysis

Analyzes collision data to show pedestrian injuries and deaths by vehicle category over time.
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

def get_vehicle_category_mapping() -> Dict[str, str]:
    """Define mapping from specific vehicle types to consolidated categories."""
    return {
        # Passenger Vehicles
        'Sedan': 'Passenger Vehicles',
        'SEDAN': 'Passenger Vehicles',
        '4 dr sedan': 'Passenger Vehicles',
        'Station Wagon/Sport Utility Vehicle': 'Passenger Vehicles',
        'SPORT UTILITY / STATION WAGON': 'Passenger Vehicles',
        'PASSENGER VEHICLE': 'Passenger Vehicles',
        'Pick-up Truck': 'Passenger Vehicles',
        'PICK-UP TRUCK': 'Passenger Vehicles',
        'PK': 'Passenger Vehicles',
        'Convertible': 'Passenger Vehicles',
        
        # Taxi/Livery
        'Taxi': 'Taxi/Livery',
        'TAXI': 'Taxi/Livery',
        'LIVERY VEHICLE': 'Taxi/Livery',
        
        # Large/Commercial Vehicles
        'Bus': 'Large/Commercial Vehicles',
        'BUS': 'Large/Commercial Vehicles',
        'Box Truck': 'Large/Commercial Vehicles',
        'BOX TRUCK': 'Large/Commercial Vehicles',
        'Dump': 'Large/Commercial Vehicles',
        'DUMP': 'Large/Commercial Vehicles',
        'Tractor Truck Diesel': 'Large/Commercial Vehicles',
        'TRACTOR TRUCK DIESEL': 'Large/Commercial Vehicles',
        'Garbage or Refuse': 'Large/Commercial Vehicles',
        'GARBAGE OR REFUSE': 'Large/Commercial Vehicles',
        'LARGE COM VEH(6 OR MORE TIRES)': 'Large/Commercial Vehicles',
        'SMALL COM VEH(4 TIRES)': 'Large/Commercial Vehicles',
        'Ambulance': 'Large/Commercial Vehicles',
        'AMBULANCE': 'Large/Commercial Vehicles',
        'Fire Truck': 'Large/Commercial Vehicles',
        'FIRE TRUCK': 'Large/Commercial Vehicles',
        'Flat Bed': 'Large/Commercial Vehicles',
        
        # Motorcycles
        'Motorcycle': 'Motorcycles',
        'MOTORCYCLE': 'Motorcycles',
        'Motorbike': 'Motorcycles',
        'Moped': 'Motorcycles',
        'MOPED': 'Motorcycles',
        
        # Bicycles/Scooters
        'Bike': 'Bicycles/Scooters',
        'BIKE': 'Bicycles/Scooters',
        'E-Bike': 'Bicycles/Scooters',
        'E-BIKE': 'Bicycles/Scooters',
        'E-Scooter': 'Bicycles/Scooters',
        'E-SCOOTER': 'Bicycles/Scooters',
        
        # Van
        'Van': 'Van',
        'VAN': 'Van',
        
        # Other/Unknown
        'UNKNOWN': 'Other/Unknown',
        'OTHER': 'Other/Unknown'
    }

def load_and_preprocess_data(filename: str) -> pd.DataFrame:
    """Load CSV data and filter for pedestrian casualties."""
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
    
    print(f"Total collision records: {len(df):,}")
    print(f"Collisions with pedestrian casualties: {len(pedestrian_collisions):,}")
    print(f"Date range: {pedestrian_collisions['YEAR'].min():.0f} - {pedestrian_collisions['YEAR'].max():.0f}")
    print(f"Total pedestrian injuries: {pedestrian_collisions['NUMBER OF PEDESTRIANS INJURED'].sum():,}")
    print(f"Total pedestrian deaths: {pedestrian_collisions['NUMBER OF PEDESTRIANS KILLED'].sum():,}")
    
    return pedestrian_collisions

def extract_yearly_data_by_category(df: pd.DataFrame) -> Dict[str, Dict[int, Dict[str, float]]]:
    """Extract yearly casualty data by vehicle category."""
    category_mapping = get_vehicle_category_mapping()
    # Structure: {category: {year: {injured: count, killed: count}}}
    yearly_data = defaultdict(lambda: defaultdict(lambda: {'injured': 0, 'killed': 0}))
    
    # Calculate 2025 projection factor
    latest_date = df['CRASH DATE'].max()
    days_in_2025 = (latest_date - pd.Timestamp("2025-01-01")).days + 1
    projection_factor = 365 / days_in_2025 if days_in_2025 > 0 else 1.0
    
    # Vehicle type columns
    vehicle_cols = ['VEHICLE TYPE CODE 1', 'VEHICLE TYPE CODE 2', 'VEHICLE TYPE CODE 3', 
                   'VEHICLE TYPE CODE 4', 'VEHICLE TYPE CODE 5']
    
    for _, row in df.iterrows():
        # Safe conversion of casualty numbers and year
        try:
            injured = int(pd.to_numeric(row['NUMBER OF PEDESTRIANS INJURED'], errors='coerce') or 0)
            killed = int(pd.to_numeric(row['NUMBER OF PEDESTRIANS KILLED'], errors='coerce') or 0)
            year = int(row['YEAR'])
        except (ValueError, TypeError):
            continue
        
        # Apply projection factor for 2025 data
        if year == 2025:
            injured *= projection_factor
            killed *= projection_factor
        
        # Get all vehicle types involved in this collision
        vehicles_in_collision = []
        for col in vehicle_cols:
            vehicle = row[col]
            if pd.notna(vehicle) and str(vehicle).strip() and str(vehicle).strip().upper() not in ['', 'UNKNOWN', 'NAN']:
                vehicle_type = str(vehicle).strip()
                # Map to category or use Other/Unknown if not found
                category = category_mapping.get(vehicle_type, 'Other/Unknown')
                vehicles_in_collision.append(category)
        
        # If no valid vehicle types found, skip this collision
        if not vehicles_in_collision:
            continue
            
        # Remove duplicates while preserving order
        unique_vehicles = list(dict.fromkeys(vehicles_in_collision))
        
        # Distribute casualties among unique vehicle categories in collision
        casualty_per_category_injured = injured / len(unique_vehicles)
        casualty_per_category_killed = killed / len(unique_vehicles)
        
        for category in unique_vehicles:
            yearly_data[category][year]['injured'] += casualty_per_category_injured
            yearly_data[category][year]['killed'] += casualty_per_category_killed
    
    return dict(yearly_data)

def create_yearly_trends_charts(yearly_data: Dict[str, Dict[int, Dict[str, float]]]) -> None:
    """Create individual bar charts for each vehicle category showing yearly trends."""
    
    # Get all years in the data
    all_years = set()
    for category_data in yearly_data.values():
        all_years.update(category_data.keys())
    all_years = sorted(list(all_years))
    
    # Sort categories by total casualties (descending)
    category_totals = []
    for category, year_data in yearly_data.items():
        total = sum(data['injured'] + data['killed'] for data in year_data.values())
        category_totals.append((category, total))
    category_totals.sort(key=lambda x: x[1], reverse=True)
    
    # Create subplots - 4 rows, 2 columns for 7 categories + 1 summary
    fig, axes = plt.subplots(4, 2, figsize=(20, 24))
    fig.suptitle('NYC Pedestrian Casualties by Vehicle Category - Yearly Trends', 
                 fontsize=20, fontweight='bold', y=0.98)
    
    # Flatten axes for easier iteration
    axes_flat = axes.flatten()
    
    # Create individual charts for each category
    for idx, (category, total) in enumerate(category_totals):
        ax = axes_flat[idx]
        year_data = yearly_data[category]
        
        # Prepare data for this category
        years = []
        injured_counts = []
        killed_counts = []
        
        for year in all_years:
            years.append(year)
            injured_counts.append(year_data.get(year, {'injured': 0})['injured'])
            killed_counts.append(year_data.get(year, {'killed': 0})['killed'])
        
        # Create stacked bar chart
        x_pos = np.arange(len(years))
        bars_injured = ax.bar(x_pos, injured_counts, label='Injured', color='steelblue', alpha=0.8)
        bars_killed = ax.bar(x_pos, killed_counts, bottom=injured_counts, label='Killed', color='darkred', alpha=0.8)
        
        # Customize chart
        ax.set_xticks(x_pos)
        ax.set_xticklabels([str(int(y)) for y in years], rotation=45)
        ax.set_ylabel('Pedestrian Casualties')
        ax.set_title(f'{category}\n(Total: {total:,.0f} casualties)', fontweight='bold', pad=10)
        ax.legend(loc='upper right', fontsize=8)
        
        # Add value labels for significant bars
        for i, (injured, killed) in enumerate(zip(injured_counts, killed_counts)):
            total_bar = injured + killed
            if total_bar > max(injured_counts + killed_counts) * 0.1:  # Only label if >10% of max
                label = f'{int(total_bar)}'
                if years[i] == 2025:  # Mark projected data
                    label += '*'
                ax.text(i, total_bar + max(injured_counts + killed_counts) * 0.02, 
                       label, ha='center', va='bottom', fontweight='bold', fontsize=8)
    
    # Create summary chart in the last subplot
    summary_ax = axes_flat[7]
    
    # Aggregate data across all categories by year
    total_by_year = defaultdict(lambda: {'injured': 0, 'killed': 0})
    for category_data in yearly_data.values():
        for year, data in category_data.items():
            total_by_year[year]['injured'] += data['injured']
            total_by_year[year]['killed'] += data['killed']
    
    # Prepare summary data
    summary_years = []
    summary_injured = []
    summary_killed = []
    
    for year in all_years:
        summary_years.append(year)
        summary_injured.append(total_by_year[year]['injured'])
        summary_killed.append(total_by_year[year]['killed'])
    
    # Create summary stacked bar chart
    x_pos = np.arange(len(summary_years))
    summary_ax.bar(x_pos, summary_injured, label='Injured', color='steelblue', alpha=0.8)
    summary_ax.bar(x_pos, summary_killed, bottom=summary_injured, label='Killed', color='darkred', alpha=0.8)
    
    summary_ax.set_xticks(x_pos)
    summary_ax.set_xticklabels([str(int(y)) for y in summary_years], rotation=45)
    summary_ax.set_ylabel('Total Pedestrian Casualties')
    summary_ax.set_title('ALL CATEGORIES COMBINED\n(Overall Yearly Trends)', fontweight='bold', pad=10)
    summary_ax.legend(loc='upper right', fontsize=8)
    
    # Add trend line to summary
    total_casualties_by_year = [i + k for i, k in zip(summary_injured, summary_killed)]
    z = np.polyfit(range(len(total_casualties_by_year)), total_casualties_by_year, 1)
    p = np.poly1d(z)
    summary_ax.plot(range(len(total_casualties_by_year)), p(range(len(total_casualties_by_year))), 
                   "r--", alpha=0.8, linewidth=2, label=f'Trend (slope: {z[0]:+.0f}/year)')
    summary_ax.legend(loc='upper right', fontsize=8)
    
    plt.tight_layout()
    plt.subplots_adjust(top=0.93)
    
    # Add projection note
    fig.text(0.02, 0.02, '*2025 data projected to full year', fontsize=10, style='italic')
    
    plt.savefig('chart5_yearly_trends_by_category.png', dpi=300, bbox_inches='tight')
    print("Saved: chart5_yearly_trends_by_category.png")
    plt.close()

def generate_yearly_report(yearly_data: Dict[str, Dict[int, Dict[str, float]]]) -> None:
    """Generate console report with yearly trends analysis."""
    
    # Get all years
    all_years = set()
    for category_data in yearly_data.values():
        all_years.update(category_data.keys())
    all_years = sorted(list(all_years))
    
    print("\n" + "="*80)
    print("NYC PEDESTRIAN CASUALTY YEARLY TRENDS ANALYSIS")
    print("="*80)
    
    # Calculate totals by year
    totals_by_year = defaultdict(lambda: {'injured': 0, 'killed': 0})
    for category_data in yearly_data.values():
        for year, data in category_data.items():
            totals_by_year[year]['injured'] += data['injured']
            totals_by_year[year]['killed'] += data['killed']
    
    print(f"\nOVERALL YEARLY TRENDS ({min(all_years):.0f}-{max(all_years):.0f}):")
    print("-" * 60)
    print(f"{'Year':<6} {'Injured':<10} {'Killed':<8} {'Total':<10} {'Fatal%':<8}")
    print("-" * 60)
    
    for year in all_years:
        injured = totals_by_year[year]['injured']
        killed = totals_by_year[year]['killed']
        total = injured + killed
        fatal_rate = (killed / total * 100) if total > 0 else 0
        
        print(f"{year:<6.0f} {injured:<10.0f} {killed:<8.0f} {total:<10.0f} {fatal_rate:<8.1f}")
    
    # Calculate year-over-year changes
    if len(all_years) >= 2:
        first_year = all_years[0]
        last_year = all_years[-1]
        first_total = totals_by_year[first_year]['injured'] + totals_by_year[first_year]['killed']
        last_total = totals_by_year[last_year]['injured'] + totals_by_year[last_year]['killed']
        
        if first_total > 0:
            change_pct = ((last_total - first_total) / first_total) * 100
            print(f"\nOVERALL CHANGE ({first_year:.0f} to {last_year:.0f}): {change_pct:+.1f}%")
    
    # Show trends for top categories
    print(f"\nTOP CATEGORIES - YEARLY BREAKDOWN:")
    print("="*80)
    
    # Sort categories by total casualties
    category_totals = []
    for category, year_data in yearly_data.items():
        total = sum(data['injured'] + data['killed'] for data in year_data.values())
        category_totals.append((category, total, year_data))
    category_totals.sort(key=lambda x: x[1], reverse=True)
    
    for category, total, year_data in category_totals[:5]:  # Top 5 categories
        print(f"\n{category} (Total: {total:,.0f} casualties):")
        print("-" * 50)
        print(f"{'Year':<6} {'Injured':<8} {'Killed':<6} {'Total':<8} {'Fatal%':<6}")
        print("-" * 50)
        
        for year in all_years:
            data = year_data.get(year, {'injured': 0, 'killed': 0})
            injured = data['injured']
            killed = data['killed']
            year_total = injured + killed
            fatal_rate = (killed / year_total * 100) if year_total > 0 else 0
            
            print(f"{year:<6.0f} {injured:<8.0f} {killed:<6.0f} {year_total:<8.0f} {fatal_rate:<6.1f}")
    
    print("="*80)

def main() -> None:
    filename = 'Motor_Vehicle_Collisions_-_Crashes_20250824.csv'
    
    # Load and preprocess data
    pedestrian_collisions = load_and_preprocess_data(filename)
    
    # Extract yearly data by category
    print("\nExtracting yearly casualty data by vehicle category...")
    yearly_data = extract_yearly_data_by_category(pedestrian_collisions)
    
    # Create visualizations
    print("Creating yearly trends visualizations...")
    create_yearly_trends_charts(yearly_data)
    
    # Generate report
    generate_yearly_report(yearly_data)
    
    print(f"\nYearly trends analysis complete!")

if __name__ == '__main__':
    main()
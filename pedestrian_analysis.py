#!/usr/bin/env python3
"""
NYC Pedestrian Casualty Analysis by Vehicle Type

Analyzes collision data to show pedestrian injuries and deaths by vehicle type.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from collections import defaultdict
from typing import Dict, List, Any, Tuple
import os
import sys

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
    required_columns = ['NUMBER OF PEDESTRIANS INJURED', 'NUMBER OF PEDESTRIANS KILLED',
                       'VEHICLE TYPE CODE 1', 'VEHICLE TYPE CODE 2', 'VEHICLE TYPE CODE 3',
                       'VEHICLE TYPE CODE 4', 'VEHICLE TYPE CODE 5']
    
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        print(f"Error: Missing required columns: {missing_columns}")
        sys.exit(1)
    
    # Filter for collisions with pedestrian casualties
    pedestrian_collisions = df[
        (df['NUMBER OF PEDESTRIANS INJURED'] > 0) | 
        (df['NUMBER OF PEDESTRIANS KILLED'] > 0)
    ].copy()
    
    print(f"Total collision records: {len(df):,}")
    print(f"Collisions with pedestrian casualties: {len(pedestrian_collisions):,}")
    print(f"Total pedestrian injuries: {pedestrian_collisions['NUMBER OF PEDESTRIANS INJURED'].sum():,}")
    print(f"Total pedestrian deaths: {pedestrian_collisions['NUMBER OF PEDESTRIANS KILLED'].sum():,}")
    
    return pedestrian_collisions

def extract_vehicle_types(df: pd.DataFrame) -> Dict[str, Dict[str, float]]:
    """Extract and consolidate vehicle types from all vehicle columns."""
    vehicle_casualties = defaultdict(lambda: {'injured': 0, 'killed': 0})
    
    # Vehicle type columns
    vehicle_cols = ['VEHICLE TYPE CODE 1', 'VEHICLE TYPE CODE 2', 'VEHICLE TYPE CODE 3', 
                   'VEHICLE TYPE CODE 4', 'VEHICLE TYPE CODE 5']
    
    for _, row in df.iterrows():
        # Safe conversion of casualty numbers
        try:
            injured = int(pd.to_numeric(row['NUMBER OF PEDESTRIANS INJURED'], errors='coerce') or 0)
            killed = int(pd.to_numeric(row['NUMBER OF PEDESTRIANS KILLED'], errors='coerce') or 0)
        except (ValueError, TypeError):
            injured = killed = 0
        
        # Get all vehicle types involved in this collision
        vehicles_in_collision = []
        for col in vehicle_cols:
            vehicle = row[col]
            if pd.notna(vehicle) and str(vehicle).strip() and str(vehicle).strip().upper() not in ['', 'UNKNOWN', 'NAN']:
                vehicles_in_collision.append(str(vehicle).strip())
        
        # If no valid vehicle types found, skip this collision
        if not vehicles_in_collision:
            continue
            
        # Distribute casualties among all vehicles in collision
        casualty_per_vehicle_injured = injured / len(vehicles_in_collision)
        casualty_per_vehicle_killed = killed / len(vehicles_in_collision)
        
        for vehicle in vehicles_in_collision:
            vehicle_casualties[vehicle]['injured'] += casualty_per_vehicle_injured
            vehicle_casualties[vehicle]['killed'] += casualty_per_vehicle_killed
    
    return vehicle_casualties

def clean_vehicle_types(vehicle_casualties: Dict[str, Dict[str, float]]) -> Dict[str, Dict[str, float]]:
    """Clean and standardize vehicle type names."""
    # Mapping for similar vehicle types
    vehicle_mapping = {
        'Station Wagon/Sport Utility Vehicle': 'SUV/Station Wagon',
        'SPORT UTILITY / STATION WAGON': 'SUV/Station Wagon',
        'Sedan': 'Sedan',
        'SEDAN': 'Sedan',
        'Pick-up Truck': 'Pickup Truck',
        'PICK-UP TRUCK': 'Pickup Truck',
        'Box Truck': 'Box Truck',
        'BOX TRUCK': 'Box Truck',
        'Taxi': 'Taxi',
        'TAXI': 'Taxi',
        'Bus': 'Bus',
        'BUS': 'Bus',
        'Bike': 'Bicycle',
        'BIKE': 'Bicycle',
        'E-Bike': 'E-Bike',
        'E-BIKE': 'E-Bike',
        'E-Scooter': 'E-Scooter',
        'E-SCOOTER': 'E-Scooter',
        'Motorcycle': 'Motorcycle',
        'MOTORCYCLE': 'Motorcycle',
        'Tractor Truck Diesel': 'Tractor Truck',
        'TRACTOR TRUCK DIESEL': 'Tractor Truck',
        'Dump': 'Dump Truck',
        'DUMP': 'Dump Truck',
        'Garbage or Refuse': 'Garbage Truck',
        'GARBAGE OR REFUSE': 'Garbage Truck',
        'Ambulance': 'Ambulance',
        'AMBULANCE': 'Ambulance',
        'Fire Truck': 'Fire Truck',
        'FIRE TRUCK': 'Fire Truck',
        'Van': 'Van',
        'VAN': 'Van',
        'Moped': 'Moped',
        'MOPED': 'Moped'
    }
    
    cleaned_casualties = defaultdict(lambda: {'injured': 0, 'killed': 0})
    
    for vehicle, casualties in vehicle_casualties.items():
        # Clean the vehicle name
        clean_name = vehicle_mapping.get(vehicle, vehicle)
        cleaned_casualties[clean_name]['injured'] += casualties['injured']
        cleaned_casualties[clean_name]['killed'] += casualties['killed']
    
    return dict(cleaned_casualties)

def create_visualizations(vehicle_data: Dict[str, Dict[str, float]]) -> pd.DataFrame:
    """Create visualizations for pedestrian casualties by vehicle type."""
    # Convert to DataFrame for easier plotting
    data_for_plot = []
    for vehicle, casualties in vehicle_data.items():
        total = casualties['injured'] + casualties['killed']
        if total >= 10:  # Only include vehicle types with significant casualties
            data_for_plot.append({
                'Vehicle Type': vehicle,
                'Injured': casualties['injured'],
                'Killed': casualties['killed'],
                'Total': total,
                'Fatality Rate': casualties['killed'] / total if total > 0 else 0.0
            })
    
    df_plot = pd.DataFrame(data_for_plot).sort_values('Total', ascending=False)
    
    # Set up the plotting style
    plt.style.use('default')
    sns.set_palette("husl")
    
    # Create figure with subplots
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(20, 16))
    fig.suptitle('NYC Pedestrian Casualties by Vehicle Type', fontsize=20, fontweight='bold')
    
    # 1. Top vehicle types by total casualties
    top_15 = df_plot.head(15)
    bars = ax1.barh(range(len(top_15)), top_15['Total'])
    ax1.set_yticks(range(len(top_15)))
    ax1.set_yticklabels(top_15['Vehicle Type'])
    ax1.set_xlabel('Total Pedestrian Casualties')
    ax1.set_title('Top 15 Vehicle Types by Total Pedestrian Casualties')
    ax1.invert_yaxis()
    
    # Add value labels on bars
    for i, (bar, value) in enumerate(zip(bars, top_15['Total'])):
        ax1.text(value + max(top_15['Total']) * 0.01, bar.get_y() + bar.get_height()/2, 
                f'{int(value):,}', va='center', fontweight='bold')
    
    # 2. Injuries vs Deaths by vehicle type (top 10)
    top_10 = df_plot.head(10)
    x_pos = np.arange(len(top_10))
    width = 0.35
    
    bars1 = ax2.bar(x_pos - width/2, top_10['Injured'], width, label='Injured', alpha=0.8)
    bars2 = ax2.bar(x_pos + width/2, top_10['Killed'], width, label='Killed', alpha=0.8)
    
    ax2.set_xlabel('Vehicle Type')
    ax2.set_ylabel('Number of Pedestrian Casualties')
    ax2.set_title('Pedestrian Injuries vs Deaths by Vehicle Type (Top 10)')
    ax2.set_xticks(x_pos)
    ax2.set_xticklabels(top_10['Vehicle Type'], rotation=45, ha='right')
    ax2.legend()
    
    # Add value labels
    for bar in bars1:
        height = bar.get_height()
        if height > 0:
            ax2.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                    f'{int(height):,}', ha='center', va='bottom', fontsize=8)
    
    for bar in bars2:
        height = bar.get_height()
        if height > 0:
            ax2.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                    f'{int(height):,}', ha='center', va='bottom', fontsize=8)
    
    # 3. Fatality rate by vehicle type (top 10)
    fatality_data = df_plot[df_plot['Total'] >= 50].head(10)  # Only vehicles with 50+ total casualties
    bars3 = ax3.bar(range(len(fatality_data)), fatality_data['Fatality Rate'] * 100)
    ax3.set_xlabel('Vehicle Type')
    ax3.set_ylabel('Fatality Rate (%)')
    ax3.set_title('Pedestrian Fatality Rate by Vehicle Type (Min 50 casualties)')
    ax3.set_xticks(range(len(fatality_data)))
    ax3.set_xticklabels(fatality_data['Vehicle Type'], rotation=45, ha='right')
    
    # Add value labels
    for i, (bar, value) in enumerate(zip(bars3, fatality_data['Fatality Rate'])):
        ax3.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.1,
                f'{value*100:.1f}%', ha='center', va='bottom', fontweight='bold')
    
    # 4. Distribution pie chart (top 10 + others)
    top_10_pie = df_plot.head(10)
    others_total = df_plot.iloc[10:]['Total'].sum()
    
    pie_data = list(top_10_pie['Total']) + [others_total]
    pie_labels = list(top_10_pie['Vehicle Type']) + ['Others']
    
    wedges, texts, autotexts = ax4.pie(pie_data, labels=pie_labels, autopct='%1.1f%%', startangle=90)
    ax4.set_title('Distribution of Pedestrian Casualties by Vehicle Type')
    
    # Make percentage text bold
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
        autotext.set_fontsize(9)
    
    plt.tight_layout()
    plt.savefig('pedestrian_casualties_by_vehicle_type.png', dpi=300, bbox_inches='tight')
    print("\nVisualization saved as 'pedestrian_casualties_by_vehicle_type.png'")
    
    return df_plot

def generate_report(vehicle_data: Dict[str, Dict[str, float]], df_plot: pd.DataFrame) -> None:
    """Generate a summary report with key insights."""
    total_injured = sum(v['injured'] for v in vehicle_data.values())
    total_killed = sum(v['killed'] for v in vehicle_data.values())
    
    print("\n" + "="*80)
    print("NYC PEDESTRIAN CASUALTY ANALYSIS BY VEHICLE TYPE")
    print("="*80)
    print(f"\nOVERALL STATISTICS:")
    print(f"Total Pedestrian Injuries: {total_injured:,.0f}")
    print(f"Total Pedestrian Deaths: {total_killed:,.0f}")
    print(f"Overall Fatality Rate: {(total_killed/(total_injured + total_killed))*100:.2f}%")
    
    print(f"\nTOP 10 MOST DANGEROUS VEHICLE TYPES FOR PEDESTRIANS:")
    print("-" * 80)
    print(f"{'Rank':<4} {'Vehicle Type':<30} {'Injured':<10} {'Killed':<8} {'Total':<8} {'Fatal%':<8}")
    print("-" * 80)
    
    for idx, (_, row) in enumerate(df_plot.head(10).iterrows(), 1):
        print(f"{idx:<4} {row['Vehicle Type']:<30} "
              f"{row['Injured']:<10.0f} {row['Killed']:<8.0f} {row['Total']:<8.0f} "
              f"{row['Fatality Rate']*100:<8.1f}")
    
    print(f"\nHIGHEST FATALITY RATES (Min 50 total casualties):")
    print("-" * 60)
    high_fatality = df_plot[df_plot['Total'] >= 50].sort_values('Fatality Rate', ascending=False).head(5)
    print(f"{'Vehicle Type':<30} {'Fatal Rate':<12} {'Total Cases':<12}")
    print("-" * 60)
    for _, row in high_fatality.iterrows():
        print(f"{row['Vehicle Type']:<30} {row['Fatality Rate']*100:<12.1f}% {row['Total']:<12.0f}")
    
    print(f"\nKEY INSIGHTS:")
    print("-" * 40)
    top_vehicle = df_plot.iloc[0]
    print(f"• {top_vehicle['Vehicle Type']} causes the most pedestrian casualties ({top_vehicle['Total']:.0f} total)")
    print(f"• The top 10 vehicle types account for {(df_plot.head(10)['Total'].sum()/(total_injured + total_killed))*100:.1f}% of all pedestrian casualties")
    
    # Find vehicle type with highest fatality rate (min 100 cases)
    high_fatal_vehicle = df_plot[df_plot['Total'] >= 100].sort_values('Fatality Rate', ascending=False).iloc[0]
    print(f"• {high_fatal_vehicle['Vehicle Type']} has the highest fatality rate among common vehicles ({high_fatal_vehicle['Fatality Rate']*100:.1f}%)")
    
    print("="*80)

def main() -> None:
    filename = 'Motor_Vehicle_Collisions_-_Crashes_20250824.csv'
    
    # Load and preprocess data
    pedestrian_collisions = load_and_preprocess_data(filename)
    
    # Extract vehicle types and casualties
    print("\nExtracting vehicle types...")
    vehicle_casualties = extract_vehicle_types(pedestrian_collisions)
    
    # Clean vehicle type names
    print("Cleaning vehicle type names...")
    cleaned_vehicle_data = clean_vehicle_types(vehicle_casualties)
    
    # Create visualizations
    print("Creating visualizations...")
    df_plot = create_visualizations(cleaned_vehicle_data)
    
    # Generate report
    generate_report(cleaned_vehicle_data, df_plot)

if __name__ == '__main__':
    main()
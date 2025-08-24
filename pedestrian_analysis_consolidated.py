#!/usr/bin/env python3
"""
NYC Pedestrian Casualty Analysis by Vehicle Category

Analyzes collision data to show pedestrian injuries and deaths by consolidated vehicle categories.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from collections import defaultdict
from typing import Dict, List, Any, Tuple
import os
import sys

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

def extract_and_categorize_vehicles(df: pd.DataFrame) -> Dict[str, Dict[str, float]]:
    """Extract vehicle types and consolidate into categories."""
    category_mapping = get_vehicle_category_mapping()
    category_casualties = defaultdict(lambda: {'injured': 0, 'killed': 0})
    
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
            category_casualties[category]['injured'] += casualty_per_category_injured
            category_casualties[category]['killed'] += casualty_per_category_killed
    
    return dict(category_casualties)

def create_stacked_bar_chart(category_data: Dict[str, Dict[str, float]]) -> None:
    """Create stacked horizontal bar chart for injuries and deaths."""
    # Prepare data
    categories = []
    injured_counts = []
    killed_counts = []
    
    # Sort by total casualties
    sorted_categories = sorted(category_data.items(), 
                             key=lambda x: x[1]['injured'] + x[1]['killed'], 
                             reverse=True)
    
    for category, casualties in sorted_categories:
        categories.append(category)
        injured_counts.append(casualties['injured'])
        killed_counts.append(casualties['killed'])
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Create stacked horizontal bars
    y_pos = np.arange(len(categories))
    bars_injured = ax.barh(y_pos, injured_counts, label='Injured', color='steelblue', alpha=0.8)
    bars_killed = ax.barh(y_pos, killed_counts, left=injured_counts, label='Killed', color='darkred', alpha=0.8)
    
    # Customize chart
    ax.set_yticks(y_pos)
    ax.set_yticklabels(categories)
    ax.invert_yaxis()
    ax.set_xlabel('Number of Pedestrian Casualties')
    ax.set_title('NYC Pedestrian Casualties by Vehicle Category\n(Stacked: Injuries and Deaths)', 
                fontsize=14, fontweight='bold', pad=20)
    ax.legend(loc='lower right')
    
    # Add value labels
    for i, (injured, killed) in enumerate(zip(injured_counts, killed_counts)):
        total = injured + killed
        # Label for total
        ax.text(total + max(injured_counts + killed_counts) * 0.01, i, 
                f'{int(total):,}', va='center', ha='left', fontweight='bold')
        # Label for killed (if significant)
        if killed > total * 0.05:  # Only show if killed > 5% of total
            ax.text(injured + killed/2, i, f'{int(killed)}', 
                   va='center', ha='center', color='white', fontweight='bold', fontsize=9)
    
    plt.tight_layout()
    plt.savefig('chart1_stacked_casualties.png', dpi=300, bbox_inches='tight')
    print("Saved: chart1_stacked_casualties.png")
    plt.close()

def create_fatality_rate_chart(category_data: Dict[str, Dict[str, float]]) -> None:
    """Create fatality rate comparison chart."""
    # Prepare data
    categories = []
    fatality_rates = []
    total_casualties = []
    
    for category, casualties in category_data.items():
        total = casualties['injured'] + casualties['killed']
        if total > 0:
            rate = casualties['killed'] / total
            categories.append(category)
            fatality_rates.append(rate * 100)
            total_casualties.append(total)
    
    # Sort by fatality rate
    sorted_data = sorted(zip(categories, fatality_rates, total_casualties), 
                        key=lambda x: x[1], reverse=True)
    categories, fatality_rates, total_casualties = zip(*sorted_data)
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Create bars with color based on total casualties (darker = more casualties)
    max_casualties = max(total_casualties) if total_casualties else 1
    colors = plt.cm.Reds([min(1.0, t/max_casualties) for t in total_casualties])
    bars = ax.bar(range(len(categories)), fatality_rates, color=colors, alpha=0.8)
    
    # Customize chart
    ax.set_xticks(range(len(categories)))
    ax.set_xticklabels(categories, rotation=45, ha='right')
    ax.set_ylabel('Fatality Rate (%)')
    ax.set_title('Pedestrian Fatality Rate by Vehicle Category', 
                fontsize=14, fontweight='bold', pad=20)
    
    # Add value labels
    for bar, rate, total in zip(bars, fatality_rates, total_casualties):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                f'{rate:.1f}%\n({int(total):,} cases)', 
                ha='center', va='bottom', fontweight='bold', fontsize=9)
    
    plt.tight_layout()
    plt.savefig('chart2_fatality_rates.png', dpi=300, bbox_inches='tight')
    print("Saved: chart2_fatality_rates.png")
    plt.close()

def create_distribution_pie_chart(category_data: Dict[str, Dict[str, float]]) -> None:
    """Create pie chart showing distribution of casualties."""
    # Prepare data
    categories = []
    totals = []
    
    for category, casualties in category_data.items():
        total = casualties['injured'] + casualties['killed']
        categories.append(category)
        totals.append(total)
    
    # Sort by total
    sorted_data = sorted(zip(categories, totals), key=lambda x: x[1], reverse=True)
    categories, totals = zip(*sorted_data)
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Create pie chart with distinct colors
    colors = plt.cm.Set3(np.linspace(0, 1, len(categories)))
    wedges, texts, autotexts = ax.pie(totals, labels=categories, autopct='%1.1f%%', 
                                     startangle=90, colors=colors)
    
    # Customize
    ax.set_title('Distribution of Pedestrian Casualties by Vehicle Category', 
                fontsize=14, fontweight='bold', pad=20)
    
    # Make percentage text more readable
    for autotext in autotexts:
        autotext.set_color('black')
        autotext.set_fontweight('bold')
        autotext.set_fontsize(10)
    
    plt.tight_layout()
    plt.savefig('chart3_distribution_pie.png', dpi=300, bbox_inches='tight')
    print("Saved: chart3_distribution_pie.png")
    plt.close()

def create_summary_table(category_data: Dict[str, Dict[str, float]]) -> None:
    """Create detailed breakdown table as an image."""
    # Prepare data
    table_data = []
    total_injured = sum(c['injured'] for c in category_data.values())
    total_killed = sum(c['killed'] for c in category_data.values())
    grand_total = total_injured + total_killed
    
    sorted_categories = sorted(category_data.items(), 
                             key=lambda x: x[1]['injured'] + x[1]['killed'], 
                             reverse=True)
    
    for category, casualties in sorted_categories:
        injured = casualties['injured']
        killed = casualties['killed']
        total = injured + killed
        fatality_rate = (killed / total * 100) if total > 0 else 0
        pct_of_total = (total / grand_total * 100) if grand_total > 0 else 0
        
        table_data.append([
            category,
            f"{injured:,.0f}",
            f"{killed:,.0f}",
            f"{total:,.0f}",
            f"{fatality_rate:.1f}%",
            f"{pct_of_total:.1f}%"
        ])
    
    # Add totals row
    overall_fatality_rate = (total_killed / grand_total * 100) if grand_total > 0 else 0
    table_data.append([
        "TOTAL",
        f"{total_injured:,.0f}",
        f"{total_killed:,.0f}",
        f"{grand_total:,.0f}",
        f"{overall_fatality_rate:.1f}%",
        "100.0%"
    ])
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.axis('tight')
    ax.axis('off')
    
    # Create table
    headers = ['Vehicle Category', 'Injured', 'Killed', 'Total', 'Fatality Rate', '% of All Casualties']
    table = ax.table(cellText=table_data, colLabels=headers, cellLoc='center', loc='center')
    
    # Style the table
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 2)
    
    # Style header
    for i in range(len(headers)):
        table[(0, i)].set_facecolor('#4CAF50')
        table[(0, i)].set_text_props(weight='bold', color='white')
    
    # Style totals row
    for i in range(len(headers)):
        table[(len(table_data), i)].set_facecolor('#E0E0E0')
        table[(len(table_data), i)].set_text_props(weight='bold')
    
    # Alternate row colors
    for i in range(1, len(table_data)):
        if i % 2 == 0:
            for j in range(len(headers)):
                table[(i, j)].set_facecolor('#F5F5F5')
    
    plt.title('NYC Pedestrian Casualties by Vehicle Category - Detailed Breakdown', 
              fontsize=14, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig('chart4_summary_table.png', dpi=300, bbox_inches='tight')
    print("Saved: chart4_summary_table.png")
    plt.close()

def generate_console_report(category_data: Dict[str, Dict[str, float]]) -> None:
    """Generate console report with key statistics."""
    total_injured = sum(c['injured'] for c in category_data.values())
    total_killed = sum(c['killed'] for c in category_data.values())
    grand_total = total_injured + total_killed
    
    print("\n" + "="*80)
    print("NYC PEDESTRIAN CASUALTY ANALYSIS BY VEHICLE CATEGORY")
    print("="*80)
    print(f"\nOVERALL STATISTICS:")
    print(f"Total Pedestrian Injuries: {total_injured:,.0f}")
    print(f"Total Pedestrian Deaths: {total_killed:,.0f}")
    print(f"Overall Fatality Rate: {(total_killed/grand_total)*100:.2f}%")
    
    print(f"\nVEHICLE CATEGORIES BY TOTAL CASUALTIES:")
    print("-" * 80)
    print(f"{'Category':<25} {'Injured':<10} {'Killed':<8} {'Total':<10} {'Fatal%':<8} {'% Total':<8}")
    print("-" * 80)
    
    sorted_categories = sorted(category_data.items(), 
                             key=lambda x: x[1]['injured'] + x[1]['killed'], 
                             reverse=True)
    
    for category, casualties in sorted_categories:
        injured = casualties['injured']
        killed = casualties['killed']
        total = injured + killed
        fatality_rate = (killed / total * 100) if total > 0 else 0
        pct_total = (total / grand_total * 100) if grand_total > 0 else 0
        
        print(f"{category:<25} {injured:<10.0f} {killed:<8.0f} {total:<10.0f} "
              f"{fatality_rate:<8.1f} {pct_total:<8.1f}")
    
    print("\nKEY INSIGHTS:")
    print("-" * 40)
    top_category = max(category_data.items(), key=lambda x: x[1]['injured'] + x[1]['killed'])
    top_name, top_casualties = top_category
    top_total = top_casualties['injured'] + top_casualties['killed']
    
    # Find category with highest fatality rate (safe division)
    def safe_fatality_rate(item):
        _, casualties = item
        total = casualties['injured'] + casualties['killed']
        return casualties['killed'] / total if total > 0 else 0
    
    highest_fatality = max(category_data.items(), key=safe_fatality_rate)
    hf_name, hf_casualties = highest_fatality
    hf_total = hf_casualties['injured'] + hf_casualties['killed']
    hf_rate = (hf_casualties['killed'] / hf_total * 100) if hf_total > 0 else 0
    
    print(f"• {top_name} cause the most pedestrian casualties ({top_total:.0f} total)")
    print(f"• {hf_name} have the highest fatality rate ({hf_rate:.1f}%)")
    print(f"• Top 3 categories account for {sum((c['injured'] + c['killed']) for _, c in sorted_categories[:3])/grand_total*100:.1f}% of all casualties")
    print("="*80)

def main() -> None:
    filename = 'Motor_Vehicle_Collisions_-_Crashes_20250824.csv'
    
    # Load and preprocess data
    pedestrian_collisions = load_and_preprocess_data(filename)
    
    # Extract and categorize vehicle types
    print("\nExtracting and categorizing vehicle types...")
    category_data = extract_and_categorize_vehicles(pedestrian_collisions)
    
    # Create visualizations
    print("Creating visualizations...")
    create_stacked_bar_chart(category_data)
    create_fatality_rate_chart(category_data)
    create_distribution_pie_chart(category_data)
    create_summary_table(category_data)
    
    # Generate report
    generate_console_report(category_data)
    
    print(f"\nAll visualizations saved as separate PNG files!")

if __name__ == '__main__':
    main()
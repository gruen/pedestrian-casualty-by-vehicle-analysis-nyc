# NYC Pedestrian Casualty Analysis

This comprehensive project analyzes NYC vehicle collision data to understand pedestrian injuries and deaths by vehicle type, providing insights into traffic safety patterns, temporal trends, and micromobility safety risks.

Data from [NYC Open Data](https://opendata.cityofnewyork.us) (too big to include in repo, but download as CSV from links below)

- [Collision data](https://data.cityofnewyork.us/Public-Safety/Motor-Vehicle-Collisions-Crashes/h9gi-nx95/about_data)
- [Bicycle Ridership data](https://data.cityofnewyork.us/Transportation/Bicycle-Counts/uczf-rk3c/about_data)

Claude Code Sonnet 4 ran most of this analysis. (And I didn't help. Take this all as directionally correct, and if you're a reporter, check my math.)

## Overview

This multi-faceted analysis examines NYC pedestrian safety from multiple angles:
1. **Vehicle category analysis** - Consolidates 100+ vehicle types into meaningful categories
2. **Temporal trends analysis** - Shows how pedestrian casualties have changed over time (2012-2025)
3. **Micromobility focus** - Deep dive into bicycle vs e-bike vs e-scooter safety (2020-2025)
4. **Risk-adjusted analysis** - Casualty rates per total bicycle ridership

## Data Sources

- **Motor Vehicle Collisions**: 2,199,933 total collision records through August 2024
- **Pedestrian Casualties**: 126,326 collisions involving pedestrian injuries or deaths
- **Bicycle Ridership**: 174,985,578 total bicycle trips (2012-2025)
- **Time Period**: 2012-2025 with 2025 data projected to full year

## Key Findings

### Overall Statistics (Current Analysis)
- **Total Pedestrian Injuries**: 115,657
- **Total Pedestrian Deaths**: 1,621
- **Overall Fatality Rate**: 1.38%
- **Trend**: Overall casualties +37% from 2012-2025 (projected)

### Vehicle Categories by Risk Level

| Rank | Category | Total Casualties | Fatality Rate | % of Total |
|------|----------|------------------|---------------|------------|
| 1 | **Large/Commercial Vehicles** | 4,228 | **6.0%** ⚠️ | 3.6% |
| 2 | Other/Unknown | 2,276 | 2.6% | 1.9% |
| 3 | Van | 2,195 | 1.8% | 1.9% |
| 4 | Motorcycles | 1,365 | 1.4% | 1.2% |
| 5 | **Passenger Vehicles** | 96,252 | 1.2% | **82.1%** |
| 6 | Taxi/Livery | 7,111 | 0.8% | 6.1% |
| 7 | Bicycles/Scooters | 3,850 | 0.6% | 3.3% |

### Micromobility Safety Analysis (2020-2025)

| Vehicle Type | Total Casualties | Fatality Rate | Growth Rate |
|--------------|------------------|---------------|-------------|
| **E-Bikes** | 943 | **1.2%** ⚠️ | +106% |
| Traditional Bicycles | 1,421 | 0.5% | +31% |
| E-Scooters | 562 | 0.7% | -28% |

### Bicycle Safety Risk Over Time
- **2015**: 0.1 casualties per million bicycle rides
- **2022**: 38.3 casualties per million rides (peak danger)
- **2025**: 20.5 casualties per million rides (projected improvement)

## Analysis Scripts

### Core Analysis Scripts
```bash
# Main consolidated vehicle category analysis
python pedestrian_analysis_consolidated.py

# Original detailed vehicle type breakdown
python pedestrian_analysis.py

# Yearly trends analysis (2012-2025)
python yearly_trends_analysis.py

# Bicycle vs E-bike focused analysis (2020-2025)
python bike_vs_ebike_analysis.py

# Casualty rates adjusted for bicycle ridership
python casualty_rate_analysis.py
```

### Requirements
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install pandas matplotlib seaborn numpy
```

## Visualizations Generated

### Chart 1: Stacked Casualties (`chart1_stacked_casualties.png`)
- Horizontal stacked bar chart by vehicle category
- Blue = injuries, Red = deaths
- Shows total volume and death proportion

### Chart 2: Fatality Rates (`chart2_fatality_rates.png`)
- Fatality rate comparison across vehicle categories
- Highlights dangerous vs safe vehicle types
- Color intensity shows total casualty volume

### Chart 3: Distribution Pie Chart (`chart3_distribution_pie.png`)
- Proportional distribution of casualties by category
- Shows passenger vehicle dominance (82.1%)

### Chart 4: Summary Table (`chart4_summary_table.png`)
- Complete statistical breakdown in table format
- Sorted by fatality rate (descending)
- Includes percentages and totals

### Chart 5: Yearly Trends (`chart5_yearly_trends_by_category.png`)
- Individual bar charts for each vehicle category (2012-2025)
- Shows temporal patterns and COVID impact
- Includes overall trend summary
- **2025 data projected to full year**

### Chart 6: Bike Trends (`chart6_bike_vs_ebike_trends.png`)
- Micromobility trends comparison (2020-2025)
- Traditional bikes vs E-bikes vs E-scooters
- Shows concerning E-bike safety trends
- **2025 data projected to full year**

### Chart 7: Bicycle Safety Risk (`chart7_casualty_rates_vs_ridership.png`)
- Pedestrian casualties per million bicycle rides
- Risk-adjusted view accounting for ridership volume
- Shows true safety trends independent of usage growth

## Detailed Reports

### `detailed_breakdown_table.md`
- Complete category definitions and vehicle mappings
- Statistics sorted by fatality rate
- Policy implications by category

### `bike_vs_ebike_analysis.md`
- Comprehensive micromobility safety analysis (2020-2025)
- E-bike safety concerns and policy recommendations
- Growth trends and projections

### `NYC_Bicycle_Ridership_Analysis.md`
- Annual bicycle ridership data (2012-2025)
- 20.8M rides projected for 2025
- Seasonal patterns and growth analysis

## Project Structure

```
nyc-pedestrians-2025/
├── README.md                                    # This file
├── Motor_Vehicle_Collisions_-_Crashes_20250824.csv  # Raw collision data
├──
├── # Analysis Scripts
├── pedestrian_analysis_consolidated.py         # Main category analysis
├── pedestrian_analysis.py                      # Detailed vehicle analysis
├── yearly_trends_analysis.py                   # Temporal trends analysis
├── bike_vs_ebike_analysis.py                   # Micromobility analysis
├── casualty_rate_analysis.py                   # Risk-adjusted analysis
├──
├── # Generated Visualizations
├── chart1_stacked_casualties.png              # Category casualties
├── chart2_fatality_rates.png                  # Fatality rate comparison
├── chart3_distribution_pie.png                # Distribution pie chart
├── chart4_summary_table.png                   # Summary statistics table
├── chart5_yearly_trends_by_category.png       # Temporal trends by category
├── chart6_bike_vs_ebike_trends.png            # Micromobility trends
├── chart7_casualty_rates_vs_ridership.png     # Risk-adjusted bicycle safety
├──
├── # Reports and Analysis
├── detailed_breakdown_table.md                # Category analysis report
├── bike_vs_ebike_analysis.md                  # Micromobility safety report
├── NYC_Bicycle_Ridership_Analysis.md          # Ridership data analysis
├──
└── venv/                                       # Python virtual environment
```

## Methodology

### Vehicle Categorization
```python
Vehicle Categories:
├── Passenger Vehicles: Sedan, SUV, Pickup, Passenger Vehicle
├── Taxi/Livery: Taxi, Livery Vehicle, For-hire vehicles
├── Large/Commercial: Bus, Truck, Box Truck, Dump Truck, Ambulance
├── Motorcycles: Motorcycle, Motorbike, Moped
├── Bicycles/Scooters: Bike, E-Bike, E-Scooter
├── Van: Van variants
└── Other/Unknown: Unspecified or rare vehicle types
```

### Analysis Process
1. **Data Loading**: Filter 2.2M records for pedestrian casualties only
2. **Vehicle Extraction**: Extract vehicles from 5 vehicle type columns per collision
3. **Category Mapping**: Map specific types to consolidated categories
4. **Casualty Distribution**: Distribute casualties among all vehicles in multi-vehicle collisions
5. **Temporal Analysis**: Year-over-year trends with 2025 projections
6. **Risk Adjustment**: Calculate rates per ridership volume where applicable

### Data Quality Notes
- **2025 Projections**: Based on 8 months of data (through August 24), projected to full year
- **Projection Factor**: 1.58x (365 days ÷ 231 days of 2025 data)
- **Multi-Vehicle Collisions**: Casualties distributed equally among all vehicles involved
- **Micromobility Focus**: 2020+ data used for better categorization accuracy
- **Ridership Integration**: NYC bicycle count data used for risk-adjusted analysis

## Critical Safety Insights

### Immediate Concerns
1. **Large/Commercial Vehicles**: 6.0% fatality rate requires urgent intervention
2. **E-Bike Safety Crisis**: 2.4x higher fatality rate than traditional bicycles
3. **Volume vs Risk**: Passenger vehicles cause most casualties but have lower individual risk

### Policy Priorities
1. **Commercial Vehicle Oversight**: Enhanced training, speed limits, separated lanes
2. **E-Bike Regulation**: Speed limits, infrastructure upgrades, helmet enforcement
3. **Infrastructure Investment**: Separated facilities for different vehicle classes
4. **Data-Driven Enforcement**: Focus resources on highest-risk categories

### Positive Trends
1. **Bicycle Infrastructure**: Risk per ride improving despite ridership growth (38.3→20.5 casualties/million rides)
2. **E-Scooter Stabilization**: Safety rates stabilizing as market matures
3. **Overall Awareness**: Recent years show some improvement in casualty rates

## Usage Instructions

### Quick Start
```bash
# Clone/download repository
# Download collision data CSV from NYC Open Data
# Place CSV file as Motor_Vehicle_Collisions_-_Crashes_20250824.csv

# Set up environment
python3 -m venv venv
source venv/bin/activate
pip install pandas matplotlib seaborn numpy

# Run main analysis
python pedestrian_analysis_consolidated.py

# Run temporal trends
python yearly_trends_analysis.py

# Run micromobility analysis
python bike_vs_ebike_analysis.py

# Run risk-adjusted analysis
python casualty_rate_analysis.py
```

### Generated Files
All analysis scripts generate both visualizations and console reports with detailed statistics.

## Future Enhancements

- **Geographic Analysis**: Borough and intersection-level risk mapping
- **Temporal Granularity**: Time of day and seasonal pattern analysis
- **Severity Analysis**: Injury severity beyond simple injury/death classification
- **Demographics**: Operator and pedestrian age/demographic correlations
- **Infrastructure Correlation**: Casualties mapped to bike lane types and traffic calming
- **Real-time Integration**: Live data feeds for dynamic safety monitoring
- **Economic Impact**: Cost analysis of casualties by vehicle type

---

*Analysis conducted using NYC Open Data through August 2024. Vehicle collision data accuracy depends on police report completeness and consistency. 2025 projections based on partial year data and may vary from actual outcomes.*

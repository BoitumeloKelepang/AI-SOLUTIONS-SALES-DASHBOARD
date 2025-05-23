import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import uuid

# Define parameters for synthetic data
countries = ['UK', 'USA', 'Germany', 'France', 'India', 'China', 'Japan', 'Brazil']
# Map countries to their respective continents
country_to_continent = {
    'UK': 'Europe',
    'USA': 'North America',
    'Germany': 'Europe',
    'France': 'Europe',
    'India': 'Asia',
    'China': 'Asia',
    'Japan': 'Asia',
    'Brazil': 'South America'
}
regions = ['Europe', 'North America', 'Asia', 'South America']
job_types = ['Software Dev', 'AI Consulting', 'Prototyping', 'Support']
actions = ['Demo', 'AI Assistant', 'Promo Event', 'General Inquiry']
products = ['AI Suite', 'Cloud Platform', 'Analytics Tool', 'Automation Bot']
sales_stages = ['Lead', 'Opportunity', 'Closed']
customer_types = ['New', 'Returning']
user_agents = ['Chrome', 'Firefox', 'Safari', 'Edge']
start_date = datetime(2022, 1, 1)
end_date = datetime(2025, 5, 21)
num_records = 80000
team_members = ['Alice Smith', 'Bob Jones', 'Clara Lee', 'David Kim']
years = [2022, 2023, 2024, 2025]

# Generate reduced target sums for each year
# 2023 and 2024 are underperforming/loss years for revenue, 2022 has very low sales volume
target_revenue_by_year = {
    2022: random.randint(500000, 9999999),  # Reduced to 5-7 digits, profitable
    2023: 100000,  # Loss year
    2024: 200000,  # Underperforming year
    2025: random.randint(500000, 9999999)   # Reduced to 5-7 digits, profitable
}
target_sales_volume_by_year = {
    2022: 10000,  # Very low sales volume
    2023: random.randint(50000, 9999999),
    2024: random.randint(50000, 9999999),
    2025: random.randint(50000, 9999999)
}

# Generate synthetic data
def generate_data():
    data = {
        'timestamp': [],
        'year': [],
        'revenue': [],
        'Sales_Volume': [],
        'member_id': [],
        'product_name': [],
        'country': [],
        'job_type': [],
        'action': [],
        'User_Agent': [],
        'Customer_Age': [],
        'sales_stage': [],
        'customer_type': [],
        'Target_Sales': [],
        'Target_Revenue': [],
        'Target_Product_Revenue': [],
        'Target_Member_Revenue': [],
        'Target_Member_Sales': [],
        'Target_Member_Activities': [],
        'Target_Team_Revenue': [],
        'Target_Team_Activities': []
    }
    
    # Estimate records per year (assuming even distribution)
    records_per_year = num_records // len(years)
    
    for year in years:
        # Calculate base per-record values to meet the target sums (in base units)
        base_revenue = target_revenue_by_year[year] / records_per_year
        base_sales_volume = target_sales_volume_by_year[year] / records_per_year
        
        for _ in range(records_per_year):
            data['timestamp'].append(start_date + timedelta(days=random.randint(0, (end_date - start_date).days)))
            data['year'].append(year)
            # Add controlled variation to per-record values (in base units)
            revenue = base_revenue * random.uniform(0.95, 1.05)  # ±5% variation
            sales_volume = int(base_sales_volume * random.uniform(0.95, 1.05))  # ±5% variation
            data['revenue'].append(revenue)
            data['Sales_Volume'].append(sales_volume)
            data['member_id'].append(random.choice(team_members))
            data['product_name'].append(random.choice(products))
            data['country'].append(random.choice(countries))
            data['job_type'].append(random.choice(job_types))
            data['action'].append(random.choice(actions))
            data['User_Agent'].append(random.choice(user_agents))
            data['Customer_Age'].append(random.randint(18, 65))
            
            # Skew sales stage distribution for 2022 to have very low conversion
            if year == 2022:
                # 95% Leads, 4% Opportunity, 1% Closed
                rand = random.random()
                if rand < 0.95:
                    stage = 'Lead'
                elif rand < 0.99:
                    stage = 'Opportunity'
                else:
                    stage = 'Closed'
            else:
                # Normal distribution for other years
                stage = random.choice(sales_stages)
            data['sales_stage'].append(stage)
            
            data['customer_type'].append(random.choice(customer_types))
            data['Target_Sales'].append(random.randint(50, 200))
            data['Target_Revenue'].append(random.uniform(5000, 15000))
            data['Target_Product_Revenue'].append(random.uniform(2000, 8000))
            data['Target_Member_Revenue'].append(random.uniform(3000, 12000))
            data['Target_Member_Sales'].append(random.randint(20, 100))
            data['Target_Member_Activities'].append(random.randint(50, 200))
            data['Target_Team_Revenue'].append(random.uniform(10000, 50000))
            data['Target_Team_Activities'].append(random.randint(100, 500))
    
    df = pd.DataFrame(data)
    # Assign region based on country
    df['region'] = df['country'].map(country_to_continent)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Compute aggregated metrics
    df['Total_Revenue'] = df.groupby('year')['revenue'].transform('sum')
    df['Total_Sales_Volume'] = df.groupby('year')['Sales_Volume'].transform('sum')
    
    # Adjust to ensure exact target sums (due to rounding errors from randomization)
    for year in years:
        year_mask = df['year'] == year
        current_revenue_sum = df.loc[year_mask, 'revenue'].sum()
        current_sales_volume_sum = df.loc[year_mask, 'Sales_Volume'].sum()
        
        # Scale to match exact target
        if current_revenue_sum != 0:  # Avoid division by zero
            revenue_scale = target_revenue_by_year[year] / current_revenue_sum
            df.loc[year_mask, 'revenue'] *= revenue_scale
            df.loc[year_mask, 'Total_Revenue'] = target_revenue_by_year[year]
        
        if current_sales_volume_sum != 0:  # Avoid division by zero
            sales_volume_scale = target_sales_volume_by_year[year] / current_sales_volume_sum
            df.loc[year_mask, 'Sales_Volume'] *= sales_volume_scale
            df.loc[year_mask, 'Total_Sales_Volume'] = target_sales_volume_by_year[year]
    
    # Recalculate other dependent metrics after scaling
    df['Member_Revenue'] = df.groupby(['member_id', 'year'])['revenue'].transform('sum')
    df['Member_Sales_Volume'] = df.groupby(['member_id', 'year'])['Sales_Volume'].transform('sum')
    df['Sales_Volume_By_Country'] = df.groupby(['year', 'country'])['Sales_Volume'].transform('sum')
    df['Total_Activities'] = df.groupby('year')['action'].transform('count')
    df['Member_Activities'] = df.groupby(['member_id', 'year'])['action'].transform('count')
    df['Member_Target_Achieved'] = df['Member_Revenue'] >= df['Target_Member_Revenue']
    df['Team_Target_Achieved'] = df['Total_Revenue'] >= df['Target_Team_Revenue']
    
    # Save to CSV
    df.to_csv('Cleaned_Web_Logs.csv', index=False)
    return df

if __name__ == "__main__":
    df = generate_data()
    print(f"Generated and saved data to 'Cleaned_Web_Logs.csv' with {len(df)} entries")
    job_type_counts = df['job_type'].value_counts()
    stats = {'mean': job_type_counts.mean(), 'std': job_type_counts.std()}
    print(f"Job Type Stats - Mean: {stats['mean']:.2f}, Std: {stats['std']:.2f}")
    # Print yearly totals for verification
    yearly_revenue = df.groupby('year')['Total_Revenue'].first()
    yearly_sales_volume = df.groupby('year')['Total_Sales_Volume'].first()
    print("\nYearly Total Revenue:")
    for year, revenue in yearly_revenue.items():
        print(f"{year}: ${revenue:,.0f}")
    print("\nYearly Total Sales Volume:")
    for year, volume in yearly_sales_volume.items():
        print(f"{year}: {volume:,.0f}")
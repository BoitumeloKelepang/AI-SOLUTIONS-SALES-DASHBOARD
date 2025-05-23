import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
import numpy as np
import uuid
from datetime import datetime

# Page config
st.set_page_config(page_title="Sales Performance Dashboard", layout="wide")

# Function to convert Plotly figure to image for PDF
def fig_to_image(fig):
    img_bytes = fig.to_image(format="png")
    return ImageReader(BytesIO(img_bytes))

# Function to create PDF from figures
def create_pdf(figures, filename):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    y_position = height - 50
    for fig in figures:
        img = fig_to_image(fig)
        img_width, img_height = img.getSize()
        aspect = img_height / img_width
        target_width = width - 100
        target_height = target_width * aspect
        if y_position - target_height < 50:
            c.showPage()
            y_position = height - 50
        c.drawImage(img, 50, y_position - target_height, width=target_width, height=target_height)
        y_position -= target_height + 20
    c.save()
    buffer.seek(0)
    return buffer

# Load data with error handling
@st.cache_data
def load_data():
    required_columns = ['timestamp', 'year', 'revenue', 'Sales_Volume', 'member_id', 'product_name', 'country', 'region',
                       'job_type', 'action', 'User_Agent', 'Customer_Age', 'sales_stage', 'customer_type',
                       'Target_Sales', 'Target_Revenue', 'Target_Product_Revenue', 'Target_Member_Revenue',
                       'Target_Member_Sales', 'Target_Member_Activities', 'Target_Team_Revenue', 'Target_Team_Activities']
    try:
        df = pd.read_csv("Cleaned_Web_Logs.csv")
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        if not all(col in df.columns for col in required_columns):
            missing = [col for col in required_columns if col not in df.columns]
            st.error(f"Missing columns in CSV: {', '.join(missing)}. Please update data.py.")
            return pd.DataFrame()
        return df
    except FileNotFoundError:
        st.error("Cleaned_Web_Logs.csv not found. Please run data.py first.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading CSV: {str(e)}")
        return pd.DataFrame()

df = load_data()
if df.empty:
    st.stop()

# Sidebar filters
st.sidebar.header("Filters")
years = sorted(df['year'].unique())
selected_years = st.sidebar.multiselect("Select Year(s)", years, default=years)
members = sorted(df['member_id'].unique())
selected_members = st.sidebar.multiselect("Select Team Member(s)", members, default=members)
products = sorted(df['product_name'].unique())
selected_products = st.sidebar.multiselect("Select Product(s)", products, default=products)
countries = sorted(df['country'].unique())
selected_countries = st.sidebar.multiselect("Select Country(ies)", countries, default=countries)
regions = sorted(df['region'].unique())
selected_regions = st.sidebar.multiselect("Select Region(s)", regions, default=regions)
job_types = sorted(df['job_type'].unique())
selected_job_types = st.sidebar.multiselect("Select Job Type(s)", job_types, default=job_types)
actions = sorted(df['action'].unique())
selected_actions = st.sidebar.multiselect("Select Action(s)", actions, default=actions)
user_agents = sorted(df['User_Agent'].unique())
selected_user_agents = st.sidebar.multiselect("Select User Agent(s)", user_agents, default=user_agents)
sales_stages = sorted(df['sales_stage'].unique())
selected_sales_stages = st.sidebar.multiselect("Select Sales Stage(s)", sales_stages, default=sales_stages)
customer_types = sorted(df['customer_type'].unique())
selected_customer_types = st.sidebar.multiselect("Select Customer Type(s)", customer_types, default=customer_types)
time_granularity = st.sidebar.selectbox("Time Granularity", ["Yearly", "Quarterly", "Monthly"], index=0)

# Smart date range filter
# Determine the min and max dates based on selected years
if selected_years:
    min_date = df[df['year'].isin(selected_years)]['timestamp'].min().date()
    max_date = df[df['year'].isin(selected_years)]['timestamp'].max().date()
else:
    min_date = df['timestamp'].min().date()
    max_date = df['timestamp'].max().date()

# Default to the full range of available dates
default_start = min_date
default_end = max_date
date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(default_start, default_end),
    min_value=min_date,
    max_value=max_date,
    format="YYYY-MM-DD"
)

# Handle the date range input (can be a single date or a tuple of start/end dates)
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date = end_date = date_range if isinstance(date_range, datetime.date) else default_start

# Filter data
filtered_df = df[
    (df['year'].isin(selected_years)) &
    (df['member_id'].isin(selected_members)) &
    (df['product_name'].isin(selected_products)) &
    (df['country'].isin(selected_countries)) &
    (df['region'].isin(selected_regions)) &
    (df['job_type'].isin(selected_job_types)) &
    (df['action'].isin(selected_actions)) &
    (df['User_Agent'].isin(selected_user_agents)) &
    (df['sales_stage'].isin(selected_sales_stages)) &
    (df['customer_type'].isin(selected_customer_types)) &
    (df['timestamp'].dt.date >= start_date) &
    (df['timestamp'].dt.date <= end_date)
]

# Scale down values by dividing by 1,000,000 to remove last 6 zeros
filtered_df['revenue'] = filtered_df['revenue'] / 1000000
filtered_df['Total_Revenue'] = filtered_df['Total_Revenue'] / 1000000
filtered_df['Target_Revenue'] = filtered_df['Target_Revenue'] / 1000000
filtered_df['Target_Product_Revenue'] = filtered_df['Target_Product_Revenue'] / 1000000
filtered_df['Target_Member_Revenue'] = filtered_df['Target_Member_Revenue'] / 1000000
filtered_df['Target_Team_Revenue'] = filtered_df['Target_Team_Revenue'] / 1000000
filtered_df['Member_Revenue'] = filtered_df['Member_Revenue'] / 1000000
filtered_df['Sales_Volume'] = filtered_df['Sales_Volume'] / 1000000
filtered_df['Total_Sales_Volume'] = filtered_df['Total_Sales_Volume'] / 1000000
filtered_df['Target_Sales'] = filtered_df['Target_Sales'] / 1000000
filtered_df['Target_Member_Sales'] = filtered_df['Target_Member_Sales'] / 1000000
filtered_df['Member_Sales_Volume'] = filtered_df['Member_Sales_Volume'] / 1000000
filtered_df['Sales_Volume_By_Country'] = filtered_df['Sales_Volume_By_Country'] / 1000000

# Title
st.markdown("""
<div style="text-align: center; padding: 10px;">
    <h1 style="color: #003366; font-size: 1.8em; font-family: Arial, sans-serif; margin: 0;">
        AI SOLUTIONS SALES DASHBOARD
    </h1>
</div>
""", unsafe_allow_html=True)

# CSS for KPI borders
st.markdown("""
<style>
    .stMetric {
        border: 2px solid #003366;
        padding: 10px;
        border-radius: 5px;
        margin: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Tabs
tabs = st.tabs(["Revenue", "Sales", "Products", "Customers", "Team Members", "Whole Team"])

# Revenue Tab
with tabs[0]:
    st.header("Revenue Analysis")
    
    # KPIs
    st.subheader("Key Performance Indicators")
    kpi1, kpi2, kpi3 = st.columns(3)
    total_revenue = filtered_df['Total_Revenue'].sum()
    kpi1.metric(label="Total Revenue", value=f"${total_revenue:,.2f}K")
    revenue_by_year = filtered_df.groupby('year')['Total_Revenue'].sum().reset_index()
    revenue_growth = ((revenue_by_year['Total_Revenue'].iloc[-1] / revenue_by_year['Total_Revenue'].iloc[0]) - 1) * 100 if len(selected_years) > 1 else 0
    kpi2.metric(label="Revenue Growth Rate", value=f"{revenue_growth:.2f}%" if len(selected_years) > 1 else "N/A", help="Select multiple years to calculate growth rate")
    top_product = filtered_df.groupby('product_name')['revenue'].sum().idxmax()
    kpi3.metric(label="Top Selling Product", value=top_product)
    
    # Graphs
    col1, col2, col3 = st.columns(3)
    with col1:
        revenue_data = filtered_df.groupby('year').agg({'Total_Revenue': 'sum', 'Target_Revenue': 'mean'}).reset_index()
        fig1 = go.Figure()
        fig1.add_trace(go.Bar(x=revenue_data['year'], y=revenue_data['Total_Revenue'], name='Actual Revenue', marker_color='royalblue'))
        fig1.add_trace(go.Scatter(x=revenue_data['year'], y=revenue_data['Target_Revenue'], name='Target Revenue', mode='lines', line_color='darkorange'))
        fig1.update_layout(title="Actual vs Target Revenue", xaxis_title="Year", yaxis_title="Revenue ($K)", height=250, margin=dict(l=10, r=10, t=30, b=10), template='plotly_white', legend=dict(font=dict(size=10)))
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        revenue_trend = filtered_df.groupby('year')['revenue'].sum().reset_index()
        fig3 = px.line(revenue_trend, x='year', y='revenue', title="Revenue Trend Over Years")
        fig3.update_traces(line_color='green')
        fig3.update_layout(height=250, margin=dict(l=10, r=10, t=30, b=10), template='plotly_white', legend=dict(font=dict(size=10)))
        st.plotly_chart(fig3, use_container_width=True)
    
    with col3:
        # Redefine Target Achievement Rate using aggregated values
        revenue_agg = filtered_df.groupby('year').agg({'Total_Revenue': 'sum', 'Target_Team_Revenue': 'sum'}).reset_index()
        revenue_agg['Achievement_Rate'] = (revenue_agg['Total_Revenue'] / revenue_agg['Target_Team_Revenue']) * 100
        achievement_rate = revenue_agg['Achievement_Rate'].mean() if not revenue_agg.empty else 0
        
        # Cap the achievement rate at 150% for gauge display
        gauge_value = min(achievement_rate, 150)
        
        # Calculate year-over-year change in achievement rate
        if len(revenue_agg) > 1:
            delta_value = revenue_agg['Achievement_Rate'].iloc[-1] - revenue_agg['Achievement_Rate'].iloc[-2]
            delta = {'reference': delta_value, 'increasing': {'symbol': '▲'}, 'decreasing': {'symbol': '▼'}}
        else:
            delta = None
        
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta" if delta else "gauge+number",
            value=gauge_value,
            title={'text': "Target Achievement Rate", 'font': {'size': 12}},
            delta=delta,
            gauge={
                'axis': {'range': [0, 150], 'tickmode': 'array', 'tickvals': [0, 50, 100, 150], 'ticktext': ['0%', '50%', '100%', '150%'], 'tickwidth': 1, 'tickcolor': "black"},
                'bar': {'color': "royalblue"},
                'steps': [{'range': [0, 50], 'color': "red"}, {'range': [50, 100], 'color': "yellow"}, {'range': [100, 150], 'color': "green"}],
                'threshold': {'line': {'color': "black", 'width': 4}, 'thickness': 0.75, 'value': gauge_value}
            }
        ))
        fig_gauge.update_layout(height=250, margin=dict(l=10, r=10, t=30, b=10), template='plotly_white')
        st.plotly_chart(fig_gauge, use_container_width=True)
    
    # Download buttons
    col4, col5 = st.columns(2)
    with col4:
        pdf_buffer = create_pdf([fig1, fig3, fig_gauge], "revenue.pdf")
        st.download_button(label="Download PDF", data=pdf_buffer, file_name="revenue.pdf", mime="application/pdf")
    with col5:
        csv_buffer = BytesIO()
        revenue_data.to_csv(csv_buffer, index=False)
        revenue_trend.to_csv(csv_buffer, index=False)
        kpi_data = pd.DataFrame({
            'KPI': ['Total Revenue', 'Revenue Growth Rate', 'Top Selling Product', 'Target Achievement Rate'],
            'Value': [total_revenue, revenue_growth if len(selected_years) > 1 else 'N/A', top_product, achievement_rate]
        })
        kpi_data.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)
        st.download_button(label="Download CSV", data=csv_buffer, file_name="revenue_data.csv", mime="text/csv")

# Sales Tab
with tabs[1]:
    st.header("Sales Analysis")
    
    # KPIs
    st.subheader("Key Performance Indicators")
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    total_sales_volume = filtered_df['Total_Sales_Volume'].sum()
    kpi1.metric(label="Total Sales Volume", value=f"{total_sales_volume:,.0f}K")
    achievement_rate = (filtered_df.groupby('year')['Team_Target_Achieved'].mean().mean() * 100) if not filtered_df.empty else 0
    kpi2.metric(label="Target Achievement Rate", value=f"{achievement_rate:.2f}%")
    top_product_sales = filtered_df.groupby('product_name')['Sales_Volume'].sum().idxmax()
    kpi3.metric(label="Top Selling Product", value=top_product_sales)
    funnel_data = filtered_df.groupby(['year', 'sales_stage']).size().reset_index(name='count')
    funnel_data = funnel_data[funnel_data['sales_stage'].isin(['Lead', 'Opportunity', 'Closed'])].sort_values(
        by='sales_stage', key=lambda x: x.map({'Lead': 1, 'Opportunity': 2, 'Closed': 3})
    )
    total_inquiries = funnel_data[funnel_data['sales_stage'] == 'Lead']['count'].sum()
    kpi4.metric(label="Total Inquiries", value=f"{total_inquiries:,.0f}")
    
    # Graphs
    col1, col2, col3 = st.columns(3)
    with col1:
        sales_data = filtered_df.groupby('year').agg({'Total_Sales_Volume': 'sum', 'Target_Sales': 'sum'}).reset_index()
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(x=sales_data['year'], y=sales_data['Total_Sales_Volume'], name='Actual Sales Volume', marker_color='royalblue'))
        fig2.add_trace(go.Scatter(x=sales_data['year'], y=sales_data['Target_Sales'], name='Target Sales', mode='lines', line_color='darkorange'))
        fig2.update_layout(title="Actual vs Target Sales Volume", xaxis_title="Year", yaxis_title="Sales Volume (K)", height=250, margin=dict(l=10, r=10, t=30, b=10), template='plotly_white', legend=dict(font=dict(size=10)))
        st.plotly_chart(fig2, use_container_width=True)
    
    with col2:
        fig_funnel = px.funnel(funnel_data, x='count', y='sales_stage', color='year', title="Sales Funnel by Year")
        fig_funnel.update_layout(height=250, margin=dict(l=10, r=10, t=30, b=10), template='plotly_white', legend=dict(font=dict(size=10)))
        st.plotly_chart(fig_funnel, use_container_width=True)
    
    with col3:
        sales_trend = filtered_df.groupby('year')['Sales_Volume'].sum().reset_index()
        fig_sales_trend = px.line(sales_trend, x='year', y='Sales_Volume', title="Sales Trend by Year")
        fig_sales_trend.update_traces(line_color='green')
        fig_sales_trend.update_layout(height=250, margin=dict(l=10, r=10, t=30, b=10), template='plotly_white', legend=dict(font=dict(size=10)))
        st.plotly_chart(fig_sales_trend, use_container_width=True)
    
    # Sales Funnel Success Gauge with Delta
    st.subheader("Sales Funnel Success")
    available_years = sorted(funnel_data['year'].unique())
    selected_gauge_year = st.selectbox("Select Year for Funnel Success Gauge", available_years, key="gauge_year_sales")
    funnel_data_year = funnel_data[funnel_data['year'] == selected_gauge_year]
    leads_count = funnel_data_year[funnel_data_year['sales_stage'] == 'Lead']['count'].iloc[0] if not funnel_data_year[funnel_data_year['sales_stage'] == 'Lead'].empty else 0
    closed_count = funnel_data_year[funnel_data_year['sales_stage'] == 'Closed']['count'].iloc[0] if not funnel_data_year[funnel_data_year['sales_stage'] == 'Closed'].empty else 0
    conversion_rate = (closed_count / leads_count * 100) if leads_count > 0 else 0
    
    # Calculate year-over-year change in conversion rate
    conversion_rates = {}
    for year in available_years:
        year_data = funnel_data[funnel_data['year'] == year]
        year_leads = year_data[year_data['sales_stage'] == 'Lead']['count'].iloc[0] if not year_data[year_data['sales_stage'] == 'Lead'].empty else 0
        year_closed = year_data[year_data['sales_stage'] == 'Closed']['count'].iloc[0] if not year_data[year_data['sales_stage'] == 'Closed'].empty else 0
        conversion_rates[year] = (year_closed / year_leads * 100) if year_leads > 0 else 0
    
    # Find the previous year's conversion rate
    previous_year = selected_gauge_year - 1 if selected_gauge_year > min(available_years) else None
    delta = None
    if previous_year and previous_year in conversion_rates:
        delta_value = conversion_rates[selected_gauge_year] - conversion_rates[previous_year]
        delta = {'reference': delta_value, 'increasing': {'symbol': '▲'}, 'decreasing': {'symbol': '▼'}}
    
    fig_success_gauge = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=conversion_rate,
        title={'text': f"Funnel Conversion Success ({selected_gauge_year})", 'font': {'size': 12}},
        delta=delta,
        gauge={
            'axis': {'range': [0, 100], 'tickmode': 'array', 'tickvals': [0, 30, 60, 100], 'ticktext': ['Low', 'Moderate', 'High'], 'tickwidth': 1, 'tickcolor': "black"},
            'bar': {'color': "rgba(0,0,0,0)"},
            'steps': [{'range': [0, 30], 'color': "red"}, {'range': [30, 60], 'color': "yellow"}, {'range': [60, 100], 'color': "green"}],
            'threshold': {'line': {'color': "black", 'width': 4}, 'thickness': 0.75, 'value': conversion_rate}
        }
    ))
    fig_success_gauge.update_layout(height=250, margin=dict(l=10, r=10, t=30, b=10), template='plotly_white')
    st.plotly_chart(fig_success_gauge, use_container_width=True)
    
    # Download buttons
    col4, col5 = st.columns(2)
    with col4:
        pdf_buffer = create_pdf([fig2, fig_funnel, fig_sales_trend, fig_success_gauge], "sales.pdf")
        st.download_button(label="Download PDF", data=pdf_buffer, file_name="sales.pdf", mime="application/pdf")
    with col5:
        csv_buffer = BytesIO()
        sales_data.to_csv(csv_buffer, index=False)
        funnel_data.to_csv(csv_buffer, index=False)
        sales_trend.to_csv(csv_buffer, index=False)
        kpi_data = pd.DataFrame({
            'KPI': ['Total Sales Volume', 'Target Achievement Rate', 'Top Selling Product', 'Total Inquiries', 'Funnel Conversion Rate'],
            'Value': [total_sales_volume, achievement_rate, top_product_sales, total_inquiries, conversion_rate]
        })
        kpi_data.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)
        st.download_button(label="Download CSV", data=csv_buffer, file_name="sales_data.csv", mime="text/csv")

# Products Tab
with tabs[2]:
    st.header("Products Analysis")
    
    # KPIs
    st.subheader("Key Performance Indicators")
    kpi1, kpi2 = st.columns(2)
    total_product_revenue = filtered_df['revenue'].sum()
    kpi1.metric(label="Total Product Revenue", value=f"${total_product_revenue:,.2f}K")
    most_purchased_product = filtered_df.groupby('product_name')['Sales_Volume'].sum().idxmax()
    kpi2.metric(label="Most Purchased Product", value=most_purchased_product)
    
    # Graphs
    col1, col2 = st.columns(2)
    with col1:
        product_revenue = filtered_df.groupby('product_name').agg({'revenue': 'sum'}).reset_index().sort_values('revenue', ascending=False)
        fig_product_revenue = px.bar(product_revenue, x='product_name', y='revenue', title="Revenue by Product", color='product_name', color_discrete_sequence=px.colors.qualitative.Bold)
        fig_product_revenue.update_layout(height=250, margin=dict(l=10, r=10, t=30, b=10), template='plotly_white', legend=dict(font=dict(size=10)))
        st.plotly_chart(fig_product_revenue, use_container_width=True)
    
    with col2:
        product_sales = filtered_df.groupby('product_name').agg({'Sales_Volume': 'sum'}).reset_index().sort_values('Sales_Volume', ascending=False)
        fig_product_sales = px.bar(product_sales, x='product_name', y='Sales_Volume', title="Sales Volume by Product", color='product_name', color_discrete_sequence=px.colors.qualitative.Pastel)
        fig_product_sales.update_layout(height=250, margin=dict(l=10, r=10, t=30, b=10), template='plotly_white', legend=dict(font=dict(size=10)))
        st.plotly_chart(fig_product_sales, use_container_width=True)
    
    # Download buttons
    col3, col4 = st.columns(2)
    with col3:
        pdf_buffer = create_pdf([fig_product_revenue, fig_product_sales], "products.pdf")
        st.download_button(label="Download PDF", data=pdf_buffer, file_name="products.pdf", mime="application/pdf")
    with col4:
        csv_buffer = BytesIO()
        product_revenue.to_csv(csv_buffer, index=False)
        product_sales.to_csv(csv_buffer, index=False)
        kpi_data = pd.DataFrame({
            'KPI': ['Total Product Revenue', 'Most Purchased Product'],
            'Value': [total_product_revenue, most_purchased_product]
        })
        kpi_data.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)
        st.download_button(label="Download CSV", data=csv_buffer, file_name="products_data.csv", mime="text/csv")

# Customers Tab
with tabs[3]:
    st.header("Customer Analysis")
    
    # KPIs
    st.subheader("Key Performance Indicators")
    kpi1, kpi2 = st.columns(2)
    total_customers = filtered_df['customer_type'].count()
    kpi1.metric(label="Total Customers", value=f"{total_customers:,.0f}")
    returning_customers = filtered_df[filtered_df['customer_type'] == 'Returning']['customer_type'].count()
    kpi2.metric(label="Returning Customers", value=f"{returning_customers:,.0f}")
    
    # Customer Distribution by Country
    st.subheader("Customer Distribution by Country")
    customer_dist = filtered_df.groupby('country')['customer_type'].count().reset_index(name='Customer_Count')
    st.table(customer_dist)
    
    # Graphs
    col1, col2, col3 = st.columns(3)
    with col1:
        country_sales = filtered_df.groupby('country').agg({'Sales_Volume_By_Country': 'sum'}).reset_index()
        fig4 = px.pie(country_sales, values='Sales_Volume_By_Country', names='country', title="Sales Volume by Country", color_discrete_sequence=px.colors.qualitative.Set3)
        fig4.update_layout(height=250, margin=dict(l=10, r=10, t=30, b=10), template='plotly_white', legend=dict(font=dict(size=10)))
        st.plotly_chart(fig4, use_container_width=True)
    
    with col2:
        customer_type_trend = filtered_df.groupby(['year', 'customer_type']).size().reset_index(name='count')
        fig_customer_trend = px.line(customer_type_trend, x='year', y='count', color='customer_type', title="New vs Returning Customers per Year", color_discrete_sequence=px.colors.qualitative.Dark2)
        fig_customer_trend.update_layout(height=250, margin=dict(l=10, r=10, t=30, b=10), template='plotly_white', legend=dict(font=dict(size=10)))
        st.plotly_chart(fig_customer_trend, use_container_width=True)
    
    with col3:
        age_bins = pd.cut(filtered_df['Customer_Age'], bins=[18, 25, 35, 45, 55, 65], labels=['18-25', '26-35', '36-45', '46-55', '56-65'])
        age_counts = age_bins.value_counts().sort_index().reset_index()
        age_counts.columns = ['Age Group', 'Count']
        fig5 = px.bar(age_counts, x='Age Group', y='Count', title="Customer Age Distribution", color='Age Group', color_discrete_sequence=px.colors.qualitative.Pastel)
        fig5.update_layout(height=250, margin=dict(l=10, r=10, t=30, b=10), template='plotly_white', legend=dict(font=dict(size=10)))
        st.plotly_chart(fig5, use_container_width=True)
    
    # Download buttons
    col4, col5 = st.columns(2)
    with col4:
        pdf_buffer = create_pdf([fig4, fig_customer_trend, fig5], "customers.pdf")
        st.download_button(label="Download PDF", data=pdf_buffer, file_name="customers.pdf", mime="application/pdf")
    with col5:
        csv_buffer = BytesIO()
        country_sales.to_csv(csv_buffer, index=False)
        customer_type_trend.to_csv(csv_buffer, index=False)
        age_counts.to_csv(csv_buffer, index=False)
        kpi_data = pd.DataFrame({
            'KPI': ['Total Customers', 'Returning Customers'],
            'Value': [total_customers, returning_customers]
        })
        kpi_data.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)
        st.download_button(label="Download CSV", data=csv_buffer, file_name="customers_data.csv", mime="text/csv")

# Team Members Tab
with tabs[4]:
    st.header("Team Member Performance")
    
    # KPIs
    st.subheader("Key Performance Indicators")
    kpi1, kpi2 = st.columns(2)
    total_member_revenue = filtered_df['Member_Revenue'].sum()
    kpi1.metric(label="Total Member Revenue", value=f"${total_member_revenue:,.2f}K")
    best_member = filtered_df.groupby('member_id')['Member_Revenue'].sum().idxmax()
    kpi2.metric(label="Best Performing Member", value=best_member)
    
    # Graphs
    col1, col2 = st.columns(2)
    with col1:
        member_data = filtered_df.groupby('member_id').agg({'Member_Revenue': 'sum', 'Target_Member_Revenue': 'mean'}).reset_index()
        fig7 = go.Figure()
        fig7.add_trace(go.Bar(x=member_data['member_id'], y=member_data['Member_Revenue'], name='Member Revenue', marker_color='royalblue'))
        fig7.add_trace(go.Scatter(x=member_data['member_id'], y=member_data['Target_Member_Revenue'], name='Target Revenue', mode='lines', line_color='darkorange'))
        fig7.update_layout(title="Individual Revenue vs Target", xaxis_title="Member ID", yaxis_title="Revenue ($K)", height=250, margin=dict(l=10, r=10, t=30, b=10), template='plotly_white', legend=dict(font=dict(size=10)))
        st.plotly_chart(fig7, use_container_width=True)
    
    with col2:
        member_sales = filtered_df.groupby('member_id').agg({'Member_Sales_Volume': 'sum', 'Target_Member_Sales': 'mean'}).reset_index()
        fig_member_sales = px.bar(member_sales, x='member_id', y='Member_Sales_Volume', title="Member Sales Volume", color='member_id', color_discrete_sequence=px.colors.qualitative.Set1)
        fig_member_sales.update_layout(height=250, margin=dict(l=10, r=10, t=30, b=10), template='plotly_white', legend=dict(font=dict(size=10)))
        st.plotly_chart(fig_member_sales, use_container_width=True)
    
    # Download buttons
    col3, col4 = st.columns(2)
    with col3:
        pdf_buffer = create_pdf([fig7, fig_member_sales], "team_members.pdf")
        st.download_button(label="Download PDF", data=pdf_buffer, file_name="team_members.pdf", mime="application/pdf")
    with col4:
        csv_buffer = BytesIO()
        member_data.to_csv(csv_buffer, index=False)
        member_sales.to_csv(csv_buffer, index=False)
        kpi_data = pd.DataFrame({
            'KPI': ['Total Member Revenue', 'Best Performing Member'],
            'Value': [total_member_revenue, best_member]
        })
        kpi_data.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)
        st.download_button(label="Download CSV", data=csv_buffer, file_name="team_members_data.csv", mime="text/csv")

# Whole Team Tab
with tabs[5]:
    st.header("Whole Team Performance")
    
    # KPIs
    st.subheader("Key Performance Indicators")
    kpi1, kpi2 = st.columns(2)
    total_team_revenue = filtered_df['Total_Revenue'].sum()
    kpi1.metric(label="Total Team Revenue", value=f"${total_team_revenue:,.2f}K")
    total_activities = filtered_df['Total_Activities'].sum()
    kpi2.metric(label="Total Activities", value=f"{total_activities:,.0f}")
    
    # Graphs
    col1, col2, col3 = st.columns(3)
    with col1:
        team_data = filtered_df.groupby('year').agg({'Total_Revenue': 'mean', 'Target_Team_Revenue': 'mean'}).reset_index()
        fig8 = go.Figure()
        fig8.add_trace(go.Bar(x=team_data['year'], y=team_data['Total_Revenue'], name='Team Revenue', marker_color='royalblue'))
        fig8.add_trace(go.Scatter(x=team_data['year'], y=team_data['Target_Team_Revenue'], name='Target Revenue', mode='lines', line_color='darkorange'))
        fig8.update_layout(title="Team Revenue vs Target", xaxis_title="Year", yaxis_title="Revenue ($K)", height=250, margin=dict(l=10, r=10, t=30, b=10), template='plotly_white', legend=dict(font=dict(size=10)))
        st.plotly_chart(fig8, use_container_width=True)
    
    with col2:
        period = {'Yearly': 'Y', 'Quarterly': 'Q', 'Monthly': 'M'}[time_granularity]
        sales_trend = filtered_df.groupby(filtered_df['timestamp'].dt.to_period(period)).agg({'Sales_Volume': 'sum'}).reset_index()
        sales_trend['timestamp'] = sales_trend['timestamp'].dt.to_timestamp()
        fig9 = px.line(sales_trend, x='timestamp', y='Sales_Volume', title="Team Sales Volume Trend")
        fig9.update_traces(line_color='green')
        fig9.update_layout(height=250, margin=dict(l=10, r=10, t=30, b=10), template='plotly_white', legend=dict(font=dict(size=10)))
        st.plotly_chart(fig9, use_container_width=True)
    
    with col3:
        activity_counts = filtered_df.groupby('year').agg({'Total_Activities': 'sum'}).reset_index()
        fig10 = px.bar(activity_counts, x='year', y='Total_Activities', title="Team Activities by Year", color='year', color_discrete_sequence=px.colors.qualitative.Set2)
        fig10.update_layout(height=250, margin=dict(l=10, r=10, t=30, b=10), template='plotly_white', legend=dict(font=dict(size=10)))
        st.plotly_chart(fig10, use_container_width=True)
    
    # Activity Success Gauge
    st.subheader("Activity Success Rate")
    activity_data = filtered_df.groupby('year').agg({'Total_Activities': 'sum', 'Target_Team_Activities': 'sum'}).reset_index()
    activity_data['Success_Rate'] = (activity_data['Total_Activities'] / activity_data['Target_Team_Activities']) * 100
    available_years = sorted(activity_data['year'].unique())
    selected_activity_year = st.selectbox("Select Year for Activity Success Gauge", available_years, key="gauge_year_activity")
    activity_year_data = activity_data[activity_data['year'] == selected_activity_year]
    success_rate = activity_year_data['Success_Rate'].iloc[0] if not activity_year_data.empty else 0
    
    # Calculate year-over-year change in success rate
    success_rates = activity_data.set_index('year')['Success_Rate'].to_dict()
    previous_year = selected_activity_year - 1 if selected_activity_year > min(available_years) else None
    delta = None
    if previous_year and previous_year in success_rates:
        delta_value = success_rates[selected_activity_year] - success_rates[previous_year]
        delta = {'reference': delta_value, 'increasing': {'symbol': '▲'}, 'decreasing': {'symbol': '▼'}}
    
    fig_activity_gauge = go.Figure(go.Indicator(
        mode="gauge+number+delta" if delta else "gauge+number",
        value=success_rate,
        title={'text': f"Activity Success Rate ({selected_activity_year})", 'font': {'size': 12}},
        delta=delta,
        gauge={
            'axis': {'range': [0, 150], 'tickmode': 'array', 'tickvals': [0, 50, 100, 150], 'ticktext': ['Low', 'Moderate', 'Target', 'Exceeded'], 'tickwidth': 1, 'tickcolor': "black"},
            'bar': {'color': "rgba(0,0,0,0)"},
            'steps': [{'range': [0, 50], 'color': "red"}, {'range': [50, 100], 'color': "yellow"}, {'range': [100, 150], 'color': "green"}],
            'threshold': {'line': {'color': "black", 'width': 4}, 'thickness': 0.75, 'value': success_rate}
        }
    ))
    fig_activity_gauge.update_layout(height=250, margin=dict(l=10, r=10, t=30, b=10), template='plotly_white')
    st.plotly_chart(fig_activity_gauge, use_container_width=True)
    
    # Download buttons
    col4, col5 = st.columns(2)
    with col4:
        pdf_buffer = create_pdf([fig8, fig9, fig10, fig_activity_gauge], "whole_team.pdf")
        st.download_button(label="Download PDF", data=pdf_buffer, file_name="whole_team.pdf", mime="application/pdf")
    with col5:
        csv_buffer = BytesIO()
        team_data.to_csv(csv_buffer, index=False)
        sales_trend.to_csv(csv_buffer, index=False)
        activity_counts.to_csv(csv_buffer, index=False)
        kpi_data = pd.DataFrame({
            'KPI': ['Total Team Revenue', 'Total Activities', 'Activity Success Rate'],
            'Value': [total_team_revenue, total_activities, success_rate]
        })
        kpi_data.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)
        st.download_button(label="Download CSV", data=csv_buffer, file_name="whole_team_data.csv", mime="text/csv")

# CSS to prevent scrolling
st.markdown("""
<style>
    .stApp {
        max-height: 100vh;
        overflow: hidden;
    }
    .stTabs [data-baseweb="tab-list"] {
        padding: 5px;
    }
    .stTabs [data-baseweb="tab"] {
        font-size: 0.9em;
    }
    .stMetric {
        border: 2px solid #003366;
        padding: 10px;
        border-radius: 5px;
        margin: 5px;
    }
</style>
""", unsafe_allow_html=True)
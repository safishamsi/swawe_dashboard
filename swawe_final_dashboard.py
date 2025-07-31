import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
from datetime import datetime, timedelta
import time

st.set_page_config(
    page_title="SWAWE Dashboard",
    page_icon="🔥",
    layout="wide"
)

# Get Shopify credentials
try:
    SHOPIFY_STORE_URL = st.secrets["35e5fd-d4.myshopify.com"]
    SHOPIFY_ACCESS_TOKEN = st.secrets["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"]
    shopify_connected = True
except:
    SHOPIFY_STORE_URL = ""
    SHOPIFY_ACCESS_TOKEN = ""
    shopify_connected = False

# Initialize session state
if 'sales_data' not in st.session_state:
    st.session_state.sales_data = []

# Modern CSS styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%);
        font-family: 'Inter', sans-serif;
    }
    
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    }
    
    .main-title {
        color: white;
        font-size: 3rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: 2px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .subtitle {
        color: rgba(255,255,255,0.9);
        font-size: 1rem;
        margin-top: 0.5rem;
        font-weight: 300;
    }
    
    .metric-container {
        background: linear-gradient(145deg, #1e1e3e, #2a2a4e);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 0.5rem 0;
        border: 1px solid rgba(102, 126, 234, 0.2);
        transition: all 0.3s ease;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    
    .metric-container:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(102, 126, 234, 0.4);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #667eea;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        color: rgba(255,255,255,0.8);
        font-size: 0.9rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .connected-badge {
        background: linear-gradient(135deg, #00d4aa, #00b894);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
        margin-bottom: 1rem;
    }
    
    .disconnected-badge {
        background: linear-gradient(135deg, #ff6b6b, #e55656);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
        margin-bottom: 1rem;
    }
    
    .chart-container {
        background: linear-gradient(145deg, #1a1a2e, #2a2a4e);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid rgba(102, 126, 234, 0.2);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    
    .insight-card {
        background: linear-gradient(145deg, #1e1e3e, #2e2e4e);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 4px solid #00d4aa;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 25px rgba(102, 126, 234, 0.5);
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1 class="main-title">SWAWE DASHBOARD</h1>
    <p class="subtitle">Fashion Analytics & Business Intelligence</p>
</div>
""", unsafe_allow_html=True)

# Connection status
if shopify_connected:
    st.markdown('<div class="connected-badge">Connected to Shopify Store</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="disconnected-badge">Shopify Not Connected - Add credentials in Settings → Secrets</div>', unsafe_allow_html=True)

# Navigation
page = st.sidebar.selectbox("Choose a section:", 
    ["Executive Dashboard", "Sales Analytics", "Product Intelligence", "Data Management"])

def fetch_all_orders():
    """Fetch all orders properly without duplicates"""
    if not shopify_connected:
        return []
        
    all_orders = []
    headers = {"X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN}
    
    # Get total count first
    count_url = f"https://{SHOPIFY_STORE_URL}/admin/api/2023-10/orders/count.json"
    count_response = requests.get(count_url, headers=headers)
    
    if count_response.status_code == 200:
        total_orders = count_response.json().get("count", 0)
        pages_needed = (total_orders + 249) // 250
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for page in range(pages_needed):
            status_text.text(f"Fetching page {page + 1} of {pages_needed}...")
            
            if page == 0:
                url = f"https://{SHOPIFY_STORE_URL}/admin/api/2023-10/orders.json?limit=250&status=any"
            else:
                last_order_date = all_orders[-1]['created_at']
                url = f"https://{SHOPIFY_STORE_URL}/admin/api/2023-10/orders.json?limit=250&status=any&created_at_max={last_order_date}"
            
            try:
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    page_orders = response.json().get("orders", [])
                    if not page_orders:
                        break
                    
                    existing_ids = {order['id'] for order in all_orders}
                    new_orders = [order for order in page_orders if order['id'] not in existing_ids]
                    all_orders.extend(new_orders)
                    
                    progress_bar.progress((page + 1) / pages_needed)
                    if len(new_orders) == 0:
                        break
                    time.sleep(0.5)
                else:
                    st.error(f"API Error: {response.status_code}")
                    break
            except Exception as e:
                st.error(f"Error: {e}")
                break
        
        progress_bar.empty()
        status_text.empty()
    
    return all_orders

def process_orders(orders):
    """Process orders ensuring no duplicates"""
    processed_sales = []
    seen_combinations = set()
    
    for order in orders:
        order_name = order.get('name', 'N/A')
        
        for line_item in order.get("line_items", []):
            item_id = line_item.get('id')
            combination_key = f"{order_name}_{item_id}"
            
            if combination_key in seen_combinations:
                continue
            seen_combinations.add(combination_key)
            
            item_name = line_item.get("name", "")
            selling_price = float(line_item.get("price", 0))
            quantity = int(line_item.get("quantity", 1))
            
            category = 'Hoodies' if 'hoodie' in item_name.lower() else 'T-Shirts'
            base_cost = 500 if category == 'Hoodies' else 210
            total_cost = base_cost + 370
            profit = selling_price - total_cost
            
            created_at = order.get("created_at", "")
            try:
                sale_date = datetime.fromisoformat(created_at.replace('Z', '+00:00')).strftime('%Y-%m-%d')
            except:
                sale_date = datetime.now().strftime('%Y-%m-%d')
            
            customer = order.get("email", "N/A")
            if '@' in str(customer):
                customer = customer.split('@')[0] + '@...'
            
            processed_sales.append({
                'item_name': item_name,
                'category': category,
                'selling_price': selling_price,
                'cost_used': total_cost,
                'profit': profit,
                'quantity': quantity,
                'date': sale_date,
                'customer': customer,
                'order_name': order_name,
                'financial_status': order.get('financial_status', 'unknown')
            })
    
    return processed_sales

def create_metric_card(label, value, delta=None, delta_color="normal"):
    delta_class = "metric-positive" if delta_color == "positive" else "metric-negative" if delta_color == "negative" else ""
    delta_html = f"<div style='font-size: 0.8rem; margin-top: 0.5rem; color: #00d4aa;'>{delta}</div>" if delta else ""
    
    return f"""
    <div class="metric-container">
        <div class="metric-value">{value}</div>
        <div class="metric-label">{label}</div>
        {delta_html}
    </div>
    """

if page == "Executive Dashboard":
    st.header("Business Performance Overview")
    
    if shopify_connected:
        if st.button("Refresh Data from Shopify", type="primary"):
            with st.spinner("Fetching all orders from your Swawe store..."):
                orders = fetch_all_orders()
                if orders:
                    st.session_state.sales_data = process_orders(orders)
                    unique_orders = len(set(sale['order_name'] for sale in st.session_state.sales_data))
                    st.success(f"Successfully loaded {unique_orders} orders with {len(st.session_state.sales_data)} line items!")
                    st.rerun()
    
    if st.session_state.sales_data:
        sales_df = pd.DataFrame(st.session_state.sales_data)
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        total_revenue = sales_df['selling_price'].sum()
        total_profit = sales_df['profit'].sum()
        profit_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
        unique_orders = sales_df['order_name'].nunique()
        
        with col1:
            st.markdown(create_metric_card("Total Revenue", f"₹{total_revenue:,.0f}"), unsafe_allow_html=True)
        with col2:
            st.markdown(create_metric_card("Net Profit", f"₹{total_profit:,.0f}", f"{profit_margin:.1f}% margin", "positive"), unsafe_allow_html=True)
        with col3:
            avg_order = sales_df['selling_price'].mean()
            st.markdown(create_metric_card("Avg Order Value", f"₹{avg_order:.0f}"), unsafe_allow_html=True)
        with col4:
            st.markdown(create_metric_card("Total Orders", f"{unique_orders:,}"), unsafe_allow_html=True)
        
        # Performance charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            sales_df['date'] = pd.to_datetime(sales_df['date'])
            monthly_data = sales_df.groupby(sales_df['date'].dt.to_period('M')).agg({
                'selling_price': 'sum',
                'profit': 'sum'
            }).reset_index()
            monthly_data['month'] = monthly_data['date'].astype(str)
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=monthly_data['month'], y=monthly_data['selling_price'],
                                   mode='lines+markers', name='Revenue', 
                                   line=dict(color='#667eea', width=3)))
            fig.add_trace(go.Scatter(x=monthly_data['month'], y=monthly_data['profit'],
                                   mode='lines+markers', name='Profit',
                                   line=dict(color='#00d4aa', width=3)))
            
            fig.update_layout(
                title="Monthly Performance Trend",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                xaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
                yaxis=dict(gridcolor='rgba(255,255,255,0.1)')
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            category_data = sales_df.groupby('category').agg({
                'selling_price': 'sum',
                'profit': 'sum'
            }).reset_index()
            
            fig = px.bar(category_data, x='category', y=['selling_price', 'profit'],
                       title="Category Performance", barmode='group',
                       color_discrete_sequence=['#667eea', '#00d4aa'])
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white')
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Business insights
        st.markdown("### Business Insights")
        
        profitable_orders = (sales_df['profit'] > 0).sum()
        profit_rate = (profitable_orders / len(sales_df)) * 100
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div class="insight-card">
                <h4 style="color: #00d4aa; margin-bottom: 0.5rem;">Profitability Analysis</h4>
                <p style="color: rgba(255,255,255,0.9);">
                {profit_rate:.1f}% of your orders are profitable with an average profit margin of {profit_margin:.1f}%.
                Your best performing category generates ₹{category_data['profit'].max():,.0f} in profits.
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            best_month = monthly_data.loc[monthly_data['profit'].idxmax(), 'month'] if len(monthly_data) > 0 else "N/A"
            st.markdown(f"""
            <div class="insight-card">
                <h4 style="color: #00d4aa; margin-bottom: 0.5rem;">Growth Trends</h4>
                <p style="color: rgba(255,255,255,0.9);">
                Your order range spans from #1231 to #1483, showing consistent business growth.
                Best performing month: {best_month} with strong profit margins.
                </p>
            </div>
            """, unsafe_allow_html=True)
        
    else:
        st.info("Click 'Refresh Data from Shopify' to load your store data and see comprehensive analytics.")

elif page == "Sales Analytics":
    st.header("Sales Analytics & Insights")
    
    if st.session_state.sales_data:
        sales_df = pd.DataFrame(st.session_state.sales_data)
        
        # Sales trends
        st.subheader("Sales Performance")
        sales_df['date'] = pd.to_datetime(sales_df['date'])
        daily_sales = sales_df.groupby('date').agg({
            'selling_price': 'sum',
            'profit': 'sum',
            'quantity': 'sum'
        }).reset_index()
        
        fig = px.line(daily_sales, x='date', y='selling_price', 
                     title="Daily Sales Trend", color_discrete_sequence=['#667eea'])
        st.plotly_chart(fig, use_container_width=True)
        
        # Product performance
        col1, col2 = st.columns(2)
        with col1:
            product_sales = sales_df.groupby('item_name').agg({
                'selling_price': 'sum',
                'quantity': 'sum'
            }).sort_values('selling_price', ascending=False).head(10)
            
            fig = px.bar(product_sales, x=product_sales.index, y='selling_price',
                        title="Top 10 Products by Revenue")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            category_profit = sales_df.groupby('category')['profit'].sum()
            fig = px.pie(values=category_profit.values, names=category_profit.index,
                        title="Profit by Category")
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Load data from Executive Dashboard first to see analytics.")

elif page == "Product Intelligence":
    st.header("Product Intelligence")
    
    if st.session_state.sales_data:
        sales_df = pd.DataFrame(st.session_state.sales_data)
        
        # Product metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Products", sales_df['item_name'].nunique())
        with col2:
            avg_price = sales_df['selling_price'].mean()
            st.metric("Avg Product Price", f"₹{avg_price:.0f}")
        with col3:
            best_product = sales_df.groupby('item_name')['profit'].sum().idxmax()
            st.metric("Best Product", best_product)
        
        # Detailed product analysis
        st.subheader("Product Performance Details")
        product_analysis = sales_df.groupby('item_name').agg({
            'selling_price': ['sum', 'mean', 'count'],
            'profit': ['sum', 'mean'],
            'quantity': 'sum'
        }).round(2)
        
        product_analysis.columns = ['Total Revenue', 'Avg Price', 'Orders', 'Total Profit', 'Avg Profit', 'Qty Sold']
        st.dataframe(product_analysis, use_container_width=True)
    else:
        st.info("Load data from Executive Dashboard first to see product intelligence.")

elif page == "Data Management":
    st.header("Data Management & Export")
    
    if st.session_state.sales_data:
        sales_df = pd.DataFrame(st.session_state.sales_data)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Orders", sales_df['order_name'].nunique())
        with col2:
            st.metric("Line Items", len(sales_df))
        with col3:
            st.metric("Revenue", f"₹{sales_df['selling_price'].sum():,.0f}")
        with col4:
            st.metric("Profit", f"₹{sales_df['profit'].sum():,.0f}")
        
        # Order range info
        order_numbers = [int(name.replace('#', '')) for name in sales_df['order_name'].unique() if name.startswith('#')]
        if order_numbers:
            min_order = min(order_numbers)
            max_order = max(order_numbers)
            st.info(f"Order Range: #{min_order} to #{max_order} ({max_order - min_order + 1} orders)")
        
        # Data preview
        st.subheader("Data Preview")
        st.dataframe(sales_df.head(20), use_container_width=True)
        
        # Export functionality
        if st.button("Export Complete Dataset", type="primary"):
            csv = sales_df.to_csv(index=False)
            st.download_button(
                label="Download Clean CSV",
                data=csv,
                file_name=f"swawe_complete_data_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv"
            )
    else:
        st.info("No data loaded. Go to Executive Dashboard and refresh data first.")

# Footer
st.markdown("""
<div style="margin-top: 3rem; padding: 2rem; text-align: center; border-top: 1px solid rgba(102, 126, 234, 0.2);">
    <div style="color: rgba(255,255,255,0.6); font-size: 0.9rem;">
        SWAWE Dashboard | Fashion Analytics & Business Intelligence
    </div>
</div>
""", unsafe_allow_html=True)

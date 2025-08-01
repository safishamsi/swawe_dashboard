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
    SHOPIFY_STORE_URL = st.secrets["SHOPIFY_STORE_URL"]
    SHOPIFY_ACCESS_TOKEN = st.secrets["SHOPIFY_ACCESS_TOKEN"]
    shopify_connected = True
except:
    SHOPIFY_STORE_URL = ""
    SHOPIFY_ACCESS_TOKEN = ""
    shopify_connected = False

# Initialize session state
if 'sales_data' not in st.session_state:
    st.session_state.sales_data = []

# Real-time update functionality
def check_for_new_orders():
    """Check for new orders since last refresh"""
    if 'last_order_check' not in st.session_state:
        st.session_state.last_order_check = datetime.now()
    
    # Check if we should refresh (every 5 minutes)
    if (datetime.now() - st.session_state.last_order_check).seconds > 300:
        if st.session_state.sales_data and shopify_connected:
            # Quick check for new orders
            headers = {"X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN}
            url = f"https://{SHOPIFY_STORE_URL}/admin/api/2023-10/orders.json?limit=5&status=any"
            try:
                response = requests.get(url, headers=headers)
                
                if response.status_code == 200:
                    recent_orders = response.json().get("orders", [])
                    if recent_orders:
                        # Check if we have new orders
                        existing_ids = {sale['order_name'] for sale in st.session_state.sales_data}
                        new_orders = [order for order in recent_orders if order.get('name') not in existing_ids]
                        
                        if new_orders:
                            st.success(f"🔔 {len(new_orders)} new orders detected! Click refresh to update.")
                            col1, col2 = st.columns([1, 4])
                            with col1:
                                if st.button("🔄 Quick Refresh"):
                                    new_sales = process_orders(new_orders)
                                    st.session_state.sales_data.extend(new_sales)
                                    st.rerun()
            except:
                pass  # Silently handle errors
        
        st.session_state.last_order_check = datetime.now()

# Enhanced CSS with mobile optimization
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
    
    /* Mobile-First Responsive Design */
    @media (max-width: 768px) {
        .main-title {
            font-size: 2rem !important;
            letter-spacing: 1px !important;
        }
        
        .subtitle {
            font-size: 0.9rem !important;
        }
        
        .main-header {
            padding: 1rem !important;
            margin-bottom: 1rem !important;
        }
        
        .metric-container {
            padding: 1rem !important;
            margin: 0.25rem 0 !important;
        }
        
        .metric-value {
            font-size: 1.8rem !important;
        }
        
        .metric-label {
            font-size: 0.8rem !important;
        }
        
        .chart-container {
            padding: 1rem !important;
            margin: 0.5rem 0 !important;
        }
        
        .insight-card {
            padding: 1rem !important;
            margin: 0.5rem 0 !important;
        }
        
        .stButton > button {
            width: 100% !important;
            padding: 0.5rem 1rem !important;
            font-size: 0.9rem !important;
            min-height: 48px !important;
        }
        
        .connected-badge, .disconnected-badge {
            font-size: 0.9rem !important;
            padding: 0.75rem 1.25rem !important;
        }
    }
    
    /* Tablet optimization */
    @media (max-width: 1024px) and (min-width: 769px) {
        .main-title {
            font-size: 2.5rem !important;
        }
        
        .metric-container {
            padding: 1.25rem !important;
        }
        
        .metric-value {
            font-size: 2rem !important;
        }
    }
    
    /* Touch-friendly elements */
    @media (hover: none) and (pointer: coarse) {
        .stButton > button {
            padding: 1rem 2rem !important;
            font-size: 1rem !important;
            min-height: 48px !important;
        }
        
        .metric-container {
            min-height: 120px !important;
        }
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
    # Check for new orders
    check_for_new_orders()
else:
    st.markdown('<div class="disconnected-badge">Shopify Not Connected - Add credentials in Settings → Secrets</div>', unsafe_allow_html=True)

# Enhanced Navigation with Shopify links
page = st.sidebar.selectbox("Choose a section:", 
    ["Executive Dashboard", "Sales Analytics", "Product Intelligence", "Data Management"])

# Add Shopify Quick Links to sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("### 🏪 Shopify Quick Links")
if shopify_connected:
    st.sidebar.markdown(f"[📦 View Orders](https://{SHOPIFY_STORE_URL}/admin/orders)")
    st.sidebar.markdown(f"[🛍️ Products](https://{SHOPIFY_STORE_URL}/admin/products)")
    st.sidebar.markdown(f"[👥 Customers](https://{SHOPIFY_STORE_URL}/admin/customers)")
    st.sidebar.markdown(f"[⚙️ Settings](https://{SHOPIFY_STORE_URL}/admin/settings)")
else:
    st.sidebar.markdown("Connect Shopify to see admin links")

# Admin Widget View Toggle
st.sidebar.markdown("---")
admin_widget_view = st.sidebar.checkbox("🎛️ Admin Widget View")

def fetch_all_orders():
    """Fetch ALL orders using proper Shopify pagination"""
    if not shopify_connected:
        return []
        
    all_orders = []
    headers = {"X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN}
    
    # Get total count first
    count_url = f"https://{SHOPIFY_STORE_URL}/admin/api/2023-10/orders/count.json?status=any"
    count_response = requests.get(count_url, headers=headers)
    
    if count_response.status_code == 200:
        total_orders = count_response.json().get("count", 0)
        st.info(f"Found {total_orders} total orders in your store")
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Start with first batch
        url = f"https://{SHOPIFY_STORE_URL}/admin/api/2023-10/orders.json?limit=250&status=any"
        page_count = 0
        
        while url:
            page_count += 1
            status_text.text(f"Fetching batch {page_count}... ({len(all_orders)} orders loaded)")
            
            try:
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    page_orders = response.json().get("orders", [])
                    if not page_orders:
                        break
                    
                    all_orders.extend(page_orders)
                    progress_bar.progress(min(len(all_orders) / total_orders, 0.99))
                    
                    # Get next page URL from Link header
                    link_header = response.headers.get('Link', '')
                    url = None
                    if 'rel="next"' in link_header:
                        # Extract next URL from Link header
                        for link in link_header.split(','):
                            if 'rel="next"' in link:
                                url = link.split(';')[0].strip('<> ')
                                break
                    
                    time.sleep(0.5)
                else:
                    st.error(f"API Error: {response.status_code} - {response.text}")
                    break
            except Exception as e:
                st.error(f"Error: {e}")
                break
        
        progress_bar.empty()
        status_text.empty()
        
        # Show order range
        order_numbers = []
        for order in all_orders:
            order_name = order.get('name', '')
            if order_name.startswith('#'):
                try:
                    order_numbers.append(int(order_name.replace('#', '')))
                except:
                    pass
        
        if order_numbers:
            min_order = min(order_numbers)
            max_order = max(order_numbers)
            st.success(f"✅ Successfully loaded {len(all_orders)} orders (#{min_order} to #{max_order})")
        else:
            st.success(f"✅ Successfully loaded {len(all_orders)} orders")
    
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

# Admin Widget View
if admin_widget_view and st.session_state.sales_data:
    st.markdown("### 📊 SWAWE Admin Dashboard")
    
    sales_df = pd.DataFrame(st.session_state.sales_data)
    
    # Quick Stats Banner
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        color: white;
        display: flex;
        justify-content: space-between;
        align-items: center;
    ">
        <div>
            <h3 style="margin: 0; font-size: 1.2rem;">SWAWE Quick Stats</h3>
            <p style="margin: 0; opacity: 0.9; font-size: 0.9rem;">Real-time business metrics</p>
        </div>
        <div style="text-align: right;">
            <div style="font-size: 1.5rem; font-weight: bold;">₹{sales_df['selling_price'].sum():,.0f}</div>
            <div style="font-size: 0.8rem; opacity: 0.8;">Total Revenue</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Orders", f"{sales_df['order_name'].nunique():,}")
    with col2:
        profit_margin = (sales_df['profit'].sum() / sales_df['selling_price'].sum() * 100)
        st.metric("Profit Margin", f"{profit_margin:.1f}%")
    with col3:
        st.metric("Avg Order", f"₹{sales_df['selling_price'].mean():,.0f}")
    with col4:
        st.metric("Total Profit", f"₹{sales_df['profit'].sum():,.0f}")
    
    # Mini Chart
    st.markdown("#### 📈 Last 7 Days Sales Trend")
    sales_df['date'] = pd.to_datetime(sales_df['date'])
    daily_sales = sales_df.groupby('date')['selling_price'].sum().tail(7)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=daily_sales.index,
        y=daily_sales.values,
        mode='lines+markers',
        line=dict(color='#667eea', width=3),
        marker=dict(size=6),
        name='Daily Sales'
    ))
    
    fig.update_layout(
        height=200,
        margin=dict(l=20, r=20, t=40, b=20),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=10, color='white'),
        showlegend=False,
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)')
    )
    
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    # Quick Actions
    st.markdown("#### 🚀 Quick Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Export Data", use_container_width=True):
            csv = sales_df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"swawe_data_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
    
    with col2:
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.rerun()
    
    with col3:
        if st.button("🏪 Open Shopify", use_container_width=True):
            st.markdown(f'<a href="https://{SHOPIFY_STORE_URL}/admin" target="_blank">Opening Shopify Admin...</a>', unsafe_allow_html=True)
    
    # Real-time status
    st.markdown(f"""
    <div style="
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: #ecfdf5;
        border: 1px solid #10b981;
        border-radius: 6px;
        padding: 0.75rem;
        margin-top: 1rem;
        font-size: 0.9rem;
    ">
        <span>🟢 Dashboard Active</span>
        <span style="color: #10b981;">Last Updated: {datetime.now().strftime("%H:%M:%S")}</span>
    </div>
    """, unsafe_allow_html=True)

# Main Dashboard Content (only show if not in widget view)
if not admin_widget_view:
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
                    Your order range spans across multiple months, showing consistent business growth.
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
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white')
            )
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
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white')
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                category_profit = sales_df.groupby('category')['profit'].sum()
                fig = px.pie(values=category_profit.values, names=category_profit.index,
                            title="Profit by Category")
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white')
                )
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

if st.session_state.sales_data:
            # Apply date filtering
            filtered_sales = filter_sales_by_date(st.session_state.sales_data)
            
            if filtered_sales:
                sales_df = pd.DataFrame(filtered_sales)
                
                # Get comparison data and fulfillment analytics
                comparison_data = get_date_comparison_metrics(sales_df)
                fulfillment_data = get_fulfillment_analytics(sales_df)
                
                # Show date range info
                total_days = (st.session_state.date_range_end - st.session_state.date_range_start).days
                st.info(f"📅 Showing data for **{st.session_state.date_range_start.strftime('%B %d, %Y')}** to **{st.session_state.date_range_end.strftime('%B %d, %Y')}** ({total_days} days)")
                
                # Fulfillment Status Alert
                if fulfillment_data and fulfillment_data['unfulfilled_orders'] > 0:
                    st.warning(f"📦 **{fulfillment_data['unfulfilled_orders']} orders** (₹{fulfillment_data['unfulfilled_value']:,.0f}) are pending fulfillment")
                
                # Premium Metrics with Period Comparison
                col1, col2, col3, col4, col5 = st.columns(5)
                
                total_revenue = sales_df['selling_price'].sum()
                total_profit = sales_df['profit'].sum()
                profit_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
                unique_orders = sales_df['order_name'].nunique()
                avg_order = sales_df['selling_price'].mean()
                
                with col1:
                    st.markdown(create_premium_metric_card_with_comparison("Total Revenue", f"₹{total_revenue:,.0f}", comparison_data, "revenue_change"), unsafe_allow_html=True)
                with col2:
                    st.markdown(create_premium_metric_card_with_comparison("Net Profit", f"₹{total_profit:,.0f}", comparison_data, "profit_change"), unsafe_allow_html=True)
                with col3:
                    st.markdown(create_premium_metric_card("Avg Order Value", f"₹{avg_order:.0f}"), unsafe_allow_html=True)
                with col4:
                    st.markdown(create_premium_metric_card_with_comparison("Total Orders", f"{unique_orders:,}", comparison_data, "orders_change"), unsafe_allow_html=True)
                
                # New Unfulfilled Orders Metric
                with col5:
                    if fulfillment_data:
                        unfulfilled_color = "⚠️" if fulfillment_data['unfulfilled_orders'] > 0 else "✅"
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-value" style="color: {'#FF6B6B' if fulfillment_data['unfulfilled_orders'] > 0 else '#00D4AA'};">
                                {unfulfilled_color} {fulfillment_data['unfulfilled_orders']}
                            </div>
                            <div class="metric-label">Pending Orders</div>
                            <div class="metric-delta" style="color: #666;">₹{fulfillment_data['unfulfilled_value']:,.0f} value</div>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Detailed Fulfillment Analytics
                if fulfillment_data:
                    st.markdown("#### 📦 **Fulfillment & Shipping Analytics**")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.markdown(f"""
                        <div class="metric-card">
                            <div style="text-align: center;">
                                <div style="font-size: 2.5rem; color: #FF6B6B; margin-bottom: 0.5rem;">📋</div>
                                <div style="font-size: 1.8rem; font-weight: bold; color: #FF6B6B;">{fulfillment_data['unfulfilled_orders']}</div>
                                <div style="color: #666; font-size: 0.9rem; margin-bottom: 0.5rem;">PENDING ORDERS</div>
                                <div style="font-size: 0.8rem; color: #999;">₹{fulfillment_data['unfulfilled_value']:,.0f} pending value</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(f"""
                        <div class="metric-card">
                            <div style="text-align: center;">
                                <div style="font-size: 2.5rem; color: #FF6B35; margin-bottom: 0.5rem;">📦</div>
                                <div style="font-size: 1.8rem; font-weight: bold; color: #FF6B35;">{fulfillment_data['pending_shipment_items']}</div>
                                <div style="color: #666; font-size: 0.9rem; margin-bottom: 0.5rem;">ITEMS TO SHIP</div>
                                <div style="font-size: 0.8rem; color: #999;">Ready for fulfillment</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col3:
                        st.markdown(f"""
                        <div class="metric-card">
                            <div style="text-align: center;">
                                <div style="font-size: 2.5rem; color: #00D4AA; margin-bottom: 0.5rem;">✅</div>
                                <div style="font-size: 1.8rem; font-weight: bold; color: #00D4AA;">{fulfillment_data['fulfilled_orders']}</div>
                                <div style="color: #666; font-size: 0.9rem; margin-bottom: 0.5rem;">FULFILLED ORDERS</div>
                                <div style="font-size: 0.8rem; color: #999;">₹{fulfillment_data['fulfilled_value']:,.0f} completed</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col4:
                        fulfillment_rate = fulfillment_data.get('fulfilled_percentage', 0)
                        rate_color = "#00D4AA" if fulfillment_rate >= 80 else "#FF6B35" if fulfillment_rate >= 60 else "#FF6B6B"
                        st.markdown(f"""
                        <div class="metric-card">
                            <div style="text-align: center;">
                                <div style="font-size: 2.5rem; color: {rate_color}; margin-bottom: 0.5rem;">📊</div>
                                <div style="font-size: 1.8rem; font-weight: bold; color: {rate_color};">{fulfillment_rate:.1f}%</div>
                                <div style="color: #666; font-size: 0.9rem; margin-bottom: 0.5rem;">FULFILLMENT RATE</div>
                                <div style="font-size: 0.8rem; color: #999;">Orders completed</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Period Comparison Summary
                if comparison_data:
                    st.markdown("#### 📊 **Period Comparison**")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        revenue_trend = "📈" if comparison_data['revenue_change'] > 0 else "📉" if comparison_data['revenue_change'] < 0 else "➡️"
                        st.markdown(f"""
                        <div style="background: rgba(255,255,255,0.05); padding: 1rem; border-radius: 10px; text-align: center;">
                            <div style="font-size: 2rem;">{revenue_trend}</div>
                            <div style="color: #FF6B35; font-weight: bold;">Revenue Trend</div>
                            <div style="font-size: 0.9rem; color: #666;">vs previous {total_days} days</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col3:
                        profit_trend = "📈" if comparison_data['profit_change'] > 0 else "📉" if comparison_data['profit_change'] < 0 else "➡️"
                        st.markdown(f"""
                        <div style="background: rgba(255,255,255,0.05); padding: 1rem; border-radius: 10px; text-align: center;">
                            <div style="font-size: 2rem;">{profit_trend}</div>
                            <div style="color: #FF6B35; font-weight: bold;">Profit Trend</div>
                            <div style="font-size: 0.9rem; color: #666;">vs previous {total_days} days</div>
                        </div>
                        """, unsafe_allow_html=True)

                # Premium Metrics with Profit Analysis
                st.markdown("#### 💰 **Profit Analysis by Category**")
                col1, col2 = st.columns(2)
                
                with col1:
                    hoodie_data = sales_df[sales_df['category'] == 'Hoodies']
                    if len(hoodie_data) > 0:
                        hoodie_profit = hoodie_data['profit'].sum()
                        hoodie_margin = (hoodie_profit / hoodie_data['selling_price'].sum() * 100) if len(hoodie_data) > 0 else 0
                        hoodie_avg_profit = hoodie_data['profit'].mean()
                        
                        st.markdown(f"""
                        <div class="metric-card">
                            <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                                <span style="font-size: 2rem; margin-right: 0.5rem;">🧥</span>
                                <h4 style="margin: 0; color: #FF6B35;">Hoodies Performance</h4>
                            </div>
                            <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                                <span>Total Profit:</span><strong>₹{hoodie_profit:,.0f}</strong>
                            </div>
                            <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                                <span>Profit Margin:</span><strong>{hoodie_margin:.1f}%</strong>
                            </div>
                            <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                                <span>Avg Profit/Item:</span><strong>₹{hoodie_avg_profit:.0f}</strong>
                            </div>
                            <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                                <span>Units Sold:</span><strong>{len(hoodie_data):,}</strong>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                
                with col2:
                    tshirt_data = sales_df[sales_df['category'] == 'T-Shirts']
                    if len(tshirt_data) > 0:
                        tshirt_profit = tshirt_data['profit'].sum()
                        tshirt_margin = (tshirt_profit / tshirt_data['selling_price'].sum() * 100) if len(tshirt_data) > 0 else 0
                        tshirt_avg_profit = tshirt_data['profit'].mean()
                        
                        st.markdown(f"""
                        <div class="metric-card">
                            <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                                <span style="font-size: 2rem; margin-right: 0.5rem;">👕</span>
                                <h4 style="margin: 0; color: #FF6B35;">T-Shirts Performance</h4>
                            </div>
                            <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                                <span>Total Profit:</span><strong>₹{tshirt_profit:,.0f}</strong>
                            </div>
                            <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                                <span>Profit Margin:</span><strong>{tshirt_margin:.1f}%</strong>
                            </div>
                            <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                                <span>Avg Profit/Item:</span><strong>₹{tshirt_avg_profit:.0f}</strong>
                            </div>
                            <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                                <span>Units Sold:</span><strong>{len(tshirt_data):,}</strong>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        orders_trend = "📈" if comparison_data['orders_change'] > 0 else "📉" if comparison_data['orders_change'] < 0 else "➡️"
                        st.markdown(f"""
                        <div style="background: rgba(255,255,255,0.05); padding: 1rem; border-radius: 10px; text-align: center;">
                            <div style="font-size: 2rem;">{orders_trend}</div>
                            <div style="color: #FF6B35; font-weight: bold;">Orders Trend</div>
                            <div style="font-size: 0.9rem; color: #666;">vs previous {total_days} days</div>
                import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
from datetime import datetime, timedelta
import time
import base64

st.set_page_config(
    page_title="SWAWE Dashboard",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
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
    
    if (datetime.now() - st.session_state.last_order_check).seconds > 300:
        if st.session_state.sales_data and shopify_connected:
            headers = {"X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN}
            url = f"https://{SHOPIFY_STORE_URL}/admin/api/2023-10/orders.json?limit=5&status=any"
            try:
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    recent_orders = response.json().get("orders", [])
                    if recent_orders:
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
                pass
        st.session_state.last_order_check = datetime.now()

# Enhanced CSS with premium branding
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800;900&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    :root {
        --swawe-primary: #FF6B35;
        --swawe-secondary: #1A1A2E;
        --swawe-accent: #16213E;
        --swawe-success: #00D4AA;
        --swawe-gradient: linear-gradient(135deg, #ffffff 0%, #f8f9fa 50%, #ffffff 100%);
        --swawe-white-gradient: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        --swawe-dark-gradient: linear-gradient(135deg, #1A1A2E 0%, #16213E 50%, #0F0F23 100%);
    }
    
    .stApp {
        background: var(--swawe-dark-gradient);
        font-family: 'Inter', sans-serif;
    }
    
    /* Custom Header with Logo */
    .swawe-header {
        background: var(--swawe-white-gradient);
        padding: 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(0, 0, 0, 0.05);
    }
    
    .swawe-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,107,53,0.05) 0%, transparent 70%);
        animation: shimmer 3s ease-in-out infinite;
    }
    
    @keyframes shimmer {
        0%, 100% { transform: translate(-50%, -50%) rotate(0deg); }
        50% { transform: translate(-50%, -50%) rotate(180deg); }
    }
    
    .swawe-logo {
        font-family: 'Poppins', sans-serif;
        color: #000000 !important;
        font-size: 3.5rem;
        font-weight: 900;
        margin: 0;
        letter-spacing: 3px;
        text-shadow: 2px 2px 8px rgba(0,0,0,0.1);
        position: relative;
        z-index: 1;
    }
    
    .swawe-tagline {
        color: #666 !important;
        font-size: 1.1rem;
        margin-top: 0.5rem;
        font-weight: 500;
        position: relative;
        z-index: 1;
    }
    
    /* Premium Metric Cards */
    .metric-card {
        background: linear-gradient(145deg, rgba(255,255,255,0.05), rgba(255,255,255,0.02));
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 20px;
        padding: 2rem;
        margin: 0.5rem 0;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,107,53,0.1), transparent);
        transition: left 0.6s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-10px) scale(1.02);
        box-shadow: 0 25px 50px rgba(255, 107, 53, 0.2);
        border-color: rgba(255, 107, 53, 0.3);
    }
    
    .metric-card:hover::before {
        left: 100%;
    }
    
    .metric-value {
        font-family: 'Poppins', sans-serif;
        font-size: 2.8rem;
        font-weight: 800;
        background: var(--swawe-gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
        line-height: 1.2;
    }
    
    .metric-label {
        color: rgba(255,255,255,0.8);
        font-size: 0.9rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 0.5rem;
    }
    
    .metric-delta {
        font-size: 0.8rem;
        color: var(--swawe-success);
        font-weight: 500;
    }
    
    /* Status Badges */
    .status-badge {
        display: inline-flex;
        align-items: center;
        padding: 0.75rem 1.5rem;
        border-radius: 50px;
        font-size: 0.9rem;
        font-weight: 600;
        margin-bottom: 1.5rem;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.1);
        transition: all 0.3s ease;
    }
    
    .status-connected {
        background: linear-gradient(135deg, #00D4AA, #00B894);
        color: white;
        box-shadow: 0 5px 15px rgba(0, 212, 170, 0.3);
    }
    
    .status-disconnected {
        background: linear-gradient(135deg, #FF6B6B, #E55656);
        color: white;
        box-shadow: 0 5px 15px rgba(255, 107, 107, 0.3);
    }
    
    /* Premium Charts */
    .chart-container {
        background: linear-gradient(145deg, rgba(255,255,255,0.03), rgba(255,255,255,0.01));
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 20px;
        padding: 2rem;
        margin: 1.5rem 0;
        transition: all 0.3s ease;
    }
    
    .chart-container:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 40px rgba(0,0,0,0.2);
        border-color: rgba(255, 107, 53, 0.2);
    }
    
    /* Insight Cards */
    .insight-card {
        background: linear-gradient(145deg, rgba(255,255,255,0.05), rgba(255,255,255,0.02));
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 20px;
        padding: 2rem;
        margin: 1.5rem 0;
        border-left: 4px solid var(--swawe-primary);
        position: relative;
        overflow: hidden;
    }
    
    .insight-card::after {
        content: '';
        position: absolute;
        top: 0;
        right: 0;
        width: 100px;
        height: 100px;
        background: radial-gradient(circle, rgba(255,107,53,0.1) 0%, transparent 70%);
        border-radius: 50%;
        transform: translate(50%, -50%);
    }
    
    /* Premium Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 50px !important;
        padding: 1rem 2.5rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 10px 25px rgba(255, 107, 53, 0.3) !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px) scale(1.05) !important;
        box-shadow: 0 20px 40px rgba(255, 107, 53, 0.4) !important;
    }
    
    .stButton > button:active {
        transform: translateY(-1px) scale(1.02) !important;
    }
    
    /* Sidebar Enhancements */
    .css-1d391kg {
        background: linear-gradient(180deg, rgba(26,26,46,0.95) 0%, rgba(15,15,35,0.95) 100%) !important;
        backdrop-filter: blur(20px) !important;
        border-right: 1px solid rgba(255,255,255,0.1) !important;
    }
    
    .css-1d391kg .stSelectbox > div > div {
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 15px !important;
        color: white !important;
    }
    
    /* Mobile Responsive */
    @media (max-width: 768px) {
        .swawe-logo {
            font-size: 2.5rem !important;
            letter-spacing: 2px !important;
        }
        
        .swawe-header {
            padding: 1.5rem !important;
            margin-bottom: 1.5rem !important;
        }
        
        .metric-card {
            padding: 1.5rem !important;
            margin: 0.5rem 0 !important;
        }
        
        .metric-value {
            font-size: 2rem !important;
        }
        
        .metric-label {
            font-size: 0.8rem !important;
            letter-spacing: 1px !important;
        }
        
        .chart-container {
            padding: 1.5rem !important;
            margin: 1rem 0 !important;
        }
        
        .insight-card {
            padding: 1.5rem !important;
            margin: 1rem 0 !important;
        }
        
        .stButton > button {
            width: 100% !important;
            padding: 1rem 1.5rem !important;
            font-size: 0.9rem !important;
        }
    }
    
    /* Loading Animation */
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    .loading {
        animation: pulse 2s ease-in-out infinite;
    }
    
    /* Premium Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255,255,255,0.05);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--swawe-gradient);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%);
    }
</style>
""", unsafe_allow_html=True)

# Premium Header with SWAWE Logo
st.markdown("""
<div class="swawe-header">
    <img src="https://cdn.shopify.com/s/files/1/0604/9733/0266/files/bimi-svg-tiny-12-ps.svg?v=1754005795" 
         style="height: 80px; margin-bottom: 1rem; filter: drop-shadow(0 4px 8px rgba(0,0,0,0.1));" 
         alt="SWAWE Logo">
    <h1 class="swawe-logo">SWAWE</h1>
    <p class="swawe-tagline">Fashion Analytics & Business Intelligence</p>
</div>
""", unsafe_allow_html=True)

# Enhanced Connection Status
if shopify_connected:
    st.markdown('<div class="status-badge status-connected">✨ Connected to Shopify Store</div>', unsafe_allow_html=True)
    check_for_new_orders()
else:
    st.markdown('<div class="status-badge status-disconnected">⚠️ Shopify Not Connected - Add credentials in Settings</div>', unsafe_allow_html=True)

# Enhanced Navigation with Date Filtering
page = st.sidebar.selectbox("🎯 Choose Dashboard Section:", 
    ["Executive Dashboard", "Sales Analytics", "Product Intelligence", "Data Management"],
    help="Select the analytics section you want to explore")

# Advanced Date Range Filtering
st.sidebar.markdown("---")
st.sidebar.markdown("### 📅 **Date Range Filter**")
st.sidebar.markdown("*Analyze specific time periods*")

# Initialize date range in session state
if 'date_range_start' not in st.session_state:
    st.session_state.date_range_start = datetime.now() - timedelta(days=30)
if 'date_range_end' not in st.session_state:
    st.session_state.date_range_end = datetime.now()

# Quick date range buttons
st.sidebar.markdown("**Quick Filters:**")
col1, col2 = st.sidebar.columns(2)

with col1:
    if st.button("📊 Last 7 Days", use_container_width=True):
        st.session_state.date_range_start = datetime.now() - timedelta(days=7)
        st.session_state.date_range_end = datetime.now()
        st.rerun()
    
    if st.button("📈 Last 30 Days", use_container_width=True):
        st.session_state.date_range_start = datetime.now() - timedelta(days=30)
        st.session_state.date_range_end = datetime.now()
        st.rerun()

with col2:
    if st.button("📉 Last 90 Days", use_container_width=True):
        st.session_state.date_range_start = datetime.now() - timedelta(days=90)
        st.session_state.date_range_end = datetime.now()
        st.rerun()
    
    if st.button("🗓️ This Year", use_container_width=True):
        st.session_state.date_range_start = datetime(datetime.now().year, 1, 1)
        st.session_state.date_range_end = datetime.now()
        st.rerun()

# Custom date range picker
st.sidebar.markdown("**Custom Range:**")
date_range = st.sidebar.date_input(
    "Select Custom Date Range",
    value=(st.session_state.date_range_start.date(), st.session_state.date_range_end.date()),
    help="Choose start and end dates for analysis"
)

# Update session state if dates changed
if len(date_range) == 2:
    new_start = datetime.combine(date_range[0], datetime.min.time())
    new_end = datetime.combine(date_range[1], datetime.max.time())
    
    if new_start != st.session_state.date_range_start or new_end != st.session_state.date_range_end:
        st.session_state.date_range_start = new_start
        st.session_state.date_range_end = new_end
        st.rerun()

# Show selected range info
total_days = (st.session_state.date_range_end - st.session_state.date_range_start).days
st.sidebar.markdown(f"""
<div style="background: rgba(255,107,53,0.1); padding: 0.75rem; border-radius: 8px; font-size: 0.85rem; margin-top: 0.5rem;">
    📅 <strong>Selected Range:</strong><br>
    {st.session_state.date_range_start.strftime('%b %d, %Y')} - {st.session_state.date_range_end.strftime('%b %d, %Y')}<br>
    <strong>{total_days} days</strong> of data
</div>
""", unsafe_allow_html=True)

# Profit Margin Configuration
st.sidebar.markdown("---")
st.sidebar.markdown("### 💰 **Profit Configuration**")
st.sidebar.markdown("*Adjust margins to analyze different pricing scenarios*")

# Initialize default margins in session state
if 'hoodie_base_cost' not in st.session_state:
    st.session_state.hoodie_base_cost = 500
if 'tshirt_base_cost' not in st.session_state:
    st.session_state.tshirt_base_cost = 210
if 'additional_cost' not in st.session_state:
    st.session_state.additional_cost = 370

with st.sidebar.expander("🔧 **Margin Settings**", expanded=False):
    st.markdown("**Product Costs:**")
    
    hoodie_cost = st.number_input(
        "🧥 Hoodie Base Cost (₹)", 
        min_value=0, 
        max_value=2000, 
        value=st.session_state.hoodie_base_cost,
        step=10,
        help="Base manufacturing cost for hoodies"
    )
    
    tshirt_cost = st.number_input(
        "👕 T-Shirt Base Cost (₹)", 
        min_value=0, 
        max_value=1000, 
        value=st.session_state.tshirt_base_cost,
        step=10,
        help="Base manufacturing cost for t-shirts"
    )
    
    additional_cost = st.number_input(
        "📦 Additional Costs (₹)", 
        min_value=0, 
        max_value=1000, 
        value=st.session_state.additional_cost,
        step=10,
        help="Shipping, packaging, overhead costs etc."
    )
    
    # Update session state when values change
    if hoodie_cost != st.session_state.hoodie_base_cost or tshirt_cost != st.session_state.tshirt_base_cost or additional_cost != st.session_state.additional_cost:
        st.session_state.hoodie_base_cost = hoodie_cost
        st.session_state.tshirt_base_cost = tshirt_cost
        st.session_state.additional_cost = additional_cost
        
        # Recalculate profits if data exists
        if st.session_state.sales_data:
            st.session_state.sales_data = recalculate_profits(st.session_state.sales_data)
            st.success("💡 Profits recalculated!")
    
    # Show current margin preview
    st.markdown("**Current Setup:**")
    hoodie_total = hoodie_cost + additional_cost
    tshirt_total = tshirt_cost + additional_cost
    
    st.markdown(f"""
    <div style="background: rgba(255,107,53,0.1); padding: 0.75rem; border-radius: 8px; font-size: 0.85rem;">
        🧥 <strong>Hoodie Total Cost:</strong> ₹{hoodie_total}<br>
        👕 <strong>T-Shirt Total Cost:</strong> ₹{tshirt_total}
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🔄 Reset to Defaults", help="Reset to original cost values"):
        st.session_state.hoodie_base_cost = 500
        st.session_state.tshirt_base_cost = 210
        st.session_state.additional_cost = 370
        if st.session_state.sales_data:
            st.session_state.sales_data = recalculate_profits(st.session_state.sales_data)
        st.rerun()

# Enhanced Shopify Quick Links
st.sidebar.markdown("---")
st.sidebar.markdown("### 🏪 **Shopify Quick Access**")
if shopify_connected:
    st.sidebar.markdown(f"""
    <div style="background: rgba(255,255,255,0.03); padding: 1rem; border-radius: 15px; border: 1px solid rgba(255,255,255,0.1);">
        <a href="https://{SHOPIFY_STORE_URL}/admin/orders" target="_blank" style="color: #FF6B35; text-decoration: none; display: block; padding: 0.5rem 0;">📦 Orders</a>
        <a href="https://{SHOPIFY_STORE_URL}/admin/products" target="_blank" style="color: #FF6B35; text-decoration: none; display: block; padding: 0.5rem 0;">🛍️ Products</a>
        <a href="https://{SHOPIFY_STORE_URL}/admin/customers" target="_blank" style="color: #FF6B35; text-decoration: none; display: block; padding: 0.5rem 0;">👥 Customers</a>
        <a href="https://{SHOPIFY_STORE_URL}/admin/settings" target="_blank" style="color: #FF6B35; text-decoration: none; display: block; padding: 0.5rem 0;">⚙️ Settings</a>
    </div>
    """, unsafe_allow_html=True)
else:
    st.sidebar.info("Connect Shopify to see admin links")

# Premium Admin Widget View Toggle
st.sidebar.markdown("---")
admin_widget_view = st.sidebar.checkbox("🎛️ **Compact Widget View**", help="Switch to a condensed dashboard view for quick insights")

def fetch_all_orders():
    """Fetch ALL orders using proper Shopify pagination"""
    if not shopify_connected:
        return []
        
    all_orders = []
    headers = {"X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN}
    
    count_url = f"https://{SHOPIFY_STORE_URL}/admin/api/2023-10/orders/count.json?status=any"
    count_response = requests.get(count_url, headers=headers)
    
    if count_response.status_code == 200:
        total_orders = count_response.json().get("count", 0)
        st.info(f"🔍 Found {total_orders} total orders in your store")
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        url = f"https://{SHOPIFY_STORE_URL}/admin/api/2023-10/orders.json?limit=250&status=any"
        page_count = 0
        
        while url:
            page_count += 1
            status_text.text(f"📥 Fetching batch {page_count}... ({len(all_orders)} orders loaded)")
            
            try:
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    page_orders = response.json().get("orders", [])
                    if not page_orders:
                        break
                    
                    all_orders.extend(page_orders)
                    progress_bar.progress(min(len(all_orders) / total_orders, 0.99))
                    
                    link_header = response.headers.get('Link', '')
                    url = None
                    if 'rel="next"' in link_header:
                        for link in link_header.split(','):
                            if 'rel="next"' in link:
                                url = link.split(';')[0].strip('<> ')
                                break
                    
                    time.sleep(0.5)
                else:
                    st.error(f"❌ API Error: {response.status_code}")
                    break
            except Exception as e:
                st.error(f"❌ Error: {e}")
                break
        
        progress_bar.empty()
        status_text.empty()
        
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

def recalculate_profits(sales_data):
    """Recalculate profits based on current margin settings"""
    updated_data = []
    
    hoodie_total_cost = st.session_state.hoodie_base_cost + st.session_state.additional_cost
    tshirt_total_cost = st.session_state.tshirt_base_cost + st.session_state.additional_cost
    
    for sale in sales_data:
        updated_sale = sale.copy()
        
        # Determine total cost based on category
        if sale['category'] == 'Hoodies':
            updated_sale['cost_used'] = hoodie_total_cost
        else:  # T-Shirts
            updated_sale['cost_used'] = tshirt_total_cost
        
        # Recalculate profit
        updated_sale['profit'] = sale['selling_price'] - updated_sale['cost_used']
        
        updated_data.append(updated_sale)
    
    return updated_data

def create_premium_metric_card_with_comparison(label, value, comparison_data=None, metric_key=None):
    """Create metric card with period comparison"""
    delta_html = ""
    
    if comparison_data and metric_key and metric_key in comparison_data:
        change = comparison_data[metric_key]
        if change > 0:
            delta_html = f'<div class="metric-delta" style="color: #00D4AA;">↗ +{change:.1f}% vs prev period</div>'
        elif change < 0:
            delta_html = f'<div class="metric-delta" style="color: #FF6B6B;">↘ {change:.1f}% vs prev period</div>'
        else:
            delta_html = f'<div class="metric-delta" style="color: #666;">→ No change vs prev period</div>'
    
    return f"""
    <div class="metric-card">
        <div class="metric-value">{value}</div>
        <div class="metric-label">{label}</div>
        {delta_html}
    </div>
    """
    """Filter sales data by selected date range"""
    if not sales_data:
        return []
    
    filtered_data = []
    start_date = st.session_state.date_range_start.date()
    end_date = st.session_state.date_range_end.date()
    
    for sale in sales_data:
        try:
            sale_date = datetime.strptime(sale['date'], '%Y-%m-%d').date()
            if start_date <= sale_date <= end_date:
                filtered_data.append(sale)
        except:
            # If date parsing fails, include the record
            filtered_data.append(sale)
    
    return filtered_data

def get_date_comparison_metrics(sales_df):
    """Get comparison metrics for selected vs previous period"""
    if sales_df.empty:
        return None
    
    # Current period metrics
    current_revenue = sales_df['selling_price'].sum()
    current_orders = sales_df['order_name'].nunique()
    current_profit = sales_df['profit'].sum()
    
    # Calculate previous period (same length as current period)
    current_days = (st.session_state.date_range_end - st.session_state.date_range_start).days
    previous_start = st.session_state.date_range_start - timedelta(days=current_days)
    previous_end = st.session_state.date_range_start - timedelta(days=1)
    
    # Filter data for previous period
    previous_data = []
    if st.session_state.sales_data:
        for sale in st.session_state.sales_data:
            try:
                sale_date = datetime.strptime(sale['date'], '%Y-%m-%d').date()
                if previous_start.date() <= sale_date <= previous_end.date():
                    previous_data.append(sale)
            except:
                continue
    
    if previous_data:
        previous_df = pd.DataFrame(previous_data)
        previous_revenue = previous_df['selling_price'].sum()
        previous_orders = previous_df['order_name'].nunique()
        previous_profit = previous_df['profit'].sum()
        
        # Calculate changes
        revenue_change = ((current_revenue - previous_revenue) / previous_revenue * 100) if previous_revenue > 0 else 0
        orders_change = ((current_orders - previous_orders) / previous_orders * 100) if previous_orders > 0 else 0
        profit_change = ((current_profit - previous_profit) / previous_profit * 100) if previous_profit > 0 else 0
        
        return {
            'revenue_change': revenue_change,
            'orders_change': orders_change,
            'profit_change': profit_change,
            'previous_revenue': previous_revenue,
            'previous_orders': previous_orders,
            'previous_profit': previous_profit
        }
    
    return None
    """Calculate fulfillment and shipping analytics"""
    if sales_df.empty:
        return None
    
    # Fulfillment status analysis
    fulfillment_stats = {
        'total_orders': sales_df['order_name'].nunique(),
        'unfulfilled_orders': 0,
        'unfulfilled_value': 0,
        'pending_shipment_items': 0,
        'fulfilled_orders': 0,
        'fulfilled_value': 0
    }
    
    # Group by order to get order-level fulfillment
    order_analysis = sales_df.groupby('order_name').agg({
        'fulfillment_status': 'first',  # Same for all items in an order
        'selling_price': 'sum',
        'quantity': 'sum'
    }).reset_index()
    
    # Calculate unfulfilled orders and values
    unfulfilled_orders = order_analysis[order_analysis['fulfillment_status'].isin(['unfulfilled', 'pending', 'partial', None])]
    fulfilled_orders = order_analysis[order_analysis['fulfillment_status'] == 'fulfilled']
    
    fulfillment_stats['unfulfilled_orders'] = len(unfulfilled_orders)
    fulfillment_stats['unfulfilled_value'] = unfulfilled_orders['selling_price'].sum()
    fulfillment_stats['pending_shipment_items'] = unfulfilled_orders['quantity'].sum()
    
    fulfillment_stats['fulfilled_orders'] = len(fulfilled_orders)
    fulfillment_stats['fulfilled_value'] = fulfilled_orders['selling_price'].sum()
    
    # Calculate percentages
    if fulfillment_stats['total_orders'] > 0:
        fulfillment_stats['unfulfilled_percentage'] = (fulfillment_stats['unfulfilled_orders'] / fulfillment_stats['total_orders']) * 100
        fulfillment_stats['fulfilled_percentage'] = (fulfillment_stats['fulfilled_orders'] / fulfillment_stats['total_orders']) * 100
    
    return fulfillment_stats
    """Get comparison metrics for selected vs previous period"""
    if sales_df.empty:
        return None
    
    # Current period metrics
    current_revenue = sales_df['selling_price'].sum()
    current_orders = sales_df['order_name'].nunique()
    current_profit = sales_df['profit'].sum()
    
    # Calculate previous period (same length as current period)
    current_days = (st.session_state.date_range_end - st.session_state.date_range_start).days
    previous_start = st.session_state.date_range_start - timedelta(days=current_days)
    previous_end = st.session_state.date_range_start - timedelta(days=1)
    
    # Filter data for previous period
    previous_data = []
    if st.session_state.sales_data:
        for sale in st.session_state.sales_data:
            try:
                sale_date = datetime.strptime(sale['date'], '%Y-%m-%d').date()
                if previous_start.date() <= sale_date <= previous_end.date():
                    previous_data.append(sale)
            except:
                continue
    
    if previous_data:
        previous_df = pd.DataFrame(previous_data)
        previous_revenue = previous_df['selling_price'].sum()
        previous_orders = previous_df['order_name'].nunique()
        previous_profit = previous_df['profit'].sum()
        
        # Calculate changes
        revenue_change = ((current_revenue - previous_revenue) / previous_revenue * 100) if previous_revenue > 0 else 0
        orders_change = ((current_orders - previous_orders) / previous_orders * 100) if previous_orders > 0 else 0
        profit_change = ((current_profit - previous_profit) / previous_profit * 100) if previous_profit > 0 else 0
        
        return {
            'revenue_change': revenue_change,
            'orders_change': orders_change,
            'profit_change': profit_change,
            'previous_revenue': previous_revenue,
            'previous_orders': previous_orders,
            'previous_profit': previous_profit
        }
    
    return None
    """Recalculate profits based on current margin settings"""
    updated_data = []
    
    hoodie_total_cost = st.session_state.hoodie_base_cost + st.session_state.additional_cost
    tshirt_total_cost = st.session_state.tshirt_base_cost + st.session_state.additional_cost
    
    for sale in sales_data:
        updated_sale = sale.copy()
        
        # Determine total cost based on category
        if sale['category'] == 'Hoodies':
            updated_sale['cost_used'] = hoodie_total_cost
        else:  # T-Shirts
            updated_sale['cost_used'] = tshirt_total_cost
        
        # Recalculate profit
        updated_sale['profit'] = sale['selling_price'] - updated_sale['cost_used']
        
        updated_data.append(updated_sale)
    
    return updated_data

def process_orders(orders):
    """Process orders ensuring no duplicates with dynamic profit calculation and fulfillment status"""
    processed_sales = []
    seen_combinations = set()
    
    # Get current cost settings
    hoodie_total_cost = st.session_state.hoodie_base_cost + st.session_state.additional_cost
    tshirt_total_cost = st.session_state.tshirt_base_cost + st.session_state.additional_cost
    
    for order in orders:
        order_name = order.get('name', 'N/A')
        fulfillment_status = order.get('fulfillment_status', 'unfulfilled')  # Get fulfillment status
        financial_status = order.get('financial_status', 'pending')
        
        for line_item in order.get("line_items", []):
            item_id = line_item.get('id')
            combination_key = f"{order_name}_{item_id}"
            
            if combination_key in seen_combinations:
                continue
            seen_combinations.add(combination_key)
            
            item_name = line_item.get("name", "")
            selling_price = float(line_item.get("price", 0))
            quantity = int(line_item.get("quantity", 1))
            
            # Determine category and use dynamic costs
            category = 'Hoodies' if 'hoodie' in item_name.lower() else 'T-Shirts'
            total_cost = hoodie_total_cost if category == 'Hoodies' else tshirt_total_cost
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
                'financial_status': financial_status,
                'fulfillment_status': fulfillment_status  # Add fulfillment status
            })
    
    return processed_sales

def create_premium_metric_card(label, value, delta=None, delta_color="normal"):
    delta_html = f'<div class="metric-delta">{delta}</div>' if delta else ""
    
    return f"""
    <div class="metric-card">
        <div class="metric-value">{value}</div>
        <div class="metric-label">{label}</div>
        {delta_html}
    </div>
    """

# Premium Admin Widget View
if admin_widget_view and st.session_state.sales_data:
    st.markdown("### 🎛️ **SWAWE Command Center**")
    
    sales_df = pd.DataFrame(st.session_state.sales_data)
    
    # Premium Stats Banner
    total_revenue = sales_df['selling_price'].sum()
    total_orders = sales_df['order_name'].nunique()
    total_profit = sales_df['profit'].sum()
    profit_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
    
    st.markdown(f"""
    <div style="
        background: var(--swawe-gradient);
        padding: 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
        position: relative;
        overflow: hidden;
        box-shadow: 0 20px 40px rgba(255, 107, 53, 0.3);
    ">
        <div style="position: relative; z-index: 1;">
            <h2 style="margin: 0; font-size: 1.5rem; font-weight: 700;">Real-Time Business Pulse</h2>
            <div style="display: flex; justify-content: space-around; margin-top: 1.5rem; flex-wrap: wrap;">
                <div style="text-align: center; margin: 0.5rem;">
                    <div style="font-size: 2rem; font-weight: 800;">₹{total_revenue:,.0f}</div>
                    <div style="font-size: 0.9rem; opacity: 0.9;">Total Revenue</div>
                </div>
                <div style="text-align: center; margin: 0.5rem;">
                    <div style="font-size: 2rem; font-weight: 800;">{total_orders:,}</div>
                    <div style="font-size: 0.9rem; opacity: 0.9;">Orders</div>
                </div>
                <div style="text-align: center; margin: 0.5rem;">
                    <div style="font-size: 2rem; font-weight: 800;">{profit_margin:.1f}%</div>
                    <div style="font-size: 0.9rem; opacity: 0.9;">Profit Margin</div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick Actions
    st.markdown("#### 🚀 **Quick Actions**")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Export Analytics", use_container_width=True):
            csv = sales_df.to_csv(index=False)
            st.download_button(
                label="💾 Download Data",
                data=csv,
                file_name=f"swawe_analytics_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
    
    with col2:
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.rerun()
    
    with col3:
        if st.button("🏪 Open Shopify", use_container_width=True):
            st.markdown(f'<meta http-equiv="refresh" content="0; url=https://{SHOPIFY_STORE_URL}/admin">', unsafe_allow_html=True)

# Main Dashboard Content
if not admin_widget_view:
    if page == "Executive Dashboard":
        st.markdown("### 📊 **Business Performance Overview**")
        
        if shopify_connected:
            if st.button("🔄 Refresh Data from Shopify", type="primary"):
                with st.spinner("🔍 Analyzing your SWAWE business data..."):
                    orders = fetch_all_orders()
                    if orders:
                        st.session_state.sales_data = process_orders(orders)
                        unique_orders = len(set(sale['order_name'] for sale in st.session_state.sales_data))
                        st.success(f"✅ Loaded {unique_orders} orders with {len(st.session_state.sales_data)} items!")
                        st.rerun()
        
        if st.session_state.sales_data:
            sales_df = pd.DataFrame(st.session_state.sales_data)
            
            # Premium Metrics with Profit Analysis
            col1, col2, col3, col4 = st.columns(4)
            
            total_revenue = sales_df['selling_price'].sum()
            total_profit = sales_df['profit'].sum()
            profit_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
            unique_orders = sales_df['order_name'].nunique()
            avg_order = sales_df['selling_price'].mean()
            
            with col1:
                st.markdown(create_premium_metric_card("Total Revenue", f"₹{total_revenue:,.0f}"), unsafe_allow_html=True)
            with col2:
                profit_color = "positive" if total_profit > 0 else "negative"
                st.markdown(create_premium_metric_card("Net Profit", f"₹{total_profit:,.0f}", f"{profit_margin:.1f}% margin"), unsafe_allow_html=True)
            with col3:
                st.markdown(create_premium_metric_card("Avg Order Value", f"₹{avg_order:.0f}"), unsafe_allow_html=True)
            with col4:
                st.markdown(create_premium_metric_card("Total Orders", f"{unique_orders:,}"), unsafe_allow_html=True)
            
            else:
                st.warning(f"📅 No data found for the selected date range: {st.session_state.date_range_start.strftime('%B %d, %Y')} - {st.session_state.date_range_end.strftime('%B %d, %Y')}")
                st.info("💡 Try selecting a different date range or refresh your data from Shopify.")
            
            with col1:
                hoodie_data = sales_df[sales_df['category'] == 'Hoodies']
                if len(hoodie_data) > 0:
                    hoodie_profit = hoodie_data['profit'].sum()
                    hoodie_margin = (hoodie_profit / hoodie_data['selling_price'].sum() * 100) if len(hoodie_data) > 0 else 0
                    hoodie_avg_profit = hoodie_data['profit'].mean()
                    
                    st.markdown(f"""
                    <div class="metric-card">
                        <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                            <span style="font-size: 2rem; margin-right: 0.5rem;">🧥</span>
                            <h4 style="margin: 0; color: #FF6B35;">Hoodies Performance</h4>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                            <span>Total Profit:</span><strong>₹{hoodie_profit:,.0f}</strong>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                            <span>Profit Margin:</span><strong>{hoodie_margin:.1f}%</strong>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                            <span>Avg Profit/Item:</span><strong>₹{hoodie_avg_profit:.0f}</strong>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                            <span>Cost Used:</span><strong>₹{st.session_state.hoodie_base_cost + st.session_state.additional_cost}</strong>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            with col2:
                tshirt_data = sales_df[sales_df['category'] == 'T-Shirts']
                if len(tshirt_data) > 0:
                    tshirt_profit = tshirt_data['profit'].sum()
                    tshirt_margin = (tshirt_profit / tshirt_data['selling_price'].sum() * 100) if len(tshirt_data) > 0 else 0
                    tshirt_avg_profit = tshirt_data['profit'].mean()
                    
                    st.markdown(f"""
                    <div class="metric-card">
                        <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                            <span style="font-size: 2rem; margin-right: 0.5rem;">👕</span>
                            <h4 style="margin: 0; color: #FF6B35;">T-Shirts Performance</h4>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                            <span>Total Profit:</span><strong>₹{tshirt_profit:,.0f}</strong>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                            <span>Profit Margin:</span><strong>{tshirt_margin:.1f}%</strong>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                            <span>Avg Profit/Item:</span><strong>₹{tshirt_avg_profit:.0f}</strong>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                            <span>Cost Used:</span><strong>₹{st.session_state.tshirt_base_cost + st.session_state.additional_cost}</strong>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Premium Charts
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
                                       line=dict(color='#FF6B35', width=4),
                                       marker=dict(size=10, color='#FF6B35')))
                fig.add_trace(go.Scatter(x=monthly_data['month'], y=monthly_data['profit'],
                                       mode='lines+markers', name='Profit',
                                       line=dict(color='#00D4AA', width=4),
                                       marker=dict(size=10, color='#00D4AA')))
                
                fig.update_layout(
                    title="📈 Monthly Performance Trend",
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white', size=12),
                    title_font_size=16,
                    xaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
                    yaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
                    legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(color='white'))
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
                           title="📊 Category Performance", barmode='group',
                           color_discrete_sequence=['#FF6B35', '#00D4AA'])
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white', size=12),
                    title_font_size=16,
                    legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(color='white'))
                )
                st.plotly_chart(fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Premium Business Insights
            st.markdown("### 💡 **Business Insights**")
            
            profitable_orders = (sales_df['profit'] > 0).sum()
            profit_rate = (profitable_orders / len(sales_df)) * 100
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"""
                <div class="insight-card">
                    <h4 style="color: #FF6B35; margin-bottom: 1rem; font-size: 1.2rem;">📈 Profitability Analysis</h4>
                    <p style="color: rgba(255,255,255,0.9); line-height: 1.6; font-size: 1rem;">
                    <strong>{profit_rate:.1f}%</strong> of your orders are profitable with an average profit margin of <strong>{profit_margin:.1f}%</strong>.
                    Your best performing category generates <strong>₹{category_data['profit'].max():,.0f}</strong> in profits.
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                best_month = monthly_data.loc[monthly_data['profit'].idxmax(), 'month'] if len(monthly_data) > 0 else "N/A"
                st.markdown(f"""
                <div class="insight-card">
                    <h4 style="color: #FF6B35; margin-bottom: 1rem; font-size: 1.2rem;">🚀 Growth Trends</h4>
                    <p style="color: rgba(255,255,255,0.9); line-height: 1.6; font-size: 1rem;">
                    Your business shows <strong>consistent growth</strong> across multiple months.
                    Best performing month: <strong>{best_month}</strong> with strong profit margins and excellent customer retention.
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
        else:
            st.markdown("""
            <div style="text-align: center; padding: 3rem; background: rgba(255,255,255,0.02); border-radius: 20px; border: 1px solid rgba(255,255,255,0.1);">
                <h3 style="color: #FF6B35; margin-bottom: 1rem;">🚀 Ready to Analyze Your SWAWE Business?</h3>
                <p style="color: rgba(255,255,255,0.8); font-size: 1.1rem; margin-bottom: 2rem;">
                Click the button above to load your Shopify data and unlock powerful business insights.
                </p>
            </div>
            """, unsafe_allow_html=True)

    elif page == "Sales Analytics":
        st.markdown("### 📊 **Sales Analytics & Insights**")
        
        if st.session_state.sales_data:
            # Apply date filtering
            filtered_sales = filter_sales_by_date(st.session_state.sales_data)
            
            if filtered_sales:
                sales_df = pd.DataFrame(filtered_sales)
                
                # Date range info
                total_days = (st.session_state.date_range_end - st.session_state.date_range_start).days
                st.info(f"📅 Analyzing **{total_days} days** of sales data")
                
                # Sales Performance Overview
                col1, col2, col3 = st.columns(3)
                with col1:
                    daily_avg = sales_df.groupby(pd.to_datetime(sales_df['date']).dt.date)['selling_price'].sum().mean()
                    st.metric("📈 Daily Avg Revenue", f"₹{daily_avg:,.0f}")
                with col2:
                    best_day_revenue = sales_df.groupby('date')['selling_price'].sum().max()
                    st.metric("🏆 Best Day Revenue", f"₹{best_day_revenue:,.0f}")
                with col3:
                    total_items = sales_df['quantity'].sum()
                    st.metric("📦 Items Sold", f"{total_items:,}")
                
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                sales_df['date'] = pd.to_datetime(sales_df['date'])
                daily_sales = sales_df.groupby('date').agg({
                    'selling_price': 'sum',
                    'profit': 'sum',
                    'quantity': 'sum'
                }).reset_index()
                
                fig = px.line(daily_sales, x='date', y='selling_price', 
                             title=f"📈 Daily Sales Trend ({st.session_state.date_range_start.strftime('%b %d')} - {st.session_state.date_range_end.strftime('%b %d')})", 
                             color_discrete_sequence=['#FF6B35'])
                fig.update_traces(line=dict(width=4), marker=dict(size=8))
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white', size=12),
                    title_font_size=16
                )
                st.plotly_chart(fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Product Analysis for date range
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                    product_sales = sales_df.groupby('item_name').agg({
                        'selling_price': 'sum',
                        'quantity': 'sum'
                    }).sort_values('selling_price', ascending=False).head(10)
                    
                    fig = px.bar(product_sales, x=product_sales.index, y='selling_price',
                                title="🏆 Top Products in Selected Period",
                                color_discrete_sequence=['#FF6B35'])
                    fig.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='white', size=12),
                        title_font_size=16,
                        xaxis_tickangle=-45
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with col2:
                    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                    category_profit = sales_df.groupby('category')['profit'].sum()
                    fig = px.pie(values=category_profit.values, names=category_profit.index,
                                title="💰 Profit Distribution (Selected Period)",
                                color_discrete_sequence=['#FF6B35', '#00D4AA'])
                    fig.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='white', size=12),
                        title_font_size=16
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.warning("📅 No sales data found for the selected date range.")
        else:
            st.info("🔍 Load data from Executive Dashboard first to see analytics.")

    elif page == "Product Intelligence":
        st.markdown("### 🛍️ **Product Intelligence**")
        
        if st.session_state.sales_data:
            sales_df = pd.DataFrame(st.session_state.sales_data)
            
            # Product Overview Metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("🏷️ Total Products", sales_df['item_name'].nunique())
            with col2:
                avg_price = sales_df['selling_price'].mean()
                st.metric("💰 Avg Product Price", f"₹{avg_price:.0f}")
            with col3:
                best_product = sales_df.groupby('item_name')['profit'].sum().idxmax()
                st.metric("🏆 Best Seller", best_product[:20] + "..." if len(best_product) > 20 else best_product)
            with col4:
                total_items_sold = sales_df['quantity'].sum()
                st.metric("📦 Items Sold", f"{total_items_sold:,}")
            
            # Detailed Product Analysis
            st.markdown("#### 📊 **Product Performance Matrix**")
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            
            product_analysis = sales_df.groupby('item_name').agg({
                'selling_price': ['sum', 'mean', 'count'],
                'profit': ['sum', 'mean'],
                'quantity': 'sum'
            }).round(2)
            
            product_analysis.columns = ['💰 Total Revenue', '💵 Avg Price', '📝 Orders', '💎 Total Profit', '📈 Avg Profit', '📦 Qty Sold']
            product_analysis = product_analysis.sort_values('💰 Total Revenue', ascending=False)
            
            # Style the dataframe
            st.dataframe(
                product_analysis,
                use_container_width=True,
                height=400
            )
            st.markdown('</div>', unsafe_allow_html=True)
            
        else:
            st.info("🔍 Load data from Executive Dashboard first to see product intelligence.")

    elif page == "Data Management":
        st.markdown("### 📁 **Data Management & Export**")
        
        if st.session_state.sales_data:
            sales_df = pd.DataFrame(st.session_state.sales_data)
            
            # Data Overview
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("📋 Total Orders", sales_df['order_name'].nunique())
            with col2:
                st.metric("📝 Line Items", len(sales_df))
            with col3:
                st.metric("💰 Revenue", f"₹{sales_df['selling_price'].sum():,.0f}")
            with col4:
                st.metric("💎 Profit", f"₹{sales_df['profit'].sum():,.0f}")
            
            # Order Range Information
            order_numbers = [int(name.replace('#', '')) for name in sales_df['order_name'].unique() if name.startswith('#')]
            if order_numbers:
                min_order = min(order_numbers)
                max_order = max(order_numbers)
                st.success(f"📊 Order Range: #{min_order} to #{max_order} ({max_order - min_order + 1} orders)")
            
            # Data Preview
            st.markdown("#### 👀 **Data Preview**")
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.dataframe(sales_df.head(20), use_container_width=True, height=400)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Export Section
            st.markdown("#### 💾 **Export Options**")
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📊 Export Complete Dataset", type="primary", use_container_width=True):
                    csv = sales_df.to_csv(index=False)
                    st.download_button(
                        label="💾 Download CSV File",
                        data=csv,
                        file_name=f"swawe_complete_data_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
            
            with col2:
                if st.button("📈 Export Analytics Summary", use_container_width=True):
                    # Create summary data
                    summary_data = {
                        'Metric': ['Total Revenue', 'Total Profit', 'Total Orders', 'Avg Order Value', 'Profit Margin'],
                        'Value': [
                            f"₹{sales_df['selling_price'].sum():,.0f}",
                            f"₹{sales_df['profit'].sum():,.0f}",
                            f"{sales_df['order_name'].nunique():,}",
                            f"₹{sales_df['selling_price'].mean():,.0f}",
                            f"{(sales_df['profit'].sum() / sales_df['selling_price'].sum() * 100):.1f}%"
                        ]
                    }
                    summary_df = pd.DataFrame(summary_data)
                    csv_summary = summary_df.to_csv(index=False)
                    st.download_button(
                        label="💡 Download Summary",
                        data=csv_summary,
                        file_name=f"swawe_summary_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
        else:
            st.info("🔍 No data loaded. Go to Executive Dashboard and refresh data first.")

# Premium Footer
st.markdown("""
<div style="
    margin-top: 4rem; 
    padding: 3rem 2rem; 
    text-align: center; 
    background: linear-gradient(135deg, rgba(255,107,53,0.1) 0%, rgba(26,26,46,0.1) 100%);
    border-top: 1px solid rgba(255,107,53,0.2);
    border-radius: 20px 20px 0 0;
">
    <div style="color: #666; font-size: 1rem; margin-bottom: 1rem;">
        <img src="https://cdn.shopify.com/s/files/1/0604/9733/0266/files/bimi-svg-tiny-12-ps.svg?v=1754005795" 
             style="height: 24px; margin-right: 10px; vertical-align: middle;" 
             alt="SWAWE Logo">
        <strong style="color: #FF6B35;">SWAWE</strong> Dashboard | Fashion Analytics & Business Intelligence
    </div>
    <div style="color: rgba(255,255,255,0.6); font-size: 0.9rem;">
        Powered by advanced analytics • Real-time Shopify integration • Mobile optimized
    </div>
</div>
""", unsafe_allow_html=True)

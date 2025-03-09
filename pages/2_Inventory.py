import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set page configuration
st.set_page_config(
    page_title="Inventory",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
    <style>
    /* Hide sidebar */
    [data-testid="collapsedControl"] {display: none !important;}
    section[data-testid="stSidebar"] {display: none !important;}
    
    /* Prescription Button Styling */
    .prescription-button {
        position: fixed;
        bottom: 2rem;
        left: 2rem;
        z-index: 1000;
        background-color: #2A5DB0;
        color: white !important;
        padding: 0.8rem 1.5rem;
        border-radius: 8px;
        text-decoration: none !important;
        font-weight: 500;
        font-size: 1.2rem;
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        transition: all 0.3s ease;
        box-shadow: 0 2px 6px rgba(0,0,0,0.15);
    }
    .prescription-button:hover {
        background-color: #1e4b8f;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    .inventory-header {
        font-family: 'Georgia', serif;
        font-size: 3.8rem;
        color: #52b788;
        margin-top: 0rem;
        margin-bottom: 0rem;
        text-align: center;
    }
    .inventory-subheader {
        text-align: center;
        margin-top: 0;
        margin-bottom: 1rem;
        color: #666;
    }
    
    /* Search Container Styling */
    .search-container {
        background-color: white;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 1.5rem 0;
    }
    
    /* Results Table Styling */
    .results-container {
        background-color: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-top: 1.5rem;
    }
    
    /* Status Tags */
    .tag {
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: 500;
        margin: 2px;
        display: inline-block;
    }
    .tag-low-stock {
        background-color: #dc3545;
        color: white;
    }
    .tag-expiring-soon {
        background-color: #ffc107;
        color: black;
    }
    .tag-in-stock {
        background-color: #28a745;
        color: white;
    }
    
    /* Stats Card Styling */
    .stats-card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
        height: 100%;
    }
    .stats-number {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2A5DB0;
        margin-bottom: 0.5rem;
    }
    .stats-label {
        color: #666;
        font-size: 1.1rem;
    }
    </style>
    
    <!-- Add Prescription Button -->
    <a href="/" class="prescription-button" target="_self">
        📋 Prescription Processing
    </a>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="inventory-header" style="color: #2A5DB0; font-size: 3.8rem;">📦Inventory</h1>', unsafe_allow_html=True)
st.markdown("<h5 style='text-align: center; margin-top: 0; margin-bottom: 0rem;'>Search and monitor medicine inventory</h5>", unsafe_allow_html=True)

# Initialize backend URL
backend_url = "http://localhost:8000"

# Search Section


# Create full-width search bar
st.markdown('<div style="display: flex; gap: 10px; align-items: center;">', unsafe_allow_html=True)

col1, col2 = st.columns([4,1])
with col1:
    search_term = st.text_input(
        "Search Medicines",
        placeholder="Enter medicine name to search...",
        key="search_input",
        label_visibility="collapsed"
    )
with col2:
    search_button = st.button("Search", type="primary", use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

# Add filter buttons with Streamlit components instead of HTML
st.markdown("""
    <style>
    .filter-button {
        width: 100%;
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.25rem 0;
        font-size: 1rem;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    .filter-button.expired {
        background-color: #dc3545;
        color: white;
    }
    .filter-button.expiring {
        background-color: #ffc107;
        color: black;
    }
    .filter-button.out-of-stock {
        background-color: #6c757d;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# Create columns for filter buttons
col1, col2, col3 = st.columns(3)

with col1:
    expired_btn = st.button("⚠️ Expired", key="expired_btn", use_container_width=True)
with col2:
    expiring_btn = st.button("⏳ Expiring Soon", key="expiring_btn", use_container_width=True)
with col3:
    out_of_stock_btn = st.button("❌ Out of Stock", key="out_of_stock_btn", use_container_width=True)

# Function to fetch and display medicines based on status
def fetch_medicines_by_status(status):
    with st.spinner(f'Fetching {status.replace("_", " ").title()} medicines...'):
        try:
            params = {
                "status_filter": [status],
                "page": 1,
                "page_size": 5000  # Increased to show all results
            }
            
            response = requests.get(
                f"{backend_url}/management/medicines",
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                medicines = data.get("medicines", [])
                
                if medicines:
                    display_data = []
                    for med in medicines:
                        display_data.append({
                            "Medicine Name": med['name'],
                            "Price (₹)": f"₹{float(med['price']):.2f}",
                            "Quantity": med['quantity_available'],
                            "Expiry Date": med.get('expiry_date', ''),
                        })
                    
                    if display_data:
                        # Convert to DataFrame
                        df = pd.DataFrame(display_data)
                        
                        # Display total matches found
                        st.success(f"Found {len(display_data)} medicines with status: {status.replace('_', ' ').title()}")
                        
                        # Display results in table
                        #st.markdown('<div class="results-container">', unsafe_allow_html=True)        
                        st.markdown("""
                            <style>
                            /* Table Styling */
                            [data-testid="stDataFrame"] {
                                width: 100%;
                            }
                            [data-testid="stDataFrame"] > div:first-child {
                                overflow-x: auto;
                            }
                            [data-testid="stDataFrame"] table {
                                width: 100%;
                                border-collapse: separate;
                                border-spacing: 0;
                                font-size: 14px;
                            }
                            [data-testid="stDataFrame"] th {
                                background-color: #f8f9fa;
                                padding: 12px 16px !important;
                                border-bottom: 2px solid #dee2e6;
                                font-weight: 600;
                                color: #333;
                                text-align: left;
                                white-space: nowrap;
                            }
                            [data-testid="stDataFrame"] td {
                                padding: 12px 16px !important;
                                border-bottom: 1px solid #dee2e6;
                                color: #333;
                                background-color: white;
                            }
                            [data-testid="stDataFrame"] tr:hover td {
                                background-color: #f5f5f5;
                            }
                            /* Column Widths */
                            [data-testid="stDataFrame"] td:nth-child(1) {
                                min-width: 300px;  /* Medicine Name column */
                                max-width: 500px;
                                white-space: normal;
                                word-wrap: break-word;
                            }
                            [data-testid="stDataFrame"] td:nth-child(2) {
                                min-width: 100px;  /* Price column */
                            }
                            [data-testid="stDataFrame"] td:nth-child(3) {
                                min-width: 100px;  /* Quantity column */
                            }
                            [data-testid="stDataFrame"] td:nth-child(4) {
                                min-width: 120px;  /* Expiry Date column */
                            }
                            </style>
                        """, unsafe_allow_html=True)
                        st.dataframe(
                            df,
                            column_config={
                                "Medicine Name": st.column_config.TextColumn(
                                    "Medicine Name",
                                    width="large",
                                    help="Full medicine name"
                                ),
                                "Price (₹)": st.column_config.TextColumn(
                                    "Price (₹)",
                                    width="small"
                                ),
                                "Quantity": st.column_config.NumberColumn(
                                    "Quantity",
                                    width="small",
                                    format="%d"
                                ),
                                "Expiry Date": st.column_config.DateColumn(
                                    "Expiry Date",
                                    width="medium",
                                    format="YYYY-MM-DD"
                                )
                            },
                            hide_index=True,
                            use_container_width=True
                        )
                        st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        st.warning(f"No medicines found with status: {status.replace('_', ' ').title()}")
                else:
                    st.warning(f"No medicines found with status: {status.replace('_', ' ').title()}")
            else:
                st.error("Error fetching data from the server.")
        except Exception as e:
            st.error(f"Error: {str(e)}")

# Handle button clicks
if expired_btn:
    fetch_medicines_by_status("expired")
elif expiring_btn:
    fetch_medicines_by_status("expiring_soon")
elif out_of_stock_btn:
    fetch_medicines_by_status("out_of_stock")

# Process search when button is clicked
if search_button or search_term:
    with st.spinner(f'Searching medicines...'):
        try:
            # Call FastAPI endpoint for full inventory search
            params = {
                "search": search_term if search_term else "",
                "page": 1,
                "page_size": 1000  # Increased to show all results
            }
            
            response = requests.get(
                f"{backend_url}/management/medicines",
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                medicines = data.get("medicines", [])
                
                if medicines:
                    # Prepare data for display
                    display_data = []
                    for med in medicines:
                        
                        display_data.append({
                            "Medicine Name": med['name'],
                            "Price (₹)": f"₹{float(med['price']):.2f}",
                            "Quantity": med['quantity_available'],
                            "Expiry Date": med.get('expiry_date', ''),
                        })
                    
                    if display_data:
                        # Convert to DataFrame
                        df = pd.DataFrame(display_data)
                        
                        # Display total matches found
                        st.write(f"Found {len(display_data)} medicines matching your search.")
                        
                        # Display results in table
                        # st.markdown('<div class="results-container">', unsafe_allow_html=True)
                        st.markdown("""
                            <style>
                            /* Table Styling */
                            [data-testid="stDataFrame"] {
                                width: 100%;
                            }
                            [data-testid="stDataFrame"] > div:first-child {
                                overflow-x: auto;
                            }
                            [data-testid="stDataFrame"] table {
                                width: 100%;
                                border-collapse: separate;
                                border-spacing: 0;
                                font-size: 14px;
                            }
                            [data-testid="stDataFrame"] th {
                                background-color: #f8f9fa;
                                padding: 12px 16px !important;
                                border-bottom: 2px solid #dee2e6;
                                font-weight: 600;
                                color: #333;
                                text-align: left;
                                white-space: nowrap;
                            }
                            [data-testid="stDataFrame"] td {
                                padding: 12px 16px !important;
                                border-bottom: 1px solid #dee2e6;
                                color: #333;
                                background-color: white;
                            }
                            [data-testid="stDataFrame"] tr:hover td {
                                background-color: #f5f5f5;
                            }
                            /* Column Widths */
                            [data-testid="stDataFrame"] td:nth-child(1) {
                                min-width: 300px;  /* Medicine Name column */
                                max-width: 500px;
                                white-space: normal;
                                word-wrap: break-word;
                            }
                            [data-testid="stDataFrame"] td:nth-child(2) {
                                min-width: 100px;  /* Price column */
                            }
                            [data-testid="stDataFrame"] td:nth-child(3) {
                                min-width: 100px;  /* Quantity column */
                            }
                            [data-testid="stDataFrame"] td:nth-child(4) {
                                min-width: 120px;  /* Expiry Date column */
                            }
                            </style>
                        """, unsafe_allow_html=True)
                        st.dataframe(
                            df,
                            column_config={
                                "Medicine Name": st.column_config.TextColumn(
                                    "Medicine Name",
                                    width="large",
                                    help="Full medicine name"
                                ),
                                "Price (₹)": st.column_config.TextColumn(
                                    "Price (₹)",
                                    width="small"
                                ),
                                "Quantity": st.column_config.NumberColumn(
                                    "Quantity",
                                    format="%d"
                                ),
                                "Expiry Date": st.column_config.DateColumn(
                                    "Expiry Date",
                                    width="medium",
                                    format="YYYY-MM-DD"
                                )
                            },
                            hide_index=True,
                            use_container_width=True
                        )
                        st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        st.info("No medicines found matching your search.")
                else:
                    st.info("No medicines found matching your search.")
            else:
                st.error("Error fetching data from the server.")
        except Exception as e:
            st.error(f"Error: {str(e)}")


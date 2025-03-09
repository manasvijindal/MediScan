import streamlit as st
import google.generativeai as genai
from PIL import Image
import os
from dotenv import load_dotenv
import requests
import re
import json
import pandas as pd
from fpdf import FPDF
import datetime
import sys
from pathlib import Path
import time

# Load environment variables
load_dotenv()

# Configure Google API
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

# Set page configuration
st.set_page_config(
    page_title="MediScan",
    page_icon="🩺",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Hide sidebar with minimal CSS
st.markdown("""
    <style>
    [data-testid="collapsedControl"] {display: none !important;}
    section[data-testid="stSidebar"] {display: none !important;}
    
    /* Inventory Button Styling */
    .inventory-button {
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
    .inventory-button:hover {
        background-color: #1e4b8f;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    .page-header {
        font-size: 2rem;
        color: #1E88E5;
        margin-bottom: 1rem;
    }
    .cart-item {
        padding: 10px;
        background-color: #f8f9fa;
        border-radius: 5px;
        margin: 5px 0;
    }
    .cart-section {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .cart-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;
    }
    .cart-items {
        display: flex;
        gap: 10px;
        overflow-x: auto;
        padding: 10px 0;
    }
    .cart-item {
        min-width: 200px;
        border: 1px solid #eee;
        padding: 10px;
        border-radius: 5px;
    }
    /* Medicine tile grid layout */
    .medicine-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 0.8rem;
        margin-top: 1rem;
    }
    .medicine-tile {
        background-color: #f8f9fa;
        border-radius: 6px;
        padding: 0.8rem 1rem;
        transition: all 0.3s ease;
        border: 1px solid #e9ecef;
        display: flex;
        flex-direction: column;
    }
    .medicine-tile:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border-color: #2A5DB0;
    }
    .medicine-name {
        font-size: 1.3rem;
        color: black;
        text-align: left;
        margin-bottom: 0.4rem;
    }
    .medicine-meta {
        color: #666;
        font-size: 0.9rem;
        text-align: right;
    }
    .medicine-details-container {
        display: none;
        margin-bottom: 2rem;
        background-color: white;
        border-radius: 10px;
        padding: 2rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        border: 1px solid #e9ecef;
    }
    .medicine-details-container.active {
        display: block;
    }
    .details-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1.5rem;
    }
    .details-title {
        font-size: 1.5rem;
        color: #2A5DB0;
        font-weight: bold;
    }
    .close-button {
        background: none;
        border: none;
        color: #666;
        cursor: pointer;
        font-size: 1.5rem;
        padding: 0.5rem;
    }
    .close-button:hover {
        color: #2A5DB0;
    }
    .details-content {
        display: grid;
        grid-template-columns: 1fr 2fr;
        gap: 2rem;
    }
    .substitute-tile {
        background-color: #f0f7ff;
        border: 1px solid #cce5ff;
    }
    .substitute-tile:hover {
        border-color: #2A5DB0;
        background-color: #e6f3ff;
    }
    </style>
    
    <!-- Add Inventory Button -->
    <a href="Inventory" class="inventory-button" target="_self">
        📦 Inventory Management
    </a>
""", unsafe_allow_html=True)

# Define backend URL as a global variable at the top level
backend_url = "http://localhost:8000"

# Initialize session state variables
if 'backend_url' not in st.session_state:
    st.session_state.backend_url = backend_url

def initialize_cart():
    """Ensures we have a 'cart' dict in session_state."""
    if 'cart' not in st.session_state:
        st.session_state.cart = {}

def analyze_prescription(image, prompt):
    """Calls Gemini with [prompt, image], returns text or an error string."""
    try:
        response = model.generate_content([prompt, image])
        return response.text
    except Exception as e:
        return f"Error calling Gemini: {str(e)}"

def generate_invoice():
    """Generate a PDF invoice based on items in st.session_state.cart."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    
    # Add header
    pdf.cell(0, 10, 'Order Invoice', 0, 1, 'C')
    pdf.line(10, 30, 200, 30)
    
    # Date/time
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f'Date: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', 0, 1)
    
    # Table headers
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(80, 10, 'Medicine', 1)
    pdf.cell(30, 10, 'Quantity', 1)
    pdf.cell(40, 10, 'Price', 1)
    pdf.cell(40, 10, 'Total', 1)
    pdf.ln()
    
    # Table rows
    total = 0
    pdf.set_font('Arial', '', 12)
    for med, details in st.session_state.cart.items():
        qty = details['quantity']
        price = details['price']
        subtotal = price * qty
        total += subtotal

        pdf.cell(80, 10, med, 1)
        pdf.cell(30, 10, str(qty), 1)
        pdf.cell(40, 10, f"Rs. {price:.2f}", 1)
        pdf.cell(40, 10, f"Rs. {subtotal:.2f}", 1)
        pdf.ln()
    
    pdf.cell(150, 10, 'Total Amount:', 1)
    pdf.cell(40, 10, f"Rs. {total:.2f}", 1)
    
    return pdf.output(dest='S').encode('latin1')

def process_substitutes(substitutes, original_med_info):
    """Process substitutes and return their details"""
    results = []
    for substitute in substitutes:
        try:
            resp = requests.get(
                f"{st.session_state.backend_url}/search_medicine/",
                params={"query": substitute},
                timeout=10
            )
            if resp.status_code == 200:
                sub_matches = resp.json()
                if isinstance(sub_matches, list) and len(sub_matches) > 0:
                    best_match = sub_matches[0]
                    if int(best_match.get('quantity_available', 0)) > 0:
                        sub_med_info = {
                            "name": best_match.get('name', 'Unknown'),
                            "composition": best_match.get('short_composition1', ''),
                            "therapeutic_class": best_match.get('therapeutic_class', ''),
                            "uses": [best_match.get(f'use{i}', '') for i in range(5) if best_match.get(f'use{i}')],
                            "action": best_match.get('action', ''),
                            "price": float(best_match.get('price', 0)),
                            "quantity_available": int(best_match.get('quantity_available', 0)),
                            "pack_size_label": best_match.get('pack_size_label', '')
                        }
                        results.append((substitute, sub_med_info, best_match))
        except requests.exceptions.RequestException as exc:
            st.error(f"Network error while searching for substitute {substitute}: {str(exc)}")
        except Exception as exc:
            st.error(f"Error processing substitute {substitute}: {str(exc)}")
    return results

def process_prescription(image, prompt):
    """Process the prescription image and return analysis results."""
    gemini_text = analyze_prescription(image, prompt)

    if not gemini_text:
        st.error("⚠️ Could not analyze the prescription. Please ensure the image is clear and contains a valid prescription.")
        return None

    try:
        # Extract JSON from Gemini output
        match = re.search(r'(\{.*\})', gemini_text, re.DOTALL)
        if not match:
            st.error("⚠️ Invalid prescription format. Please provide a clear image of a valid prescription.")
            return None

        # Get the JSON part
        json_str = match.group(1)
        try:
            parsed = json.loads(json_str)
        except json.JSONDecodeError:
            st.error("⚠️ Invalid prescription format. Please provide a clear image of a valid prescription.")
            return None
        
        # Store medicines data in session state
        st.session_state.medicines = parsed.get("medicines", [])
        
        # Check for valid doctor's license number
        doctor_info = parsed.get("doctor_info", {})
        license_number = doctor_info.get("license_number")
        
        # Validate license number
        if not license_number or not isinstance(license_number, str) or license_number.strip().lower() in ["not available", "n/a", "-", "...", "", "none", "null"]:
            st.error("⚠️ Invalid prescription: Doctor's registration/license number not found. Please provide a valid prescription with the doctor's registration number.")
            return None
            
        # If license number is valid, display it
        st.success(f"✅ Valid Prescription - Doctor's Registration Number: {license_number.strip()}")
            
        # Proceed with medicines
        medicines = parsed.get("medicines", [])
        if not medicines:
            st.warning("No medicines found in the prescription.")
            return None

        # Display only the medications section
        st.subheader("📋 *Prescribed Medications*")
        
        # Format medicines data in plain text
        medicines_text = ""
        for med in medicines:
            name = med.get("medicine_name", "-")
            strength = med.get("strength_dosage", "-")
            quantity = med.get("quantity", "-")
            frequency = med.get("frequency", "-")
            instructions = med.get("instructions", "-")
            
            medicines_text += f"""
            <div class="medicine-card">
                <div class="medicine-header">
                    <span class="medicine-name">{name}</span>
                </div>
                <div class="medicine-details">
                    <div class="detail-row">
                        <span class="detail-label">💊 Strength:</span>
                        <span class="detail-value">{strength}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">📦 Quantity:</span>
                        <span class="detail-value">{quantity}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">⏰ Frequency:</span>
                        <span class="detail-value">{frequency}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">📝 Instructions:</span>
                        <span class="detail-value">{instructions}</span>
                    </div>
                </div>
            </div>
            """

        st.markdown(f"""
            <style>
                .medicine-card {{
                    background-color: white;
                    border-radius: 10px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    margin: 1rem 0;
                    padding: 1.5rem;
                    border: 1px solid #e0e0e0;
                }}
                .medicine-header {{
                    margin-bottom: 1rem;
                    padding-bottom: 0.5rem;
                    border-bottom: 2px solid #f0f0f0;
                }}
                .medicine-name {{
                    font-size: 1.25rem;
                    font-weight: 600;
                    color: #2A5DB0;
                }}
                .medicine-details {{
                    display: grid;
                    gap: 0.8rem;
                }}
                .detail-row {{
                    display: flex;
                    align-items: baseline;
                    gap: 1rem;
                }}
                .detail-label {{
                    min-width: 120px;
                    font-weight: 500;
                    color: #555;
                }}
                .detail-value {{
                    color: #333;
                    flex: 1;
                }}
            </style>
            <div class="prescription-details">
                {medicines_text}
            </div>
        """, unsafe_allow_html=True)

        # Gather all medicine names and split combined medicines
        med_names = []
        for m in medicines:
            name = m.get("medicine_name")
            if name and isinstance(name, str):
                name = name.strip()
                if name.lower() not in ["not available", "n/a", "-"]:
                    # Split medicine names if they contain plus signs
                    split_names = [n.strip() for n in name.split("+")]
                    med_names.extend(split_names)

        # Remove duplicates while preserving order
        med_names = list(dict.fromkeys(med_names))

        if not med_names:
            st.warning("No valid medicine names found in the prescription.")
            return None

        return med_names
        
    except Exception as e:
        st.error("⚠️ Invalid prescription format. Please provide a clear image of a valid prescription.")
        return None

# Initialize cart
initialize_cart()

# Remove the top cart display section and keep only the header
st.markdown('<h1 class="page-header" style="font-family: \'Georgia\', serif; text-align: center; font-size: 3.8rem; color: #2A5DB0; margin-top: 0rem; margin-bottom: 0rem;">🩺MediScan</h1>', unsafe_allow_html=True)
st.write("<h5 style='text-align: center; margin-top: 0; margin-bottom: 0rem;'>Your AI-powered prescription analyzer & medicine finder</h5>", unsafe_allow_html=True)

# File uploader for prescription image
uploaded_file = st.file_uploader("📂 **Upload Prescription Image with Valid Doctor's License Number** (JPG, PNG, JPEG)", type=['jpg', 'jpeg', 'png'], label_visibility="visible", key="prescription_uploader", help="Upload a clear image of your prescription")
st.markdown("<style>div[data-testid='stFileUploader'] label {font-size: 1.7rem !important;}</style>", unsafe_allow_html=True)

# Show welcome box only when no file is uploaded
if not uploaded_file:
    st.markdown("""
        <div style="border-radius: 10px; padding: 20px; background-color: #F5F7FA; text-align: center; box-shadow: 2px 2px 12px rgba(0,0,0,0.1);">
            <h2 style="font-size: 36px; color: #2A5DB0;"><em>Scan it. Find it. Get it.</em></h2>
            <hr style="border: 1px solid #D1D5DB; margin: 8px 0;">
            <h4>🚀 What Can This Do?</h4>
            <div style="text-align: left; font-size: 18px;">
                📸 Upload a <strong>prescription image</strong> to extract medicine details.<br>
                🔍 <strong>Smart medicine matching</strong> to check availability in the inventory.<br>
                📦 Add medicines to <strong>cart and generate an order summary</strong>.<br>
                📜 Get a <strong>quick AI-generated summary</strong> of medicines.
            </div>
        </div>
    """, unsafe_allow_html=True)

if uploaded_file:
    # Show the uploaded image
    image = Image.open(uploaded_file)
    st.image(image, caption="📜 Uploaded Prescription", use_column_width=True)

    # Prompt for Gemini
    prompt = """
    Analyze this prescription image and provide **TWO sections** in your answer.

    SECTION 1: (To be displayed to the user but don't write "Section 1:" in the response)
    1. DOCTOR INFORMATION:
        - Look for any of these variations of license number:
          * Registration No./Reg No./Reg.No/Registration Number
          * License No./Lic No./Lic.No/License Number/Licence No.
          * Medical Registration No./Medical Reg No.
          * MCI Reg No./MCI Registration
          * State Medical Council No.
        If found, include it in the response.

    2. MEDICATIONS:
    For each medication, provide the following information in a clear format:
    • Medicine Name
      - Strength/Dosage
      - Quantity
      - Frequency
      - Special Instructions

    Important Notes:
    - Extract and clearly display the doctor's registration/license number if found
    - If medicines are combined with '+' signs (e.g., "Medicine1 + Medicine2"), split them and list them as separate entries
    - Each medicine should be listed separately, even if they are prescribed together
    - For combined medicines, split the strength/dosage appropriately for each component
    - Use "-" for any information that is not visible or unclear
    - Keep entries concise but informative

    SECTION 2: (JSON BLOCK - This is NOT TO BE DISPLAYED TO THE USER, ONLY PASSED TO THE BACKEND)

    {
      "doctor_info": {
        "license_number": "...",
        "license_type": "..."
      },
      "medicines": [
        {
          "medicine_name": "...",
          "strength_dosage": "...",
          "quantity": "...",
          "frequency": "...",
          "instructions": "..."
        }
      ]
    }
    """

    col1, col2 = st.columns([2, 1])
    
    with col1:
        if st.button("Analyze"):
            # Clear previous cart and search results when analyzing new prescription
            st.session_state.cart = {}
            if 'search_results' in st.session_state:
                del st.session_state.search_results
            
            # Add loading indicator
            with st.spinner("Extracting medicine details from Prescription"):
                # Add a small delay to show the spinner
                time.sleep(1)
                
                med_names = process_prescription(image, prompt)
                if med_names:
                    # Call FastAPI for fuzzy matching
                    st.subheader("*Available Medicines & Alternatives*")

                    all_matches = []
                    for med in med_names:
                        with st.spinner(f"Searching DB for '{med}'..."):
                            try:
                                resp = requests.get(f"{backend_url}/search_medicine/", params={"query": med})
                                if resp.status_code == 200:
                                    data = resp.json()
                                    all_matches.append((med, data))
                                else:
                                    all_matches.append((med, f"Error: {resp.status_code}"))
                            except Exception as exc:
                                all_matches.append((med, f"Error calling FastAPI: {exc}"))

                    # Save results so they persist across reruns
                    st.session_state.search_results = all_matches

    # If we have search results in session_state, display them
    if 'search_results' in st.session_state:
        all_matches = st.session_state.search_results

        # Single form for adjusting quantities
        with st.form("update_cart_form"):
            for med, matches in all_matches:
                st.markdown(f"### 💊 Matches for {med}")

                if isinstance(matches, dict) and "message" in matches:
                    st.write(matches["message"])
                elif isinstance(matches, list) and len(matches) > 0:
                    # Create grid container for the tiles
                    st.markdown('<div class="medicine-grid">', unsafe_allow_html=True)
                    
                    for row in matches:
                        name = row.get('name', 'Unknown')
                        if name:
                            name = name[0].upper() + name[1:].lower()  # Title-case
                        price = float(row.get('price', 0))
                        qty_avail = int(row.get('quantity_available', 0))
                        similarity = float(row.get('similarity_score', 0))

                        # Create tile with basic info and handle out of stock
                        stock_status = "text-danger" if qty_avail == 0 else ""
                        stock_text = "Out of Stock" if qty_avail == 0 else f"{qty_avail} available"
                        
                        st.markdown(f"""
                            <div class="medicine-tile">
                                <div class="medicine-name">{name}</div>
                                <div style="margin-bottom: 0.4rem;">
                                    <span style="color: #2A5DB0; font-weight: 500;">
                                        Match: {similarity*100:.1f}%
                                    </span>
                                </div>
                                <div class="medicine-meta">
                                    ₹{price} | <span class="{stock_status}">{stock_text}</span>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)

                        # Create expander for details (for both in-stock and out-of-stock items)
                        with st.expander(f"View Details"):
                            if qty_avail == 0:
                                st.error("⚠️ This medicine is currently out of stock")
                            
                            # Get prescribed quantity from medicines list
                            prescribed_qty = 0
                            if 'medicines' in st.session_state:
                                for m in st.session_state.medicines:
                                    if m.get("medicine_name", "").strip() == med:
                                        qty_str = m.get("quantity", "0").strip()
                                        try:
                                            prescribed_qty = int(qty_str)
                                        except ValueError:
                                            prescribed_qty = 0
                            
                            # Get pack size and calculate suggested quantity
                            pack_size = 1
                            pack_size_label = row.get('pack_size_label', '')
                            if pack_size_label:
                                # Extract number from pack size label (e.g., "Strip of 10" -> 10)
                                pack_size_match = re.search(r'\d+', pack_size_label)
                                if pack_size_match:
                                    pack_size = int(pack_size_match.group())
                            
                            # Only show suggestion for in-stock items
                            if qty_avail > 0:
                                # Calculate suggested quantity in packs
                                suggested_packs = 0
                                if pack_size > 0 and prescribed_qty > 0:
                                    suggested_packs = (prescribed_qty + pack_size - 1) // pack_size  # Round up division
                                
                                if pack_size > 1 and prescribed_qty > 0:
                                    st.success(f"💡 Suggestion: Order {suggested_packs} packs to get {suggested_packs * pack_size} units")
                                
                                # Add quantity selector
                                cart_item = st.session_state.cart.get(name, {})
                                current_qty = cart_item.get('quantity', 0)

                                new_qty = st.number_input(
                                    f"Select number of packs for {name} (max {qty_avail})",
                                    min_value=0,
                                    max_value=qty_avail,
                                    value=current_qty,
                                    key=f"{name}_qty"
                                )

                                if pack_size > 1:
                                    st.write(f"Total units: {new_qty * pack_size}")

                            # Create table data
                            table_data = []
                            fields_to_display = [
                                ("Price(₹)", "price"),
                                ("Quantity Available", "quantity_available"), 
                                ("Pack Size", "pack_size_label"),
                                ("Expiry Date", "expiry_date"),
                                ("Composition", "short_composition1")
                            ]

                            # Add basic fields
                            for label, key in fields_to_display:
                                val = row.get(key) if key != "price" else price
                                # Special handling for expiry date to ensure it's shown
                                if key == "expiry_date":
                                    expiry_val = row.get(key)
                                    if expiry_val and str(expiry_val).strip().lower() not in ["unknown", "n/a", "not available", "-", "", "none", "null"]:
                                        table_data.append([label, str(expiry_val)])
                                # Handle other fields
                                elif val and str(val).strip().lower() not in ["unknown", "n/a", "not available", "-", "", "none", "null"]:
                                    table_data.append([label, str(val)])

                            # Add uses if available
                            uses = [use for use in (row.get(f'use{i}', '') for i in range(5)) 
                                   if use and use.lower() not in ["unknown", "n/a", "not available", "-", ""]]
                            if uses:
                                table_data.append(["Uses", "<br>".join([f"• {use}" for use in uses])])

                            # Add side effects if available
                            side_effects = [effect for effect in (row.get(f'sideEffect{i}', '') for i in range(5)) 
                                          if effect and effect.lower() not in ["unknown", "n/a", "not available", "-", ""]]
                            if side_effects:
                                table_data.append(["Side Effects", "<br>".join([f"• {effect}" for effect in side_effects])])

                            # Add substitutes if available
                            substitutes = [sub for sub in (row.get(f'substitute{i}', '') for i in range(5)) 
                                         if sub and sub.lower() not in ["unknown", "n/a", "not available", "-", ""]]
                            if substitutes:
                                table_data.append(["Substitutes", "<br>".join([f"• {sub}" for sub in substitutes])])

                            # Create and display the table
                            if table_data:
                                df = pd.DataFrame(table_data, columns=['Field', 'Value'])
                                table_html = f"""<table>
    <thead>
        <tr>
            <th>Field</th>
            <th>Value</th>
        </tr>
    </thead>
    <tbody>
        {"".join(f'<tr><td><strong>{row[0]}</strong></td><td class="value-cell">{row[1]}</td></tr>' for row in table_data)}
    </tbody>
</table>"""
                                st.markdown(table_html, unsafe_allow_html=True)

                            # If medicine is out of stock, search for substitutes
                            if qty_avail == 0:
                                # Get all substitutes
                                substitutes = []
                                for i in range(5):  # Check substitute0 through substitute4
                                    sub = row.get(f'substitute{i}')
                                    if sub and isinstance(sub, str) and sub.strip().lower() not in ["unknown", "n/a", "not available", "-", "", "none", "null"]:
                                        substitutes.append(sub.strip())

                                if substitutes:
                                    st.markdown("#### 🔄 Available Substitutes")
                                    
                                    # Get original medicine details for comparison
                                    original_med_info = {
                                        "name": name,
                                        "composition": row.get('short_composition1', ''),
                                        "therapeutic_class": row.get('therapeutic_class', ''),
                                        "uses": [row.get(f'use{i}', '') for i in range(5) if row.get(f'use{i}')],
                                        "action": row.get('action', '')
                                    }
                                    
                                    # Process all substitutes
                                    substitute_results = process_substitutes(substitutes, original_med_info)
                                    
                                    for substitute, sub_med_info, best_match in substitute_results:
                                        # Generate comparison prompt for Gemini
                                        comparison_prompt = f"""
                                        Compare these two medicines and provide a SHORT analysis about their substitutability:

                                        Original Medicine:
                                        - Name: {original_med_info['name']}
                                        - Composition: {original_med_info['composition']}
                                        - Therapeutic Class: {original_med_info['therapeutic_class']}
                                        - Uses: {', '.join(original_med_info['uses'])}
                                        - Action: {original_med_info['action']}

                                        Substitute Medicine:
                                        - Name: {sub_med_info['name']}
                                        - Composition: {sub_med_info['composition']}
                                        - Therapeutic Class: {sub_med_info['therapeutic_class']}
                                        - Uses: {', '.join(sub_med_info['uses'])}
                                        - Action: {sub_med_info['action']}

                                        Provide a concise 2-3 sentence analysis focusing on:
                                        1. Whether they have matching therapeutic properties
                                        2. If the substitute is safe to use
                                        3. Compare their compositions and highlight any differences
                                        End with a clear YES/NO recommendation.
                                        """

                                        try:
                                            # Get Gemini's analysis
                                            response = model.generate_content(comparison_prompt)
                                            analysis = response.text

                                            # Display substitute information with analysis
                                            st.markdown(f"""
                                                <div style="padding: 20px; border: 1px solid #e0e0e0; border-radius: 10px; margin: 10px 0;">
                                                    <h4 style="color: #2A5DB0;">Alternative Option for {original_med_info['name']}: {sub_med_info['name']}</h4>
                                                    <div style="margin: 15px 0;">
                                                        <strong>Price:</strong> ₹{sub_med_info['price']}<br>
                                                        <strong>Available Quantity:</strong> {sub_med_info['quantity_available']}<br>
                                                        <strong>Composition:</strong> {sub_med_info['composition']}<br>
                                                        <strong>Therapeutic Class:</strong> {sub_med_info['therapeutic_class']}
                                                    </div>
                                                    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 10px 0;">
                                                        <strong>AI Analysis:</strong><br>
                                                        {analysis}
                                                    </div>
                                                </div>
                                            """, unsafe_allow_html=True)

                                            # Add to cart option if recommended
                                            if "YES" in analysis.upper():
                                                sub_name = sub_med_info['name']
                                                sub_qty = sub_med_info['quantity_available']
                                                
                                                # Get pack size for substitute
                                                pack_size = 1
                                                pack_size_label = sub_med_info['pack_size_label']
                                                if pack_size_label:
                                                    pack_size_match = re.search(r'\d+', pack_size_label)
                                                    if pack_size_match:
                                                        pack_size = int(pack_size_match.group())
                                                
                                                # Create unique key for substitute quantity input
                                                qty_key = f"substitute_{sub_name}_qty"
                                                cart_item = st.session_state.cart.get(sub_name, {})
                                                current_qty = cart_item.get('quantity', 0)
                                                
                                                col1, col2 = st.columns([3, 1])
                                                with col1:
                                                    new_qty = st.number_input(
                                                        "",
                                                        min_value=0,
                                                        max_value=sub_qty,
                                                        value=current_qty,
                                                        key=qty_key,
                                                        label_visibility="collapsed"
                                                    )
                                                    
                                                    # Update cart when quantity changes
                                                    if new_qty > 0:
                                                        st.session_state.cart[sub_name] = {
                                                            "price": sub_med_info['price'],
                                                            "quantity": new_qty
                                                        }
                                                    elif sub_name in st.session_state.cart and new_qty == 0:
                                                        st.session_state.cart.pop(sub_name, None)
                                                        
                                                with col2:
                                                    if pack_size > 1:
                                                        st.markdown(f"""
                                                            <div style="
                                                                background-color: #f0f7ff;
                                                                padding: 8px 12px;
                                                                border-radius: 4px;
                                                                border: 1px solid #cce5ff;
                                                                text-align: center;
                                                                height: 38px;
                                                                line-height: 22px;
                                                                margin-top: 2px;
                                                            ">
                                                                Pack: {pack_size} units
                                                            </div>
                                                        """, unsafe_allow_html=True)

                                        except Exception as e:
                                            st.error(f"Error analyzing substitute: {str(e)}")
                                else:
                                    st.info("No substitutes available for this medicine")

                    st.markdown('</div>', unsafe_allow_html=True)

            # Update Cart button
            submitted = st.form_submit_button("Generate Order")
            if submitted:
                cart_updated = False  # Flag to track if any changes were made
                # Update the cart based on all the number inputs
                for med, matches in all_matches:
                    if isinstance(matches, list) and len(matches) > 0:
                        for row in matches:
                            item_name = row.get('name', 'Unknown')
                            if item_name:
                                item_name = item_name[0].upper() + item_name[1:].lower()
                            price = float(row.get('price', 0))
                            qty_avail = int(row.get('quantity_available', 0))

                            key_qty = f"{item_name}_qty"
                            if key_qty in st.session_state:
                                chosen_qty = st.session_state[key_qty]
                                if chosen_qty > 0:
                                    st.session_state.cart[item_name] = {
                                        "price": price,
                                        "quantity": chosen_qty
                                    }
                                    cart_updated = True
                                elif item_name in st.session_state.cart:
                                    # If zero and item exists in cart, remove it
                                    st.session_state.cart.pop(item_name, None)
                                    cart_updated = True
                
                if cart_updated:
                    st.success("Cart updated successfully!")
                else:
                    st.info("No changes made to cart. Select quantities and try again.")

        # End of update_cart_form
        
        # Initialize session state for patient details if not exists
        if 'patient_details' not in st.session_state:
            st.session_state.patient_details = {
                'name': '',
                'age': 25,
                'gender': 'Male',
                'date': datetime.datetime.now()
            }
        
        # Display order summary and invoice generation outside the cart form
        if st.session_state.cart:
            st.markdown("""
                <div style='margin-top: 20px; padding: 20px; border: 1px solid #eee; border-radius: 8px;'>
                    <div style='display: flex; align-items: center; gap: 8px; margin-bottom: 15px;'>
                        <span style='font-size: 1.2rem;'>🛒</span>
                        <span style='font-size: 1.2rem; color: #2A5DB0;'>Order Summary</span>
                    </div>
            """, unsafe_allow_html=True)
            
            total = 0
            for item, details in st.session_state.cart.items():
                qty = details['quantity']
                price = details['price']
                subtotal = qty * price
                total += subtotal
                
                st.markdown(f"""
                    <div style='display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #eee;'>
                        <div style='flex: 2;'>{item}</div>
                        <div style='flex: 1; text-align: center;'>{qty}</div>
                        <div style='flex: 1; text-align: center;'>₹{price:.2f}</div>
                        <div style='flex: 1; text-align: right;'>₹{subtotal:.2f}</div>
                    </div>
                """, unsafe_allow_html=True)
            
            st.markdown(f"""
                    <div style='display: flex; justify-content: space-between; padding: 12px 0; border-top: 2px solid #ddd; margin-top: 8px;'>
                        <div style='font-weight: 500;'>Total Amount:</div>
                        <div style='font-weight: 500;'>₹{total:.2f}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Add patient details form directly below order summary
            col1, col2 = st.columns(2)
            with col1:
                name_changed = st.text_input("Patient Name", value=st.session_state.patient_details['name'], key="patient_name")
                if name_changed != st.session_state.patient_details['name']:
                    st.session_state.patient_details['name'] = name_changed
                
                age_changed = st.number_input("Age", min_value=0, max_value=120, value=st.session_state.patient_details['age'], key="patient_age")
                if age_changed != st.session_state.patient_details['age']:
                    st.session_state.patient_details['age'] = age_changed
                
            with col2:
                gender_changed = st.selectbox("Gender", ["Male", "Female", "Other"], index=["Male", "Female", "Other"].index(st.session_state.patient_details['gender']), key="patient_gender")
                if gender_changed != st.session_state.patient_details['gender']:
                    st.session_state.patient_details['gender'] = gender_changed
                
                date_changed = st.date_input("Date", value=st.session_state.patient_details['date'], key="invoice_date")
                if date_changed != st.session_state.patient_details['date']:
                    st.session_state.patient_details['date'] = date_changed
            
            # Show download button if patient name is filled
            if st.session_state.patient_details['name'].strip():
                try:
                    # Generate PDF with patient details
                    pdf = FPDF()
                    pdf.add_page()
                    pdf.set_font('Arial', 'B', 16)
                    
                    # Add header
                    pdf.cell(0, 10, 'Order Invoice', 0, 1, 'C')
                    pdf.line(10, 30, 200, 30)
                    
                    # Add patient details
                    pdf.set_font('Arial', '', 12)
                    pdf.cell(0, 10, f'Patient Name: {st.session_state.patient_details["name"]}', 0, 1)
                    pdf.cell(0, 10, f'Age: {st.session_state.patient_details["age"]} years | Gender: {st.session_state.patient_details["gender"]}', 0, 1)
                    pdf.cell(0, 10, f'Date: {st.session_state.patient_details["date"].strftime("%Y-%m-%d")}', 0, 1)
                    pdf.ln(5)
                    
                    # Table headers
                    pdf.set_font('Arial', 'B', 12)
                    pdf.cell(80, 10, 'Medicine', 1)
                    pdf.cell(30, 10, 'Quantity', 1)
                    pdf.cell(40, 10, 'Price', 1)
                    pdf.cell(40, 10, 'Total', 1)
                    pdf.ln()
                    
                    # Table rows
                    total = 0
                    pdf.set_font('Arial', '', 12)
                    for med, details in st.session_state.cart.items():
                        qty = details['quantity']
                        price = details['price']
                        subtotal = price * qty
                        total += subtotal
                        
                        pdf.cell(80, 10, med, 1)
                        pdf.cell(30, 10, str(qty), 1)
                        pdf.cell(40, 10, f"Rs. {price:.2f}", 1)
                        pdf.cell(40, 10, f"Rs. {subtotal:.2f}", 1)
                        pdf.ln()
                    
                    # Total amount
                    pdf.cell(150, 10, 'Total Amount:', 1)
                    pdf.cell(40, 10, f"Rs. {total:.2f}", 1)
                    
                    # Add pharmacist signature space
                    pdf.ln(20)
                    pdf.cell(0, 10, 'Pharmacist Signature:', 0, 1)
                    pdf.line(10, pdf.get_y() + 15, 80, pdf.get_y() + 15)
                    
                    # Generate PDF
                    pdf_bytes = pdf.output(dest='S').encode('latin1')
                    
                    # Create filename with patient details
                    filename = f"{st.session_state.patient_details['name']}_{st.session_state.patient_details['age']}_{st.session_state.patient_details['gender']}.pdf"
                    # Remove spaces and special characters from filename
                    filename = re.sub(r'[^\w\-_.]', '_', filename)
                    
                    # Show download button
                    st.download_button(
                        label="Download Invoice PDF",
                        data=pdf_bytes,
                        file_name=filename,
                        mime="application/pdf",
                        key="download_button"
                    )
                    
                except Exception as e:
                    st.error(f"Error generating invoice: {str(e)}")
            else:
                st.info("Please enter patient name to download the invoice")

        # Add custom table styles
        st.markdown("""
            <style>
            table {
                width: 100%;
                border-collapse: collapse;
                margin: 1rem 0;
                font-size: 0.95rem;
                color: #000000;
                table-layout: fixed;
            }
            th {
                background-color: #f8f9fa;
                padding: 12px 16px;
                text-align: left;
                border: 1px solid #dee2e6;
                color: #000000;
                font-weight: 600;
            }
            td {
                padding: 12px 16px;
                border: 1px solid #dee2e6;
                vertical-align: top;
                line-height: 1.6;
                color: #000000;
                word-wrap: break-word;
            }
            .value-cell {
                color: #000000;
                padding-left: 16px;
                background-color: white;
            }
            tr:nth-child(even) {
                background-color: #f8f9fa;
            }
            td:first-child {
                width: 25%;
                background-color: #f8f9fa;
                font-weight: 600;
            }
            td:last-child {
                width: 75%;
            }
            /* Add more spacing for bullet points */
            .value-cell br {
                content: "";
                display: block;
                margin: 8px 0;
            }
            /* Style bullet points */
            .value-cell {
                padding-left: 16px;
            }
            /* Ensure table fills expander width */
            .element-container {
                width: 100% !important;
            }
            div[data-testid="stExpander"] {
                width: 100% !important;
            }
            div[data-testid="stExpander"] > div {
                width: 100% !important;
            }
            </style>
        """, unsafe_allow_html=True) 
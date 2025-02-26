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

# =========== Load environment variables =========== 
load_dotenv()

# =========== Configure Gemini API =========== 
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
model = genai.GenerativeModel('gemini-2.0-flash')

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
        pdf.cell(40, 10, f"₹{price}", 1)
        pdf.cell(40, 10, f"₹{subtotal}", 1)
        pdf.ln()
    
    pdf.cell(150, 10, 'Total Amount:', 1)
    pdf.cell(40, 10, f"₹{total}", 1)
    
    return pdf.output(dest='S').encode('latin1')

def main():
    initialize_cart()

    # ==== APP HEADER ====
    st.markdown(
        "<h1 style='text-align: center; color: #2A5DB0;'>🩺 MediScan - Pharmacist's Assistant</h1>", 
        unsafe_allow_html=True
    )
    st.write(
        "<h5 style='text-align: center;'>Your AI-powered prescription analyzer & medicine finder</h5>", 
        unsafe_allow_html=True
    )

    # ==== IMAGE UPLOAD SECTION ====
    uploaded_file = st.file_uploader(
        "📂 **Upload Your Prescription Image** (JPG, PNG, JPEG)",
        type=['jpg', 'jpeg', 'png']
    )

    # Show welcome box only when no file is uploaded
    if not uploaded_file:
        # ==== WELCOME BOX ====
        with st.container():
            st.markdown(
                """
                <div style="border-radius: 10px; padding: 20px; background-color: #F5F7FA; text-align: center; box-shadow: 2px 2px 12px rgba(0,0,0,0.1);">
                    <h2 style="color: #2A5DB0;">🏥 Welcome to MediScan</h2>
                    <p style="font-size: 24px;"><em>Scan it. Find it. Get it.</em></p>
                    <hr style="border: 1px solid #D1D5DB; margin: 8px 0;">
                    <h4>🚀 What Can This App Do?</h4>
                    <ul style="text-align: left; font-size: 16px;">
                        <li>📸 Upload a <strong>prescription image</strong> to extract medicine details.</li>
                        <li>🔍 <strong>Smart medicine matching</strong> to check availability and find substitutes.</li>
                        <li>📦 Add medicines to <strong>cart and generate an order summary</strong>.</li>
                        <li>📜 Get a <strong>quick AI-generated summary</strong> of medicines.</li>
                    </ul>
                </div>
                """,
                unsafe_allow_html=True
            )

    if uploaded_file:
        # Show the uploaded image
        image = Image.open(uploaded_file)
        st.image(image, caption="📜 Uploaded Prescription", use_container_width=True)

        # Prompt for Gemini
        prompt = """
        Analyze this prescription image and provide **TWO sections** in your answer.

        SECTION 1: (To be displayed to the user but don't write "Section 1:" in the response)
        1. PATIENT INFORMATION:
            - Name
            - Age

        2. MEDICATIONS:
         For each medication, provide:
            - Medicine Name
            - Strength/Dosage
            - Quantity
            - Frequency
            - Special Instructions

        Format medications in a clear, tabular structure.
        If any information is not visible or unclear, mention "-".

        SECTION 2: (JSON BLOCK - This is NOT TO BE DISPLAYED TO THE USER, ONLY PASSED TO THE BACKEND)

        {
          "patient_info": {
            "name": "...",
            "age": "...",
            "other_details": "..."
          },
          "physician_info": {
            "name": "...",
            "specialization": "...",
            "contact_details": "..."
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

        if st.button("Analyze"):
            with st.spinner("Extracting information from the prescription..."):
                gemini_text = analyze_prescription(image, prompt)

            # Display the human-readable portion
            st.subheader("*Prescription Details*")
            display_text = gemini_text.split("SECTION 2:")[0]
            st.write(display_text)

            # Extract JSON from Gemini output
            match = re.search(r'(\{.*\})', gemini_text, flags=re.DOTALL)
            if not match:
                st.error("No JSON found in Gemini output.")
                return

            json_str = match.group(1)
            try:
                parsed = json.loads(json_str)
                medicines = parsed.get("medicines", [])
            except Exception as e:
                st.error(f"Could not parse JSON from Gemini: {e}")
                return

            if not medicines:
                st.warning("No medicines found in the JSON block.")
                return

            # Gather all medicine names
            med_names = []
            for m in medicines:
                name = m.get("medicine_name", "").strip()
                if name and name.lower() != "not available":
                    med_names.append(name)

            if not med_names:
                st.warning("No valid medicine names extracted.")
                return

            # Call FastAPI for fuzzy matching
            st.subheader("*Available Medicines & Alternatives*")
            backend_url = "http://localhost:8000"  # Adjust if needed

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
                    for row in matches:
                        # 1) Display the medicine name as a heading
                        name = row.get('name', 'Unknown')
                        if name:
                            name = name[0].upper() + name[1:].lower()  # Title-case
                        st.markdown(f"#### {matches.index(row) + 1}. {name}")

                        # 2) Let user pick quantity (moved up)
                        price = float(row.get('price', 0))
                        qty_avail = int(row.get('quantity_available', 0))
                        cart_item = st.session_state.cart.get(name, {})
                        current_qty = cart_item.get('quantity', 0)

                        qty_label = f"Select quantity for {name} (max {qty_avail})"
                        new_qty = st.number_input(
                            qty_label,
                            min_value=0,
                            max_value=qty_avail,
                            value=current_qty,
                            key=f"{name}_qty"
                        )

                        # 3) Build a small "table" of fields
                        table_data = []
                        fields_to_display = [
                            ("Price(₹)", "price"),
                            ("Quantity Available", "quantity_available"), 
                            ("Pack Size Label", "pack_size_label"),
                            ("Composition 1", "short_composition1"),
                            ("Composition 2", "short_composition2"),
                            ("Substitute 1", "substitute0"),
                            ("Substitute 2", "substitute1"),
                            ("Substitute 3", "substitute2"),
                            ("Substitute 4", "substitute3"),
                            ("Substitute 5", "substitute4"),
                            ("Side Effect 1", "sideEffect0"),
                            ("Side Effect 2", "sideEffect1"),
                            ("Side Effect 3", "sideEffect2"),
                            ("Side Effect 4", "sideEffect3"),
                            ("Side Effect 5", "sideEffect4"),
                            ("Use Case 1", "use0"),
                            ("Use Case 2", "use1"),
                            ("Use Case 3", "use2"),
                            ("Use Case 4", "use3"),
                            ("Use Case 5", "use4"),
                            ("Therapeutic Class", "therapeutic_class"),
                            ("Action Class", "action_class"),
                        ]

                        for label, key in fields_to_display:
                            val = row.get(key)
                            if val and str(val).strip().lower() not in ["unknown", "n/a", "not available", "-"]:
                                table_data.append([f"**{label}**", str(val)])

                        # Add similarity score
                        similarity_score = row.get("similarity_score")
                        if similarity_score is not None:
                            table_data.append(["**Similarity Score**", f"{round(similarity_score * 100, 2)}%"])

                        # Show the table
                        df = pd.DataFrame(table_data, columns=['Field', 'Value'])
                        st.table(df)

                        # 4) Generate & Display Gemini summary
                        summary_prompt = f"""
                        Based on this medicine information:
                        - Name: {name}
                        - Pack Size: {row.get('pack_size_label', '')}
                        - Uses: {', '.join(str(row.get(f'use{i}', '')) for i in range(5) if row.get(f'use{i}'))}
                        - Side Effects: {', '.join(str(row.get(f'sideEffect{i}', '')) for i in range(5) if row.get(f'sideEffect{i}'))}
                        - Therapeutic Class: {row.get('therapeutic_class', '')}
                        - Action Class: {row.get('action_class', '')}

                        Provide a concise 1-2 line summary including main uses, key side effects, and available alternatives.
                        Keep it simple and especially emphasize the uses and side effects.
                        """
                        with st.spinner("Generating summary..."):
                            try:
                                summary = model.generate_content(summary_prompt).text
                                st.info(f"💡 **Quick Summary**: {summary}")
                            except Exception as e:
                                st.warning("Couldn't generate summary for this medicine.")

                        st.markdown("---")

            # A single "Generate Order" button for all items
            submitted = st.form_submit_button("Generate Order")
            if submitted:
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
                                else:
                                    # If zero, remove from cart
                                    st.session_state.cart.pop(item_name, None)
                
                st.success("Order generated successfully!")

    # Display Cart & Order Summary
    if st.session_state.cart:
        st.sidebar.header("🛒 Order Summary")
        total = 0
        
        for med, details in st.session_state.cart.items():
            qty = details['quantity']
            price = details['price']
            subtotal = qty * price
            total += subtotal

            st.sidebar.markdown(f"**{med}**")
            st.sidebar.markdown(f"Quantity: {qty}  \nPrice: ₹{price}  \nTotal: {qty} × {price} = ₹{round(subtotal)}")
            st.sidebar.markdown("<hr style='margin: 5px 0px;'>", unsafe_allow_html=True)

        st.sidebar.markdown(f"### Total Amount: ₹{round(total)}")

if __name__ == "__main__":
    main()
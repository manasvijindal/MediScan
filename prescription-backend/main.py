from fastapi import FastAPI, HTTPException
import psycopg2
import os
import pandas as pd
from rapidfuzz import process, fuzz
from dotenv import load_dotenv
import re

app = FastAPI()

# Load Supabase Database URL
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../.env")) 
DATABASE_URL = os.getenv("REACT_APP_SUPERBASE_URL")

# Connect to Supabase
try:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    print(" Connected to Supabase database")
except Exception as e:
    raise Exception(f" Database connection failed: {e}")

# Fetch Medicine Data from Supabase
def fetch_medicine_data():
    query = """
    SELECT id, name, price, quantity_available, pack_size_label, composition, substitutes, 
           uses, side_effects, therapeutic_class, action_class 
    FROM medicines;
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    columns = ["id", "name", "price", "quantity_available", "pack_size_label", 
               "composition", "substitutes", "uses", "side_effects", 
               "therapeutic_class", "action_class"]
    return pd.DataFrame(rows, columns=columns)

# ✅ Load Medicine Data into DataFrame
df_medicines = fetch_medicine_data()

# ✅ Text Cleaning Function
def clean_text(text):
    """Cleans input text by keeping alphanumeric characters and converting to lowercase."""
    if pd.isna(text) or not isinstance(text, str):
        return ""
    return re.sub(r'[^a-zA-Z0-9 ]', '', text).lower().strip()

# ✅ Fuzzy Search Function
def fuzzy_medicine_search(query, df, threshold=50, top_k=10):
    query_clean = clean_text(query)
    if len(query_clean) < 2:  # Prevent invalid queries
        return None

    medicine_names = df["name"].dropna().apply(clean_text).tolist()
    fuzzy_results = process.extract(query_clean, medicine_names, scorer=fuzz.WRatio, limit=top_k)

    matched_medicines = []
    for match, score, _ in fuzzy_results:
        if score >= threshold:
            row = df[df["name"].apply(clean_text) == match].iloc[0]  # Get correct row
            matched_medicines.append({
                "name": row["name"],
                "price": row["price"],
                "quantity_available": row["quantity_available"],
                "pack_size_label": row["pack_size_label"],
                "composition": row["composition"],
                "substitutes": row["substitutes"],
                "uses": row["uses"],
                "side_effects": row["side_effects"],
                "therapeutic_class": row["therapeutic_class"],
                "action_class": row["action_class"],
                "similarity_score": score / 100.0  # Normalize score
            })

    return matched_medicines if matched_medicines else None

# ✅ API Endpoint for Fuzzy Search
@app.get("/search_medicine/")
async def search_medicine(query: str):
    """Searches for medicines in Supabase using RapidFuzz."""
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    matched_medicines = fuzzy_medicine_search(query, df_medicines, top_k=3)
    return matched_medicines if matched_medicines else {"message": "No matches found"}

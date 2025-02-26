from fastapi import FastAPI, HTTPException
import psycopg2
import os
import pandas as pd
from rapidfuzz import process, fuzz
from dotenv import load_dotenv
import re

app = FastAPI()

# Load .env from one directory up if needed, adjust the path to match your structure
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../.env"))

# Fetch from environment
DATABASE_URL = os.getenv("SUPABASE_DATABASE_URL")
USER = os.getenv("user")
PASSWORD = os.getenv("password")
HOST = os.getenv("host")
PORT = os.getenv("port")
DBNAME = os.getenv("dbname")

if not DATABASE_URL:
    raise Exception(" SUPABASE_DATABASE_URL not found in .env file")

# Connect to Supabase (Postgres)
try:
    connection = psycopg2.connect(
        user=USER,
        password=PASSWORD,
        host=HOST,
        port=PORT,
        dbname=DBNAME
    )
    cursor = connection.cursor()
    print(" Connected to Supabase database")
except Exception as e:
    print(f" Connection URL being used: {DATABASE_URL}")
    raise Exception(f" Database connection failed: {e}")

# Fetch all medicine data into a DataFrame
def fetch_medicine_data():
    query = """
    SELECT id, name, price, quantity_available, pack_size_label, 
           short_composition1, short_composition2,
           substitute0, substitute1, substitute2, substitute3, substitute4,
           "sideEffect0", "sideEffect1", "sideEffect2", "sideEffect3", "sideEffect4",
           use0, use1, use2, use3, use4,
           therapeutic_class, action_class
    FROM medicine;
    """
    cursor.execute(query)
    rows = cursor.fetchall()

    columns = [
        "id", "name", "price", "quantity_available", "pack_size_label",
        "short_composition1", "short_composition2",
        "substitute0", "substitute1", "substitute2", "substitute3", "substitute4",
        "sideEffect0", "sideEffect1", "sideEffect2", "sideEffect3", "sideEffect4",
        "use0", "use1", "use2", "use3", "use4",
        "therapeutic_class", "action_class"
    ]
    return pd.DataFrame(rows, columns=columns)

df_medicines = fetch_medicine_data()

def clean_text(text):
    """Removes non-alphanumeric chars and converts to lowercase for fuzzy matching."""
    if pd.isna(text) or not isinstance(text, str):
        return ""
    return re.sub(r'[^a-zA-Z0-9 ]', '', text).lower().strip()

def fuzzy_medicine_search(query, df, threshold=50, top_k=3):
    """Fuzzy search for a medicine name in DataFrame, returning top_k matches above threshold."""
    query_clean = clean_text(query)
    if len(query_clean) < 2:  # skip very short queries
        return None

    # Prepare a list of all medicine names in cleaned form
    medicine_names = df["name"].dropna().apply(clean_text).tolist()

    # RapidFuzz fuzzy matching
    fuzzy_results = process.extract(query_clean, medicine_names, scorer=fuzz.WRatio, limit=top_k)
    matched_medicines = []

    for match, score, _ in fuzzy_results:
        if score >= threshold:
            # match is the cleaned text, find the original row
            # We compare by cleaned name to find the correct row
            row = df[df["name"].apply(clean_text) == match].iloc[0]
            matched_medicines.append({
                "name": row["name"],
                "price": row["price"],
                "quantity_available": row["quantity_available"],
                "pack_size_label": row["pack_size_label"],
                "short_composition1": row["short_composition1"],
                "short_composition2": row["short_composition2"],
                "substitute0": row["substitute0"],
                "substitute1": row["substitute1"],
                "substitute2": row["substitute2"],
                "substitute3": row["substitute3"],
                "substitute4": row["substitute4"],
                "sideEffect0": row["sideEffect0"],
                "sideEffect1": row["sideEffect1"],
                "sideEffect2": row["sideEffect2"],
                "sideEffect3": row["sideEffect3"],
                "sideEffect4": row["sideEffect4"],
                "use0": row["use0"],
                "use1": row["use1"],
                "use2": row["use2"],
                "use3": row["use3"],
                "use4": row["use4"],
                "therapeutic_class": row["therapeutic_class"],
                "action_class": row["action_class"],
                "similarity_score": score / 100.0
            })

    return matched_medicines if matched_medicines else None

@app.get("/search_medicine/")
async def search_medicine(query: str):
    """
    Provide a 'query' string and retrieve up to 3 fuzzy matches from the 'medicine' table.
    Example: /search_medicine?query=Amoxicillin
    """
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    matched_medicines = fuzzy_medicine_search(query, df_medicines, threshold=50, top_k=3)
    return matched_medicines if matched_medicines else {"message": "No matches found"}

from fastapi import FastAPI, HTTPException, Query
import psycopg2
import os
import pandas as pd
from rapidfuzz import process, fuzz
from dotenv import load_dotenv
import re
from typing import Optional, List
from enum import Enum
from datetime import datetime, timedelta

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

class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"

class StockStatus(str, Enum):
    OUT_OF_STOCK = "out_of_stock"
    LOW_STOCK = "low_stock"
    EXPIRED = "expired"
    EXPIRING_SOON = "expiring_soon"
    IN_STOCK = "in_stock"

def get_stock_status(quantity: int, expiry_date: str, low_stock_threshold: int = 10) -> List[StockStatus]:
    """Determine stock status based on quantity and expiry date."""
    status = []
    
    # Check quantity-based status
    if quantity <= 0:
        status.append(StockStatus.OUT_OF_STOCK)
    elif quantity <= low_stock_threshold:
        status.append(StockStatus.LOW_STOCK)
    else:
        status.append(StockStatus.IN_STOCK)
    
    # Check expiry-based status
    if expiry_date:
        try:
            expiry = datetime.strptime(expiry_date, '%Y-%m-%d')
            today = datetime.now()
            
            if expiry < today:
                status.append(StockStatus.EXPIRED)
            elif expiry < today + timedelta(days=30):  # Within 30 days of expiry
                status.append(StockStatus.EXPIRING_SOON)
        except (ValueError, TypeError):
            pass
    
    return status

# Fetch all medicine data into a DataFrame
def fetch_medicine_data():
    query = """
    SELECT id, name, price, quantity_available, pack_size_label, 
           short_composition1, short_composition2,
           substitute0, substitute1, substitute2, substitute3, substitute4,
           "sideEffect0", "sideEffect1", "sideEffect2", "sideEffect3", "sideEffect4",
           use0, use1, use2, use3, use4,
           therapeutic_class, action_class, expiry_date
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
        "therapeutic_class", "action_class", "expiry_date"
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
                "expiry_date": row["expiry_date"],
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

@app.get("/management/medicines")
async def get_medicines(
    search: Optional[str] = None,
    sort_by: Optional[str] = None,
    sort_order: Optional[SortOrder] = SortOrder.asc,
    status_filter: Optional[List[StockStatus]] = Query(None),
    page: int = 1,
    page_size: int = 50
):
    """
    Get medicines with sorting, filtering, and pagination.
    - search: Optional search term for medicine name
    - sort_by: Column to sort by (quantity_available, expiry_date, price, name)
    - sort_order: asc or desc
    - status_filter: Filter by stock status (out_of_stock, low_stock, expired, expiring_soon, in_stock)
    - page: Page number
    - page_size: Number of items per page
    """
    try:
        # Start with all medicines
        medicines_df = df_medicines.copy()
        
        # Apply search if provided
        if search:
            matched_medicines = fuzzy_medicine_search(search, medicines_df, threshold=50, top_k=100)
            if matched_medicines:
                medicine_names = [m["name"] for m in matched_medicines]
                medicines_df = medicines_df[medicines_df["name"].isin(medicine_names)]
        
        # Convert to list of dictionaries for processing
        medicines = medicines_df.to_dict('records')
        
        # Add status flags to each medicine
        for medicine in medicines:
            try:
                # Ensure numeric fields are properly converted
                medicine["quantity_available"] = int(medicine["quantity_available"]) if medicine["quantity_available"] is not None else 0
                medicine["price"] = float(medicine["price"]) if medicine["price"] is not None else 0.0
                
                # Calculate expiry status
                is_expired = False
                is_expiring_soon = False
                if medicine.get("expiry_date"):
                    try:
                        expiry_date = datetime.strptime(str(medicine["expiry_date"]), '%Y-%m-%d')
                        days_until_expiry = (expiry_date - datetime.now()).days
                        if days_until_expiry <= 0:
                            is_expired = True
                        elif days_until_expiry <= 15:
                            is_expiring_soon = True
                    except (ValueError, TypeError):
                        pass

                # Set status flags
                status_flags = []
                if medicine["quantity_available"] <= 0:
                    status_flags.append(StockStatus.OUT_OF_STOCK)
                elif medicine["quantity_available"] < 5:
                    status_flags.append(StockStatus.LOW_STOCK)
                else:
                    status_flags.append(StockStatus.IN_STOCK)
                
                if is_expired:
                    status_flags.append(StockStatus.EXPIRED)
                elif is_expiring_soon:
                    status_flags.append(StockStatus.EXPIRING_SOON)
                
                medicine["status"] = status_flags
            except (ValueError, TypeError):
                medicine["quantity_available"] = 0
                medicine["price"] = 0.0
                medicine["status"] = [StockStatus.OUT_OF_STOCK]
        
        # Apply status filter if provided
        if status_filter:
            medicines = [
                m for m in medicines 
                if any(status in m["status"] for status in status_filter)
            ]
        
        # Apply sorting
        if sort_by:
            reverse = sort_order == SortOrder.desc
            medicines.sort(
                key=lambda x: (
                    x.get(sort_by, 0) if sort_by != 'expiry_date' 
                    else datetime.strptime(str(x.get('expiry_date', '2000-01-01')), '%Y-%m-%d')
                ),
                reverse=reverse
            )
        
        # Apply pagination
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_medicines = medicines[start_idx:end_idx]
        
        # Format response
        for medicine in paginated_medicines:
            # Format uses
            uses = []
            for i in range(5):
                use = medicine.get(f'use{i}')
                if use and isinstance(use, str) and use.strip():
                    uses.append(use.strip())
            medicine['uses'] = uses
            
            # Clean up response
            for i in range(5):
                medicine.pop(f'use{i}', None)
            
            # Ensure all fields are properly formatted
            medicine["name"] = str(medicine.get("name", ""))
            medicine["price"] = float(medicine.get("price", 0))
            medicine["quantity_available"] = int(medicine.get("quantity_available", 0))
            medicine["expiry_date"] = str(medicine.get("expiry_date", "")) if medicine.get("expiry_date") else ""
        
        return {
            "total": len(medicines),
            "page": page,
            "page_size": page_size,
            "medicines": paginated_medicines
        }
        
    except Exception as e:
        print(f"Error in get_medicines: {str(e)}")  # Add logging
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/inventory_stats")
async def get_inventory_stats():
    """Get inventory statistics including total items, low stock, out of stock, and expiring soon."""
    try:
        medicines_df = df_medicines.copy()
        total_items = len(medicines_df)
        
        # Calculate statistics
        stats = {
            "total_items": total_items,
            "low_stock_items": 0,
            "out_of_stock": 0,
            "expiring_soon": 0
        }
        
        # Process each medicine
        for _, medicine in medicines_df.iterrows():
            try:
                quantity = int(medicine['quantity_available'])
                if quantity <= 0:
                    stats["out_of_stock"] += 1
                elif quantity < 5:
                    stats["low_stock_items"] += 1
                    
                # Check expiry
                if medicine.get('expiry_date'):
                    try:
                        expiry_date = datetime.strptime(medicine['expiry_date'], '%Y-%m-%d')
                        if expiry_date < datetime.now() + timedelta(days=15):
                            stats["expiring_soon"] += 1
                    except (ValueError, TypeError):
                        pass
            except (ValueError, TypeError):
                stats["out_of_stock"] += 1
        
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


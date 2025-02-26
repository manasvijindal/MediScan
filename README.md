# MediScan - Pharmacist's Assistant

A powerful tool that helps pharmacists analyze prescriptions and manage medicine inventory using AI.

## Features

* 📋 Prescription Image Analysis using Google's Gemini AI
* 💊 Medicine Inventory Management
* 🔍 Smart Medicine Matching
* 📊 Detailed Medicine Information
* 🛒 Shopping Cart System

## Demo

https://github.com/manasvijindal/MediScan/raw/main/demo/mediscan-demo.mp4

Watch the video demo above to see MediScan in action! 

## Tech Stack

- **Frontend**: Streamlit
- **Backend**: FastAPI
- **AI/ML**: Google Gemini AI
- **Database**: Supabase

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/MediScan.git
cd MediScan
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the root directory with:
```
GOOGLE_API_KEY=your_gemini_api_key
```

5. Start the backend server:
```bash
cd prescription-backend
uvicorn main:app --reload
```

6. In a new terminal, start the Streamlit app:
```bash
streamlit run app.py
```

## Usage

1. Upload a prescription image
2. Click "Analyze" to extract prescription details
3. View matched medicines from inventory
4. Add medicines to cart
5. Generate order summary

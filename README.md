# 🩺 MediScan - A Pharmacist Assistent

MediScan is an intelligent prescription processing system designed to assist pharmacists in efficiently managing prescriptions, inventory, and medicine substitutions.

## 🌟 Key Features

### 1. Prescription Analysis
- 📝 Automated extraction of prescription details using Google's Gemini AI
- ✅ Doctor's license verification
- 🔍 Intelligent medicine name recognition
- 📊 Dosage and quantity analysis

### 2. Smart Medicine Matching
- 🎯 Fuzzy matching algorithm for medicine names
- 💊 Intelligent substitute recommendations
- 📦 Pack size optimization suggestions

### 3. Inventory Management
- 📊 Real-time stock tracking
- ⚠️ Expiry date monitoring
- 🔄 Low stock alerts
- 📈 Stock status visualization

### 4. Professional Documentation
- 🧾 Automated invoice generation

## 🛠️ Technology Stack

- **Frontend:** Streamlit (Python)
- **Backend:** FastAPI
- **Database:** PostgreSQL (Supabase)
- **AI/ML:** 
  - Google Gemini API for prescription analysis
  - RapidFuzz for medicine matching
- **Additional Libraries:**
  - FPDF for PDF generation
  - Pandas for data manipulation
  - Python-dotenv for environment management

## 🚀 Getting Started

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/MediScan.git
   cd MediScan
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file with:
   ```env
   GOOGLE_API_KEY=your_gemini_api_key
   SUPABASE_DATABASE_URL=your_database_url
   ```

5. **Run the application**
   ```bash
   streamlit run Prescription.py
   ```

## 💡 Usage

1. **Upload Prescription**
   - Click "Upload Prescription Image"
   - Select a clear image of the prescription
   - Click "Analyze" to process

2. **Review Medicines**
   - View matched medicines
   - Check availability and alternatives
   - Subtitutes if a medicine out of stock

3. **Generate Order**
   - Add medicines to cart
   - Fill patient details
   - Generate and download invoice

3. **Search for a specific medicine**

5. **Check Expired, Expiry Soon and Out of Stock medicines in inventory**

## 🎯 Target Users

- 💊 Pharmacists
- 🏥 Pharmacy Staff
- 📦 Inventory Managers

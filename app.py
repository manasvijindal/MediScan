import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
from PIL import Image

# =========== Load environment variables ===========
load_dotenv()

# =========== Configure Gemini API ===========
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
model = genai.GenerativeModel('gemini-2.0-flash')  # Vision model

# =========== Gemini Functions ===========

def extract_text_from_image(image):
    """
    Uses Gemini Vision to extract and clean text from an image, returning a formatted text response.
    """
    prompt = """
    Extract and correct the text from this prescription image.

    - Identify patient details (name, age, gender) if available.
    - Identify physician details (name, designation) if available.
    - Extract medicine names and correct any spelling errors or infer full medicine names if incomplete.
    - Extract dosage information.
    - Calculate total quantity based on frequency (e.g., "1 cap 3X day for 7 days" should be calculated as "21 capsules").
    - Expand and clarify instructions to make them more readable.
    - Ignore unnecessary details like logos or handwriting noise.

    Format the response in the **exact text format** below:

    Patient Name: [If available]
    Other details: [If available]

    Physician Name: [If available]
    Physician Details: [If available]

    Medicine Name: [Extracted Medicine Name]
    Corrected/Full Name: [Corrected Medicine Name]
    Dosage: [Dosage]
    Form: [Tablet/Capsule/Liquid/etc.]
    Quantity: [Total count or volume, calculated if necessary]
    Instruction: [Expanded clear instruction]

    (Repeat for each medicine)

    Summary:
    - [Medicine 1]: [Dosage], [Form], [Short Explanation]
    - [Medicine 2]: [Dosage], [Form], [Short Explanation]

    - If any information is **not found**, do **not include** that section.
    - Return **only formatted text** as per the structure above.
    - Do **not return JSON** or extra explanations.
    """

    response = model.generate_content([prompt, image])

    # Ensure response is not empty
    if response.text.strip():
        return response.text
    else:
        return "Failed to extract text from the image."

# =========== Streamlit App ===========

def main():
    st.title("Prescription Extraction & Formatting App")
    st.write("Upload a prescription image (JPG/JPEG/PNG) to extract structured medicine details in text format.")

    uploaded_file = st.file_uploader("Choose an image", type=['jpg', 'jpeg', 'png'])

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Prescription", use_column_width=True)

        if st.button("Analyze"):
            with st.spinner("Extracting text with Gemini..."):
                formatted_text = extract_text_from_image(image)

                st.subheader("Prescription Details")
                st.text(formatted_text)

if __name__ == "__main__":
    main()




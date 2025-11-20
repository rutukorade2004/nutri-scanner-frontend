import streamlit as st
import requests
from PIL import Image
import numpy as np
from zxingcpp import read_barcodes      # <--- ZXing import

# ------------------------------------
# Streamlit CONFIG
# ------------------------------------
st.set_page_config(page_title="AI Nutrition Scanner", page_icon="🥗")
st.title("🥗 AI Nutrition Scanner")

# ------------------------------------
# Barcode Scanner (ZXing)
# ------------------------------------
def extract_barcode(pil_image):
    """Extract barcode using ZXing (no DLL required)."""
    try:
        img = np.array(pil_image)
        results = read_barcodes(img)

        if results:
            return results[0].text  # barcode value

        return None
    except Exception as e:
        return None


# ------------------------------------
# INPUT OPTIONS
# ------------------------------------
st.subheader("📸 Choose Input Method")
option = st.radio(
    "Select how you want to scan:",
    ["Enter Barcode Manually", "Scan Using Camera", "Upload Image"]
)

barcode = None

# ------------------ MANUAL OPTION ------------------
if option == "Enter Barcode Manually":
    barcode = st.text_input("Enter product barcode")


# ------------------ CAMERA SCAN ------------------
elif option == "Scan Using Camera":
    st.write("📷 Use your camera to scan the barcode")
    img_file = st.camera_input("Take a picture")

    if img_file:
        image = Image.open(img_file)
        barcode = extract_barcode(image)

        if barcode:
            st.success(f"Detected Barcode: {barcode}")
        else:
            st.error("❌ No barcode detected. Try again.")


# ------------------ UPLOAD IMAGE OPTION ------------------
elif option == "Upload Image":
    img_file = st.file_uploader("Upload product image", type=["jpg", "jpeg", "png"])

    if img_file:
        image = Image.open(img_file)
        st.image(image, caption="Uploaded Image", use_container_width=True)

        barcode = extract_barcode(image)

        if barcode:
            st.success(f"Detected Barcode: {barcode}")
        else:
            st.error("❌ No barcode detected in the uploaded image.")


# ------------------------------------
# SCAN BUTTON → Backend API Call
# ------------------------------------
if st.button("Scan Product"):

    if not barcode:
        st.warning("Please enter or scan a valid barcode.")
        st.stop()

    with st.spinner("Scanning..."):
        url = f"http://127.0.0.1:8000/scan/{barcode}"

        try:
            res = requests.get(url).json()
        except:
            st.error("❌ Backend not running. Start FastAPI first.")
            st.stop()

    if "error" in res:
        st.error("❌ Product not found in OpenFoodFacts or API.")
    else:
        st.success("✔ Product Data Retrieved Successfully!")

        # Product Name
        st.subheader(res.get("product_name", "Unknown Product"))

        # Ingredients
        st.write("### 🧂 Ingredients")
        st.write(res.get("ingredients", "No ingredients found."))

        # ML Prediction
        st.write("### 🤖 ML Prediction")
        st.info(res.get("model_prediction", "N/A"))

        # Health Result
        st.write("### 🥇 Health Result")
        st.success(res.get("result", "N/A"))

        # Health Score
        st.write("### 📊 Health Score")
        st.metric(label="Score (0–100)", value=res.get("health_score", "N/A"))

        # Warnings
        st.write("### ⚠️ Warnings")
        warnings = res.get("warnings", [])
        if len(warnings) == 0:
            st.success("No major issues detected.")
        else:
            for w in warnings:
                st.warning(w)   
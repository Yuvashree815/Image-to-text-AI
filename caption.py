import requests
import streamlit as st
import base64

def get_img_as_base64(file):
    with open(file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

img = get_img_as_base64("ai.jpg")

page_bg_img = f"""
<style>
[data-testid="stAppViewContainer"] > .main {{
background-image: url("data:image/png;base64,{img}");
background-size: cover;
}}
[data-testid="stHeader"] {{
background: rgba(0,0,0,0);
}}
</style>
"""
st.markdown(page_bg_img, unsafe_allow_html=True)

API_URL = "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-large"
headers = {"Authorization": "Bearer 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"}

def query(image_data):
    response = requests.post(API_URL, headers=headers, data=image_data)
    return response.json()

# Image uploader
uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

# If an image is uploaded
if uploaded_file is not None:
    # Display the uploaded image
    st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)

    # Read the image data from the uploaded file
    image_data = uploaded_file.read()

    # Send the image data to the Hugging Face API
    with st.spinner('Generating caption...'):
        result = query(image_data)

    # Display the result (the generated caption)
    if "error" in result:
        st.error(f"Error: {result['error']}")
    else:
        caption = result[0]['generated_text']
        st.markdown(f"""
        <div style="background-color:white; padding:10px; border-radius:10px;">
            <p style="color:black; font-size:18px;">{caption}</p>
        </div>
        """, unsafe_allow_html=True)

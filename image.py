import requests
import streamlit as st
import base64
import io
from PIL import Image

def get_img_as_base64(file):
    with open(file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Load background image
img = get_img_as_base64("ss.jpg")

page_bg_img = f"""
<style>
[data-testid="stAppViewContainer"] > .main {{
background-image: url("data:image/png;base64,{img}");
background-size: cover;
}}
[data-testid="stHeader"] {{
background: rgba(0, 0, 0, 0);
}}
h1 {{
    color: white;
    font-family: 'bookman old style', sans-serif;
    font-size: 60px;
    text-align: center;
    margin-top: 50px;
}}
</style>
"""
st.markdown(page_bg_img, unsafe_allow_html=True)

# Styled Eurobot heading
st.markdown("<h1>AIbot</h1>", unsafe_allow_html=True)

# Selection menu
option = st.selectbox(
    "Choose a functionality:",
    ["Text to Image Generator", "Image to Text Generator"]
)

if option == "Text to Image Generator":
    st.subheader("Text to Image Generator")

    text_prompt = st.text_input("Enter prompt for image generation")

    if st.button('Generate Image'):
        if text_prompt:
            # Hugging Face API details for text-to-image
            API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
            headers = {"Authorization": "Bearer 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"}

            def query(payload):
                try:
                    response = requests.post(API_URL, headers=headers, json=payload)
                    response.raise_for_status()  # Raises an error for bad HTTP status codes
                    return response.content
                except requests.exceptions.RequestException as e:
                    st.error(f"Request failed: {e}")
                    return None

            # Generate the image
            image_bytes = query({"inputs": text_prompt})

            if image_bytes:
                try:
                    # Open the image with PIL
                    image = Image.open(io.BytesIO(image_bytes))
                    st.image(image, caption="Generated Image")

                    # Add download button
                    st.download_button(
                        label="Download Image",
                        data=image_bytes,
                        file_name="generated_image.png",
                        mime="image/png"
                    )
                    
                    # Add reprompt button
                    if st.button("Reprompt"):
                        st.experimental_rerun()

                except IOError:
                    st.error("Failed to generate image. The returned data might not be a valid image.")
        else:
            st.warning("Please enter a prompt.")

elif option == "Image to Text Generator":
    st.subheader("Image Caption Generator")

    # Hugging Face API details for image captioning
    IMAGE_API_URL = "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-large"
    IMAGE_HEADERS = {"Authorization": "Bearer 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"}

    def query_image(image_data):
        try:
            response = requests.post(IMAGE_API_URL, headers=IMAGE_HEADERS, data=image_data)
            response.raise_for_status()  # Raises an error for bad HTTP status codes
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Request failed: {e}")
            return None

    # Image uploader
    uploaded_file = st.file_uploader("Upload an image for captioning", type=["jpg", "jpeg", "png"])

    # If an image is uploaded
    if uploaded_file is not None:
        # Display the uploaded image
        st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)

        # Read the image data from the uploaded file
        image_data = uploaded_file.read()

        # Send the image data to the Hugging Face API
        with st.spinner('Generating caption...'):
            result = query_image(image_data)

        # Display the result (the generated caption)
        if result is not None:
            if "error" in result:
                st.error(f"Error: {result['error']}")
            else:
                st.success(f"Generated Caption: {result[0]['generated_text']}")
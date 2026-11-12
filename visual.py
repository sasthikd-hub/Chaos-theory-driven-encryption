import streamlit as st
import numpy as np
from PIL import Image
from pendulum import make_mask

st.title("Chaos theory driven image encryption")
st.write("Scramble and restore an image using a simulated double pendulum.")

st.sidebar.header("Physics key")

theta1 = st.sidebar.number_input("Top angle (°)", value=120.0, step=0.0001, format="%.4f")
theta2 = st.sidebar.number_input("Bottom angle (°)", value=-100.0, step=0.0001, format="%.4f")
m1 = st.sidebar.number_input("Top bob mass (kg)", min_value=0.1, value=1.0)
m2 = st.sidebar.number_input("Bottom bob mass (kg)", min_value=0.1, value=1.0)
l1 = st.sidebar.number_input("Top rod length (m)", min_value=0.1, value=1.0)
l2 = st.sidebar.number_input("Bottom rod length (m)", min_value=0.1, value=1.0)

uploaded_file = st.file_uploader("Choose a photo", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    with Image.open(uploaded_file) as image:
        pixels = np.array(image.convert("RGB"), dtype=np.uint8)

        mask = make_mask(theta1, theta2, m1, m2, l1, l2,
        byte_count=pixels.size)
        mask_array = np.frombuffer(mask, dtype=np.uint8).reshape(pixels.shape)
        encrypted_pixels = np.bitwise_xor(pixels, mask_array)

        original_col, encrypted_col = st.columns(2)
        original_col.image(pixels, caption="Original photo")
        encrypted_col.image(encrypted_pixels, caption="Scrambled photo")
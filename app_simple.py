import streamlit as st
from PIL import Image, ImageFilter, ImageEnhance, ImageOps
import os
import io
import numpy as np

OUTPUTS_DIR = "./outputs"
os.makedirs(OUTPUTS_DIR, exist_ok=True)

def create_artistic_sketch(image, style="pencil", intensity=1.0):
    """Create artistic sketch using PIL"""
    if style == "pencil":
        return create_pencil_effect(image, intensity)
    elif style == "charcoal":
        return create_charcoal_effect(image, intensity)
    else:
        return create_ink_effect(image, intensity)

def create_pencil_effect(image, intensity):
    gray = image.convert('L')
    inverted = ImageOps.invert(gray)
    blurred = inverted.filter(ImageFilter.GaussianBlur(radius=intensity))
    
    # Dodge blend
    def dodge_blend(base, blend):
        base_arr = np.array(base, dtype=np.float32)
        blend_arr = np.array(blend, dtype=np.float32)
        blend_arr = np.where(blend_arr == 255, 254, blend_arr)
        result = (base_arr * 255) / (255 - blend_arr)
        return Image.fromarray(np.clip(result, 0, 255).astype(np.uint8))
    
    return dodge_blend(gray, blurred)

def create_charcoal_effect(image, intensity):
    gray = image.convert('L')
    blurred = gray.filter(ImageFilter.GaussianBlur(radius=intensity))
    enhanced = ImageEnhance.Contrast(blurred).enhance(2.0)
    return ImageOps.posterize(enhanced, 4)

def create_ink_effect(image, intensity):
    gray = image.convert('L')
    edges = gray.filter(ImageFilter.FIND_EDGES)
    enhanced = ImageEnhance.Contrast(edges).enhance(intensity * 2)
    return ImageOps.invert(enhanced)

def main():
    st.set_page_config(page_title="Art Style Generator", layout="wide")
    
    st.title("🎨 Art Style Generator")
    st.write("Transform your images into different artistic styles")
    
    # Sidebar controls
    st.sidebar.header("Settings")
    style = st.sidebar.selectbox("Art Style", ["pencil", "charcoal", "ink"])
    intensity = st.sidebar.slider("Intensity", 0.5, 3.0, 1.5, 0.1)
    
    uploaded_file = st.file_uploader("Choose an image...", type=['jpg', 'jpeg', 'png'])
    
    if uploaded_file is not None:
        original_image = Image.open(uploaded_file).convert("RGB")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Original Image")
            st.image(original_image, use_column_width=True)
        
        with st.spinner(f"Creating {style} artwork..."):
            art_image = create_artistic_sketch(original_image, style, intensity)
            
            with col2:
                st.subheader(f"{style.title()} Art")
                st.image(art_image, use_column_width=True)
            
            # Download
            buf = io.BytesIO()
            art_image.save(buf, format="PNG")
            buf.seek(0)
            
            st.download_button(
                label=f"📥 Download {style.title()} Art",
                data=buf.getvalue(),
                file_name=f"{style}_{uploaded_file.name}",
                mime="image/png"
            )

if __name__ == "__main__":
    main()
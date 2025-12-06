import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import io
import base64
import random
import os

# Page configuration
st.set_page_config(
    page_title="🎬 YouTube Thumbnail Generator",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# YouTube thumbnail dimensions (standard)
THUMBNAIL_WIDTH = 1280
THUMBNAIL_HEIGHT = 720

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(90deg, #FF0000 0%, #CC0000 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
    }
    .stButton>button {
        background: linear-gradient(90deg, #FF0000 0%, #CC0000 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.5rem 2rem;
        font-weight: 600;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #CC0000 0%, #990000 100%);
        box-shadow: 0 4px 12px rgba(255, 0, 0, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'thumbnail_image' not in st.session_state:
    st.session_state.thumbnail_image = None
if 'text_elements' not in st.session_state:
    st.session_state.text_elements = []

def create_gradient_background(color1, color2, width, height, direction='horizontal'):
    """Create a gradient background"""
    img = Image.new('RGB', (width, height), color1)
    draw = ImageDraw.Draw(img)
    
    if direction == 'horizontal':
        for i in range(width):
            r = int(color1[0] * (1 - i/width) + color2[0] * (i/width))
            g = int(color1[1] * (1 - i/width) + color2[1] * (i/width))
            b = int(color1[2] * (1 - i/width) + color2[2] * (i/width))
            draw.line([(i, 0), (i, height)], fill=(r, g, b))
    else:  # vertical
        for i in range(height):
            r = int(color1[0] * (1 - i/height) + color2[0] * (i/height))
            g = int(color1[1] * (1 - i/height) + color2[1] * (i/height))
            b = int(color1[2] * (1 - i/height) + color2[2] * (i/height))
            draw.line([(0, i), (width, i)], fill=(r, g, b))
    
    return img

def hex_to_rgb(hex_color):
    """Convert hex color to RGB"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def get_font(size, bold=False):
    """Get a font, trying different options"""
    try:
        if bold:
            font_paths = [
                "C:/Windows/Fonts/arialbd.ttf",
                "C:/Windows/Fonts/calibrib.ttf",
                "/System/Library/Fonts/Helvetica.ttc",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
            ]
        else:
            font_paths = [
                "C:/Windows/Fonts/arial.ttf",
                "C:/Windows/Fonts/calibri.ttf",
                "/System/Library/Fonts/Helvetica.ttc",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
            ]
        
        for path in font_paths:
            if os.path.exists(path):
                return ImageFont.truetype(path, size)
    except:
        pass
    
    # Fallback to default font
    return ImageFont.load_default()

def create_thumbnail(
    background_type,
    background_color1,
    background_color2,
    gradient_direction,
    uploaded_image,
    text_elements
):
    """Create the thumbnail image"""
    
    # Create base image
    if background_type == "Solid Color":
        bg_color = hex_to_rgb(background_color1)
        img = Image.new('RGB', (THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT), bg_color)
    elif background_type == "Gradient":
        color1 = hex_to_rgb(background_color1)
        color2 = hex_to_rgb(background_color2)
        img = create_gradient_background(color1, color2, THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT, gradient_direction)
    elif background_type == "Upload Image":
        if uploaded_image:
            img = Image.open(uploaded_image).convert('RGB')
            img = img.resize((THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT), Image.Resampling.LANCZOS)
        else:
            img = Image.new('RGB', (THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT), (50, 50, 50))
    
    draw = ImageDraw.Draw(img)
    
    # Add text elements
    for element in text_elements:
        text = element['text']
        x = int(element['x'] * THUMBNAIL_WIDTH / 100)
        y = int(element['y'] * THUMBNAIL_HEIGHT / 100)
        font_size = element['font_size']
        text_color = hex_to_rgb(element['text_color'])
        stroke_color = hex_to_rgb(element['stroke_color'])
        stroke_width = element['stroke_width']
        bold = element.get('bold', False)
        
        font = get_font(font_size, bold)
        
        # Draw text with stroke (outline)
        draw.text(
            (x, y),
            text,
            font=font,
            fill=text_color,
            stroke_fill=stroke_color,
            stroke_width=stroke_width,
            anchor='mm'
        )
    
    return img

def image_to_base64(img):
    """Convert PIL image to base64 string"""
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return img_str

def get_image_download_link(img, filename="thumbnail.png"):
    """Generate a download link for the image"""
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    href = f'<a href="data:image/png;base64,{img_str}" download="{filename}" style="background: linear-gradient(90deg, #FF0000 0%, #CC0000 100%); color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; font-weight: bold;">📥 Download Thumbnail</a>'
    return href

# Header
st.markdown('<h1 class="main-header">🎬 YouTube Thumbnail Generator</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #666; font-size: 1.2rem;">Create stunning thumbnails for your YouTube videos</p>', unsafe_allow_html=True)

# Sidebar for controls
st.sidebar.header("⚙️ Settings")

# Background settings
st.sidebar.subheader("🎨 Background")
background_type = st.sidebar.radio(
    "Background Type",
    ["Solid Color", "Gradient", "Upload Image"]
)

background_color1 = "#FF0000"
background_color2 = "#0000FF"
gradient_direction = "horizontal"
uploaded_image = None

if background_type == "Solid Color":
    background_color1 = st.sidebar.color_picker("Background Color", "#FF0000")
elif background_type == "Gradient":
    col1, col2 = st.sidebar.columns(2)
    with col1:
        background_color1 = st.color_picker("Color 1", "#FF0000")
    with col2:
        background_color2 = st.color_picker("Color 2", "#0000FF")
    gradient_direction = st.sidebar.selectbox("Gradient Direction", ["horizontal", "vertical"])
elif background_type == "Upload Image":
    uploaded_image = st.sidebar.file_uploader("Upload Background Image", type=['png', 'jpg', 'jpeg'])

st.sidebar.divider()

# Text elements management
st.sidebar.subheader("📝 Text Elements")

# Add new text element
if st.sidebar.button("➕ Add Text", use_container_width=True):
    if 'text_elements' not in st.session_state:
        st.session_state.text_elements = []
    
    new_element = {
        'text': 'Your Text Here',
        'x': 50,
        'y': 50,
        'font_size': 60,
        'text_color': '#FFFFFF',
        'stroke_color': '#000000',
        'stroke_width': 3,
        'bold': True
    }
    st.session_state.text_elements.append(new_element)

# Manage existing text elements
if st.session_state.text_elements:
    st.sidebar.write(f"**{len(st.session_state.text_elements)} text element(s)**")
    
    for i, element in enumerate(st.session_state.text_elements):
        with st.sidebar.expander(f"Text {i+1}: {element['text'][:20]}..."):
            element['text'] = st.text_input("Text", element['text'], key=f"text_{i}")
            
            col1, col2 = st.columns(2)
            with col1:
                element['x'] = st.slider("X Position (%)", 0, 100, element['x'], key=f"x_{i}")
            with col2:
                element['y'] = st.slider("Y Position (%)", 0, 100, element['y'], key=f"y_{i}")
            
            element['font_size'] = st.slider("Font Size", 20, 200, element['font_size'], key=f"size_{i}")
            
            element['text_color'] = st.color_picker("Text Color", element['text_color'], key=f"color_{i}")
            
            col1, col2 = st.columns(2)
            with col1:
                element['stroke_color'] = st.color_picker("Stroke Color", element['stroke_color'], key=f"stroke_color_{i}")
            with col2:
                element['stroke_width'] = st.slider("Stroke Width", 0, 10, element['stroke_width'], key=f"stroke_{i}")
            
            element['bold'] = st.checkbox("Bold", element.get('bold', False), key=f"bold_{i}")
            
            if st.button(f"🗑️ Delete Text {i+1}", key=f"delete_{i}"):
                st.session_state.text_elements.pop(i)
                st.rerun()

st.sidebar.divider()

# Quick templates
st.sidebar.subheader("🎯 Quick Templates")
if st.sidebar.button("📌 Title + Subtitle Template", use_container_width=True):
    st.session_state.text_elements = [
        {
            'text': 'MAIN TITLE',
            'x': 50,
            'y': 35,
            'font_size': 80,
            'text_color': '#FFFFFF',
            'stroke_color': '#000000',
            'stroke_width': 5,
            'bold': True
        },
        {
            'text': 'Subtitle Text',
            'x': 50,
            'y': 60,
            'font_size': 50,
            'text_color': '#FFFF00',
            'stroke_color': '#000000',
            'stroke_width': 3,
            'bold': True
        }
    ]
    st.rerun()

if st.sidebar.button("🔥 Attention Grabbing", use_container_width=True):
    st.session_state.text_elements = [
        {
            'text': '⚠️ YOU WON\'T BELIEVE',
            'x': 50,
            'y': 30,
            'font_size': 70,
            'text_color': '#FF0000',
            'stroke_color': '#FFFFFF',
            'stroke_width': 6,
            'bold': True
        },
        {
            'text': 'WHAT HAPPENS NEXT!',
            'x': 50,
            'y': 55,
            'font_size': 75,
            'text_color': '#FFFF00',
            'stroke_color': '#000000',
            'stroke_width': 5,
            'bold': True
        }
    ]
    st.rerun()

if st.sidebar.button("💡 Tutorial Style", use_container_width=True):
    st.session_state.text_elements = [
        {
            'text': 'HOW TO',
            'x': 50,
            'y': 40,
            'font_size': 90,
            'text_color': '#00FF00',
            'stroke_color': '#000000',
            'stroke_width': 6,
            'bold': True
        },
        {
            'text': 'Step by Step Guide',
            'x': 50,
            'y': 65,
            'font_size': 55,
            'text_color': '#FFFFFF',
            'stroke_color': '#000000',
            'stroke_width': 4,
            'bold': True
        }
    ]
    st.rerun()

if st.sidebar.button("🗑️ Clear All Text", use_container_width=True):
    st.session_state.text_elements = []
    st.rerun()

# Main content area
st.subheader("🎨 Preview")

# Generate thumbnail
if st.button("🔄 Generate Thumbnail", type="primary", use_container_width=True):
    try:
        thumbnail = create_thumbnail(
            background_type,
            background_color1,
            background_color2,
            gradient_direction,
            uploaded_image,
            st.session_state.text_elements
        )
        st.session_state.thumbnail_image = thumbnail
    except Exception as e:
        st.error(f"Error generating thumbnail: {str(e)}")

# Display thumbnail
if st.session_state.thumbnail_image:
    st.image(st.session_state.thumbnail_image, use_container_width=True, caption="Your YouTube Thumbnail (1280x720)")
    
    # Download button
    st.markdown(get_image_download_link(st.session_state.thumbnail_image), unsafe_allow_html=True)
    
    # Auto-generate on settings change
    st.info("💡 Tip: Adjust settings and click 'Generate Thumbnail' to update the preview")
else:
    # Show placeholder
    placeholder = Image.new('RGB', (THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT), (50, 50, 50))
    draw = ImageDraw.Draw(placeholder)
    
    # Draw grid
    for i in range(0, THUMBNAIL_WIDTH, 100):
        draw.line([(i, 0), (i, THUMBNAIL_HEIGHT)], fill=(70, 70, 70), width=1)
    for i in range(0, THUMBNAIL_HEIGHT, 100):
        draw.line([(0, i), (THUMBNAIL_WIDTH, i)], fill=(70, 70, 70), width=1)
    
    # Center crosshair
    draw.line([(THUMBNAIL_WIDTH//2, 0), (THUMBNAIL_WIDTH//2, THUMBNAIL_HEIGHT)], fill=(100, 100, 100), width=2)
    draw.line([(0, THUMBNAIL_HEIGHT//2), (THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT//2)], fill=(100, 100, 100), width=2)
    
    # Text
    try:
        font = get_font(40, True)
        text = "Click 'Generate Thumbnail' to create your design"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        draw.text(
            ((THUMBNAIL_WIDTH - text_width) // 2, (THUMBNAIL_HEIGHT - text_height) // 2),
            text,
            font=font,
            fill=(150, 150, 150)
        )
    except:
        pass
    
    st.image(placeholder, use_container_width=True, caption="Thumbnail Preview (1280x720)")

# Footer
st.divider()
col1, col2 = st.columns(2)

with col1:
    st.markdown("**Standard YouTube size: 1280×720**")
with col2:
    st.markdown("**Export: PNG format**")

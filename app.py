import streamlit as st
import cv2
import numpy as np
import time
from PIL import Image

# Page configuration
st.set_page_config(
    page_title="✨ Invisibility Cloak",
    page_icon="🎭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for amazing styling
st.markdown("""
<style>
    .main-header {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(120deg, #8b5cf6, #ec4899, #f59e0b);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
        animation: gradient 3s ease infinite;
    }
    
    .subtitle {
        text-align: center;
        font-size: 1.2rem;
        color: #94a3b8;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        color: white;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }
    
    .status-active {
        color: #10b981;
        font-weight: bold;
        font-size: 1.1rem;
    }
    
    .status-inactive {
        color: #ef4444;
        font-weight: bold;
        font-size: 1.1rem;
    }
    
    div.stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: 600;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 0.5rem;
        font-size: 1.1rem;
        transition: all 0.3s ease;
    }
    
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">✨ Invisibility Cloak</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Experience the magic of Harry Potter\'s cloak with computer vision! 🪄</p>', unsafe_allow_html=True)

# Sidebar controls
with st.sidebar:
    st.markdown("## 🎛️ Control Panel")
    st.markdown("---")
    
    # Color range sliders
    st.markdown("### 🎨 Red Color Detection")
    lower_hue1 = st.slider("Lower Hue 1", 0, 180, 0)
    upper_hue1 = st.slider("Upper Hue 1", 0, 180, 10)
    
    lower_hue2 = st.slider("Lower Hue 2", 0, 180, 170)
    upper_hue2 = st.slider("Upper Hue 2", 0, 180, 180)
    
    saturation_min = st.slider("Saturation Min", 0, 255, 120)
    value_min = st.slider("Value Min", 0, 255, 70)
    
    st.markdown("---")
    st.markdown("### ⚙️ Processing Settings")
    blur_kernel = st.slider("Blur Kernel Size", 1, 51, 35, step=2)
    morph_kernel = st.slider("Morphology Kernel", 1, 15, 5, step=2)
    
    st.markdown("---")
    st.markdown("### 📷 Camera Settings")
    fps_display = st.checkbox("Show FPS", value=True)
    show_mask = st.checkbox("Show Detection Mask", value=False)

# Initialize session state
if 'running' not in st.session_state:
    st.session_state.running = False
if 'background_captured' not in st.session_state:
    st.session_state.background_captured = False
if 'background' not in st.session_state:
    st.session_state.background = None

# Main content area
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    # Control buttons
    btn_col1, btn_col2, btn_col3, btn_col4 = st.columns(4)
    
    with btn_col1:
        if st.button("📸 Capture Background"):
            with st.spinner("Capturing background..."):
                video = cv2.VideoCapture(0)
                time.sleep(1)
                
                background = None
                for i in range(30):
                    ret, background = video.read()
                
                if background is not None:
                    st.session_state.background = np.flip(background, axis=1)
                    st.session_state.background_captured = True
                    st.success("✅ Background captured!")
                video.release()
    
    with btn_col2:
        if st.button("▶️ Start Magic"):
            if st.session_state.background_captured:
                st.session_state.running = True
            else:
                st.warning("⚠️ Please capture background first!")
    
    with btn_col3:
        if st.button("⏹️ Stop"):
            st.session_state.running = False
    
    with btn_col4:
        if st.button("🔄 Reset"):
            st.session_state.running = False
            st.session_state.background_captured = False
            st.session_state.background = None
            st.rerun()

# Status indicators
st.markdown("---")
status_col1, status_col2, status_col3 = st.columns(3)

with status_col1:
    if st.session_state.background_captured:
        st.markdown('<p class="status-active">🟢 Background Ready</p>', unsafe_allow_html=True)
    else:
        st.markdown('<p class="status-inactive">🔴 Capture Background First</p>', unsafe_allow_html=True)

with status_col2:
    if st.session_state.running:
        st.markdown('<p class="status-active">🟢 Magic Active</p>', unsafe_allow_html=True)
    else:
        st.markdown('<p class="status-inactive">🔴 Paused</p>', unsafe_allow_html=True)

with status_col3:
    st.markdown(f'<p class="status-active">👁️ Live View</p>', unsafe_allow_html=True)

st.markdown("---")

# Video display area
if show_mask:
    video_col1, video_col2 = st.columns(2)
    with video_col1:
        video_placeholder = st.empty()
    with video_col2:
        mask_placeholder = st.empty()
else:
    video_placeholder = st.empty()
    mask_placeholder = None

fps_placeholder = st.empty()

# Info section
with st.expander("ℹ️ How It Works", expanded=False):
    st.markdown("""
    ### The Magic Behind the Cloak 🎩
    
    1. **Background Capture**: First, capture a clean background without any red objects
    2. **Color Detection**: The app detects red-colored fabric using HSV color space
    3. **Masking**: Creates a mask where red color is detected
    4. **Replacement**: Replaces masked areas with the captured background
    5. **Result**: You become invisible! 👻
    
    **Tips for Best Results:**
    - Use a solid red cloth or garment
    - Ensure good lighting
    - Keep the background static
    - Adjust color ranges if detection is poor
    """)

# Main processing loop
if st.session_state.running and st.session_state.background_captured:
    video = cv2.VideoCapture(0)
    prev_time = time.time()
    
    while st.session_state.running:
        ret, frame = video.read()
        if not ret:
            st.error("Failed to access camera!")
            break
        
        # Flip image
        image = np.flip(frame, axis=1)
        
        # Convert to HSV
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # Create masks for red color
        lower1 = np.array([lower_hue1, saturation_min, value_min])
        upper1 = np.array([upper_hue1, 255, 255])
        mask01 = cv2.inRange(hsv, lower1, upper1)
        
        lower2 = np.array([lower_hue2, saturation_min, value_min])
        upper2 = np.array([upper_hue2, 255, 255])
        mask02 = cv2.inRange(hsv, lower2, upper2)
        
        # Combine masks
        mask = mask01 + mask02
        
        # Morphological operations
        kernel = np.ones((morph_kernel, morph_kernel), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_DILATE, kernel)
        
        # Apply invisibility effect
        result = image.copy()
        result[np.where(mask == 255)] = st.session_state.background[np.where(mask == 255)]
        
        # Calculate FPS
        curr_time = time.time()
        fps = 1 / (curr_time - prev_time)
        prev_time = curr_time
        
        # Add FPS overlay
        if fps_display:
            cv2.putText(result, f'FPS: {int(fps)}', (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Convert BGR to RGB for display
        result_rgb = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
        
        # Display
        video_placeholder.image(result_rgb, channels="RGB", use_container_width=True)
        
        if show_mask and mask_placeholder is not None:
            mask_rgb = cv2.cvtColor(mask, cv2.COLOR_GRAY2RGB)
            mask_placeholder.image(mask_rgb, channels="RGB", use_container_width=True)
        
        if fps_display:
            fps_placeholder.metric("⚡ Performance", f"{int(fps)} FPS")
        
        time.sleep(0.03)  # Small delay to prevent overwhelming the display
    
    video.release()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #64748b; padding: 2rem;'>
    <p>Made with ❤️ using OpenCV and Streamlit | Inspired by Harry Potter's Invisibility Cloak 🪄</p>
</div>
""", unsafe_allow_html=True)
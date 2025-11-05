import streamlit as st
import cv2
import numpy as np
import av
import time
from streamlit_webrtc import webrtc_streamer, WebRtcMode, VideoProcessorBase

# ---- PAGE CONFIG ----
st.set_page_config(
    page_title="✨ Invisibility Cloak",
    page_icon="🎭",
    layout="wide"
)

# ---- CUSTOM CSS ----
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
    }
    .subtitle {
        text-align: center;
        font-size: 1.2rem;
        color: #94a3b8;
        margin-bottom: 2rem;
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

st.markdown('<h1 class="main-header">✨ Invisibility Cloak</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Experience Harry Potter’s magic cloak using computer vision! 🪄</p>', unsafe_allow_html=True)

# ---- SIDEBAR ----
with st.sidebar:
    st.markdown("## 🎛️ Control Panel")
    st.markdown("---")

    st.markdown("### 🎨 Color Detection Settings")
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
    show_mask = st.checkbox("Show Mask Preview", value=False)
    show_fps = st.checkbox("Show FPS", value=True)


# ---- VIDEO PROCESSOR CLASS ----
class CloakProcessor(VideoProcessorBase):
    def __init__(self):
        self.background = None
        self.capture_bg = False
        self.magic_on = False
        self.prev_time = time.time()
        self.fps = 0

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        img = cv2.flip(img, 1)

        # Capture background frame
        if self.capture_bg:
            self.background = img.copy()
            self.capture_bg = False

        if self.magic_on and self.background is not None:
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

            lower1 = np.array([lower_hue1, saturation_min, value_min])
            upper1 = np.array([upper_hue1, 255, 255])
            lower2 = np.array([lower_hue2, saturation_min, value_min])
            upper2 = np.array([upper_hue2, 255, 255])

            mask1 = cv2.inRange(hsv, lower1, upper1)
            mask2 = cv2.inRange(hsv, lower2, upper2)
            mask = mask1 + mask2

            kernel = np.ones((morph_kernel, morph_kernel), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_DILATE, kernel)

            result = img.copy()
            result[np.where(mask == 255)] = self.background[np.where(mask == 255)]

            # FPS calculation
            if show_fps:
                curr_time = time.time()
                self.fps = int(1 / (curr_time - self.prev_time))
                self.prev_time = curr_time
                cv2.putText(result, f'FPS: {self.fps}', (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            if show_mask:
                mask_rgb = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
                combined = np.hstack((result, mask_rgb))
                return av.VideoFrame.from_ndarray(combined, format="bgr24")

            return av.VideoFrame.from_ndarray(result, format="bgr24")

        return av.VideoFrame.from_ndarray(img, format="bgr24")


# ---- STREAMLIT-WEBRTC ----
ctx = webrtc_streamer(
    key="cloak-stream",
    mode=WebRtcMode.SENDRECV,
    video_processor_factory=CloakProcessor,
    media_stream_constraints={"video": True, "audio": False},
)

# ---- CONTROL BUTTONS ----
if ctx.video_processor:
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("📸 Capture Background"):
            ctx.video_processor.capture_bg = True
            st.toast("Background captured!", icon="✅")
    with c2:
        if st.button("🪄 Start Magic"):
            if ctx.video_processor.background is not None:
                ctx.video_processor.magic_on = True
                st.toast("Magic activated!", icon="✨")
            else:
                st.warning("Please capture background first!")
    with c3:
        if st.button("⏹️ Stop"):
            ctx.video_processor.magic_on = False
            st.toast("Stopped.", icon="🛑")
    with c4:
        if st.button("🔄 Reset"):
            ctx.video_processor.background = None
            ctx.video_processor.magic_on = False
            st.toast("Reset done.", icon="♻️")

# ---- INFO ----
st.markdown("---")
with st.expander("ℹ️ How It Works"):
    st.markdown("""
    ### 🪄 The Magic Behind the Cloak
    1. Capture a clean background.
    2. Wear a red cloth (detected in HSV color space).
    3. Detected red areas are replaced with the saved background.
    4. Voila — invisibility achieved!

    **Tips for best results:**
    - Use bright red cloth.
    - Ensure good lighting.
    - Keep background static.
    """)

st.markdown("""
<div style='text-align:center; color:#94a3b8; margin-top:2rem;'>
    Made with ❤️ using OpenCV + Streamlit + WebRTC | Inspired by Harry Potter 🪄
</div>
""", unsafe_allow_html=True)

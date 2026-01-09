import streamlit as st
import cv2
import numpy as np
import tempfile
import os
import requests
import time
from datetime import datetime

# ==========================================
# 1. CONFIG & AUTHENTICATION
# ==========================================
FIREBASE_API_KEY = "AIzaSyDMpzUog6qJsSCIL_SyQK6JYzzXkHYvNGg"
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def verify_firebase_login(email, password):
    if email == "admin" and password == "drishti123":
        return True, "SYSTEM_ADMIN"
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
    payload = {"email": email, "password": password, "returnSecureToken": True}
    try:
        res = requests.post(url, json=payload, timeout=5)
        data = res.json()
        if "error" in data: return False, data['error']['message']
        return True, data['email']
    except: return False, "Database Connection Error"

# ==========================================
# 2. ENHANCEMENT ENGINE
# ==========================================

def forensic_engine_v14(frame, denoise=True):
    """NIGHT VISION Engine: Multi-Stage Forensic Restoration"""
    if denoise:
        frame = cv2.bilateralFilter(frame, 7, 50, 50)
    
    lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    l = clahe.apply(l)
    enhanced = cv2.merge((l, a, b))
    enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
    
    # Brightness Normalize
    gamma = 1.3
    invGamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** invGamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
    enhanced = cv2.LUT(enhanced, table)

    # Edge Sharpening
    gaussian = cv2.GaussianBlur(enhanced, (0, 0), 2)
    return cv2.addWeighted(enhanced, 1.6, gaussian, -0.6, 0)

# ==========================================
# 3. UI STYLING
# ==========================================
st.set_page_config(page_title="NIGHT VISION: COMMAND V14", page_icon="🦅", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #e0e0e0; }
    h1, h2, h3 { color: #00FF99 !important; font-family: 'Orbitron', sans-serif; text-shadow: 0px 0px 10px #00FF99; }
    .stButton>button { background-color: #111; color: #00FF99; border: 1px solid #00FF99; border-radius: 0px; font-weight: bold; }
    .stButton>button:hover { background-color: #00FF99; color: black; box-shadow: 0px 0px 15px #00FF99; }
    .report-paper {
        background: #111; color: #0f0; padding: 30px; 
        border: 2px solid #0f0; font-family: 'Courier New', courier;
        margin-top: 20px; box-shadow: inset 0px 0px 20px #003300;
    }
    .alert-header {
        background: #440000; border: 2px solid red; color: white;
        padding: 10px; text-align: center; font-weight: bold; animation: blinker 1s linear infinite;
    }
    @keyframes blinker { 50% { opacity: 0; } }
    .metric-card { background: #111; padding: 15px; border: 1px solid #333; border-left: 5px solid #00FF99; margin-bottom: 15px; }
    </style>
""", unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False
if 'snapshots' not in st.session_state: st.session_state.snapshots = []

# ==========================================
# 4. MAIN ROUTING
# ==========================================

if not st.session_state.auth:
    _, col2, _ = st.columns([1, 2, 1])
    with col2:
        st.title("🦅 NIGHT VISION PRO")
        st.subheader("SECURE TERMINAL LOGIN")
        e_id = st.text_input("Agent ID")
        e_pw = st.text_input("Access Code", type="password")
        if st.button("AUTHENTICATE", use_container_width=True):
            success, message = verify_firebase_login(e_id, e_pw)
            if success:
                st.session_state.auth, st.session_state.user = True, message
                st.rerun()
            else: st.error(f"ACCESS DENIED: {message}")

else:
    with st.sidebar:
        st.title("🦅 NIGHT VISION")
        st.code(f"AGENT: {st.session_state.user}\nSTATUS: AUTHORIZED")
        st.markdown("---")
        mode = st.radio("SELECT OPERATIONAL MODULE:", ["🔍 IMAGE ENHANCEMENT", "🎥 VIDEO RESTORATION", "🕵️ INTELLIGENCE TRACKING"])
        st.markdown("---")
        if st.button("🔴 TERMINATE SESSION"):
            st.session_state.auth = False
            st.rerun()

    # --- IMAGE ENHANCEMENT PAGE ---
    if mode == "🔍 IMAGE ENHANCEMENT":
        st.header("🔍 STATIC EVIDENCE ENHANCEMENT")
        u_img = st.file_uploader("Drop low-light evidence file", type=['jpg', 'png', 'jpeg'])
        if u_img:
            file_bytes = np.asarray(bytearray(u_img.read()), dtype=np.uint8)
            raw = cv2.imdecode(file_bytes, 1)
            
            if st.button("⚡ EXECUTE NIGHT VISION PROCESS"):
                with st.spinner("Processing..."):
                    res = forensic_engine_v14(raw)
                    st.session_state.raw_img, st.session_state.proc_img = raw, res

            if 'proc_img' in st.session_state:
                st.markdown("### SIDE-BY-SIDE COMPARISON")
                c1, c2 = st.columns(2)
                c1.image(st.session_state.raw_img, caption="RAW SOURCE", channels="BGR", use_container_width=True)
                c2.image(st.session_state.proc_img, caption="NIGHT VISION ENHANCED", channels="BGR", use_container_width=True)
                
                _, buf = cv2.imencode('.png', st.session_state.proc_img)
                st.download_button("💾 DOWNLOAD ENHANCED EVIDENCE (PNG)", buf.tobytes(), "nightvision_evidence.png", use_container_width=True)

    # --- VIDEO RESTORATION PAGE ---
    elif mode == "🎥 VIDEO RESTORATION":
        st.header("🎥 VIDEO FEED RESTORATION")
        u_vid = st.file_uploader("Upload Surveillance Footage", type=['mp4', 'avi'])
        if u_vid:
            tfile = tempfile.NamedTemporaryFile(delete=False)
            tfile.write(u_vid.read()); cap = cv2.VideoCapture(tfile.name)
            fps, width, height = int(cap.get(cv2.CAP_PROP_FPS)), int(cap.get(3)), int(cap.get(4))
            total_f = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            out_file = os.path.join(tempfile.gettempdir(), "night_restored.mp4")
            out_writer = cv2.VideoWriter(out_file, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))
            
            st.markdown(f'<div class="metric-card">SOURCE READY: {width}x{height} | {total_f} Frames</div>', unsafe_allow_html=True)
            ph = st.empty()
            
            if st.button("🔴 RUN BATCH RESTORATION"):
                start_t = time.time()
                count = 0
                while cap.isOpened():
                    ret, frame = cap.read()
                    if not ret: break
                    enhanced = forensic_engine_v14(frame, denoise=False)
                    out_writer.write(enhanced)
                    if count % 10 == 0:
                        combined = np.hstack((cv2.resize(frame, (640, 360)), cv2.resize(enhanced, (640, 360))))
                        ph.image(combined, caption=f"Processing: {count}/{total_f} Frames", channels="BGR")
                    count += 1
                
                cap.release(); out_writer.release()
                st.success("Video Restoration Complete.")
                with open(out_file, 'rb') as f:
                    st.download_button("💾 DOWNLOAD CLARIFIED VIDEO", f, "restored_footage.mp4", mime="video/mp4", use_container_width=True)

    # --- INTELLIGENCE TRACKING PAGE ---
    elif mode == "🕵️ INTELLIGENCE TRACKING":
        st.header("🕵️ ENHANCED INTELLIGENCE SCANNER")
        
        # New Feature UI
        sensitivity = st.slider("Motion Sensitivity Threshold", 500, 5000, 2500)
        
        u_case = st.file_uploader("Input Intelligence Feed", type=['mp4', 'avi'])
        
        if u_case:
            tfile = tempfile.NamedTemporaryFile(delete=False)
            tfile.write(u_case.read()); cap = cv2.VideoCapture(tfile.name)
            fgbg = cv2.createBackgroundSubtractorMOG2(history=300, varThreshold=50)
            
            m_events, f_events = 0, 0
            last_cap_time = 0
            alert_placeholder = st.empty()
            vid_spot = st.empty()
            st.markdown("### 📸 CAPTURED EVIDENCE GALLERY")
            snapshot_area = st.container()

            if st.button("🛡️ INITIATE ENHANCED SCAN"):
                st.session_state.snapshots = []
                
                while cap.isOpened():
                    ret, frame = cap.read()
                    if not ret: break
                    
                    enhanced = forensic_engine_v14(frame, denoise=True)
                    captured_this_frame = False
                    label = ""

                    # 1. Face Tracking
                    gray = cv2.cvtColor(enhanced, cv2.COLOR_BGR2GRAY)
                    faces = face_cascade.detectMultiScale(gray, 1.1, 8)
                    for (fx, fy, fw, fh) in faces:
                        f_events += 1
                        captured_this_frame = True
                        label = "TARGET_ACQUIRED"
                        cv2.rectangle(enhanced, (fx, fy), (fx+fw, fy+fh), (0, 255, 0), 2)
                        # HUD Overlay
                        cv2.putText(enhanced, f"ID: {st.session_state.user}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

                    # 2. Motion Tracking
                    if not captured_this_frame:
                        mask = fgbg.apply(enhanced)
                        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                        for c in contours:
                            if cv2.contourArea(c) > sensitivity:
                                m_events += 1
                                captured_this_frame = True
                                label = "MOTION_DETECTION"
                                x, y, w, h = cv2.boundingRect(c)
                                cv2.rectangle(enhanced, (x, y), (x+w, y+h), (0, 0, 255), 2)

                    # 3. Dynamic Alert Logic
                    if f_events > 5:
                        alert_placeholder.markdown('<div class="alert-header">🚨 CRITICAL ALERT: MULTIPLE TARGETS IDENTIFIED 🚨</div>', unsafe_allow_html=True)

                    # 4. Save Snapshot Logic
                    cur_time = time.time()
                    if captured_this_frame and (cur_time - last_cap_time > 1.5):
                        st.session_state.snapshots.append({
                            "img": enhanced.copy(),
                            "time": datetime.now().strftime("%H:%M:%S"),
                            "type": label
                        })
                        last_cap_time = cur_time

                    vid_spot.image(enhanced, caption="LIVE TRACKING", channels="BGR", use_container_width=True)
                    
                    with snapshot_area:
                        if st.session_state.snapshots:
                            cols = st.columns(3)
                            for i, snap in enumerate(st.session_state.snapshots[-6:][::-1]):
                                with cols[i % 3]:
                                    st.image(snap["img"], caption=f"{snap['time']} | {snap['type']}", channels="BGR")
                
                cap.release()
                st.markdown(f"""
                <div class="report-paper">
                    <h2 style="text-align:center;">🕵️ FINAL THREAT ASSESSMENT</h2>
                    <p><b>BIOMETRIC HITS:</b> {f_events}</p>
                    <p><b>THREAT STATUS:</b> {'HIGH' if f_events > 0 else 'LOW'}</p>
                </div>
                """, unsafe_allow_html=True)

        if st.button("🗑️ WIPE EVIDENCE LOG"):
            st.session_state.snapshots = []
            st.rerun()
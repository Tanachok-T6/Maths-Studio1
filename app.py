import streamlit as st
import datetime
from zoneinfo import ZoneInfo
import threading
import requests
import time

# ==========================================
# 0. ข้อมูลโจทย์ (5 ด่าน ด่านละ 5 ข้อ)
# ==========================================
QUIZ_DATA = {
    1:[
        {"q": "2x + 3x มีค่าเท่ากับเท่าใด?", "options": ["5x", "6x", "5x^2", "x"], "ans": "5x"},
        {"q": "5y - 2y มีค่าเท่ากับเท่าใด?", "options":["3", "3y", "7y", "10y"], "ans": "3y"},
        {"q": "4a + a มีค่าเท่ากับเท่าใด?", "options":["4", "5a", "4a^2", "a"], "ans": "5a"},
        {"q": "10b - 4b มีค่าเท่ากับเท่าใด?", "options":["6", "14b", "6b", "6b^2"], "ans": "6b"},
        {"q": "x + x + x มีค่าเท่ากับเท่าใด?", "options": ["3x", "x^3", "3", "3x^2"], "ans": "3x"},
    ],
    2:[
        {"q": "x * x มีค่าเท่ากับเท่าใด?", "options":["2x", "x^2", "x", "1"], "ans": "x^2"},
        {"q": "2x * 3x มีค่าเท่ากับเท่าใด?", "options": ["5x", "6x", "6x^2", "5x^2"], "ans": "6x^2"},
        {"q": "4y * 2 มีค่าเท่ากับเท่าใด?", "options": ["6y", "8y", "8", "8y^2"], "ans": "8y"},
        {"q": "(-3a) * 2a มีค่าเท่ากับเท่าใด?", "options": ["-6a", "-6a^2", "6a^2", "-a"], "ans": "-6a^2"},
        {"q": "5b * (-2b) มีค่าเท่ากับเท่าใด?", "options": ["-10b^2", "10b^2", "-3b", "-10b"], "ans": "-10b^2"},
    ],
    3:[
        {"q": "2(x + 3) มีค่าเท่ากับเท่าใด?", "options":["2x + 3", "2x + 6", "5x", "x + 6"], "ans": "2x + 6"},
        {"q": "3(y - 2) มีค่าเท่ากับเท่าใด?", "options": ["3y - 6", "3y - 2", "y - 6", "-3y"], "ans": "3y - 6"},
        {"q": "-2(a + 4) มีค่าเท่ากับเท่าใด?", "options":["-2a + 8", "-2a - 4", "-2a - 8", "2a - 8"], "ans": "-2a - 8"},
        {"q": "x(x + 5) มีค่าเท่ากับเท่าใด?", "options":["x^2 + 5", "x^2 + 5x", "2x + 5", "5x^2"], "ans": "x^2 + 5x"},
        {"q": "2y(y - 3) มีค่าเท่ากับเท่าใด?", "options":["2y^2 - 3", "2y^2 - 6y", "2y - 6y", "4y^2"], "ans": "2y^2 - 6y"},
    ],
    4:[
        {"q": "(x + 1)(x + 2) มีค่าเท่ากับเท่าใด?", "options":["x^2 + 3x + 2", "x^2 + 2", "2x + 3", "x^2 + 2x + 1"], "ans": "x^2 + 3x + 2"},
        {"q": "(y - 2)(y + 3) มีค่าเท่ากับเท่าใด?", "options":["y^2 + y - 6", "y^2 - 6", "y^2 + 5y - 6", "2y + 1"], "ans": "y^2 + y - 6"},
        {"q": "(a + 3)^2 มีค่าเท่ากับเท่าใด?", "options":["a^2 + 9", "a^2 + 6a + 9", "2a + 6", "a^2 + 3a + 9"], "ans": "a^2 + 6a + 9"},
        {"q": "(b - 4)(b - 4) มีค่าเท่ากับเท่าใด?", "options":["b^2 - 16", "b^2 - 8b + 16", "b^2 + 16", "2b - 8"], "ans": "b^2 - 8b + 16"},
        {"q": "(x + 5)(x - 5) มีค่าเท่ากับเท่าใด?", "options":["x^2 - 25", "x^2 + 25", "x^2 - 10x - 25", "2x"], "ans": "x^2 - 25"},
    ],
    5:[
        {"q": "แยกตัวประกอบ x^2 + 5x + 6", "options":["(x+1)(x+6)", "(x+2)(x+3)", "(x-2)(x-3)", "(x+5)(x+1)"], "ans": "(x+2)(x+3)"},
        {"q": "แยกตัวประกอบ y^2 - 9", "options":["(y-3)^2", "(y+3)(y-3)", "(y-9)(y+1)", "y(y-9)"], "ans": "(y+3)(y-3)"},
        {"q": "แยกตัวประกอบ a^2 - 4a + 4", "options":["(a-2)^2", "(a+2)^2", "(a-4)(a+1)", "(a-2)(a+2)"], "ans": "(a-2)^2"},
        {"q": "แยกตัวประกอบ 2x^2 + 4x", "options":["2(x^2+2)", "2x(x+2)", "x(2x+4)", "2x(x+4)"], "ans": "2x(x+2)"},
        {"q": "แยกตัวประกอบ x^2 - x - 12", "options":["(x-4)(x+3)", "(x+4)(x-3)", "(x-6)(x+2)", "(x-12)(x+1)"], "ans": "(x-4)(x+3)"},
    ]
}

# ==========================================
# 1. ระบบ Log และ Tracking
# ==========================================
class GlobalTracker:
    def __init__(self):
        self.active_count = 0
        self.lock = threading.Lock()
    def increment(self):
        with self.lock:
            self.active_count += 1
            return self.active_count
    def decrement(self):
        with self.lock:
            self.active_count -= 1
            return self.active_count

@st.cache_resource
def get_global_tracker():
    return GlobalTracker()

def get_user_ip():
    try:
        return requests.get('https://api.ipify.org', timeout=5).text
    except:
        return "Unknown"

global_tracker = get_global_tracker()
if 'ip' not in st.session_state:
    st.session_state.ip = get_user_ip()
    global_tracker.increment()

# ==========================================
# 2. การจัดการ State ของเกม
# ==========================================
if 'unlocked_levels' not in st.session_state: st.session_state.unlocked_levels = 1
if 'current_level' not in st.session_state: st.session_state.current_level = 1
if 'q_index' not in st.session_state: st.session_state.q_index = 0
if 'score' not in st.session_state: st.session_state.score = 0
if 'feedback' not in st.session_state: st.session_state.feedback = None
if 'level_finished' not in st.session_state: st.session_state.level_finished = False

def change_level(level):
    st.session_state.current_level = level
    st.session_state.q_index = 0
    st.session_state.score = 0
    st.session_state.feedback = None
    st.session_state.level_finished = False

def check_answer(selected, correct):
    if selected == correct:
        st.session_state.score += 1
        st.session_state.feedback = 'correct'
    else:
        st.session_state.feedback = 'incorrect'
    
    st.session_state.q_index += 1
    if st.session_state.q_index >= 5:
        st.session_state.level_finished = True

# ==========================================
# 3. CSS ตกแต่ง
# ==========================================
st.set_page_config(page_title="Maths Studio", page_icon="🔢", layout="wide")
st.markdown("""
<style>
    /* บังคับสีพื้นหลังของกล่องโจทย์ */
    .question-box { 
        background-color: #ffffff !important; 
        color: #000000 !important; 
        padding: 30px; 
        border-radius: 20px; 
        border: 2px solid #0d6efd; 
        font-size: 24px; 
        font-weight: bold; 
        text-align: center; 
        margin-bottom: 20px; 
    }
            
    .feedback-overlay { 
        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; 
        background: rgba(255, 255, 255, 0.98); /* เพิ่มความทึบแสงเพื่อให้เห็นชัดขึ้น */
        z-index: 999999; 
        display: flex; flex-direction: column; justify-content: center; align-items: center; 
    }
            
    .big-icon { 
        font-size: 300px; 
        animation: pulse 0.5s ease-in-out; 
    }
            
    @keyframes pulse {
        0% { transform: scale(0.5); opacity: 0; }
        100% { transform: scale(1); opacity: 1; }
    }
    
    /* บังคับสีตัวอักษรในปุ่มให้เห็นชัดใน Dark Mode */
    div[data-testid="stButton"] button {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 2px solid #0d6efd !important;
        font-size: 18px !important;
        font-weight: bold !important;
    }
    
    /* ส่วนเดิมของคุณ */
    .school-title { position: fixed; top: 14px; left: 50%; transform: translateX(-50%); z-index: 999999; font-size: 26px; font-weight: 800; color: #FFFFFF !important; }
    .feedback-overlay { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(255, 255, 255, 0.9); z-index: 99999; display: flex; flex-direction: column; justify-content: center; align-items: center; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 4. แสดงผล Feedback (ถูก/ผิด)
# ==========================================
if st.session_state.feedback:
    if st.session_state.feedback == 'correct':
        st.markdown("""
            <div class='feedback-overlay'>
                <div class='big-icon'>✅</div>
                <h1 style='color: #28a745; font-size: 60px;'>ถูกต้อง!</h1>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div class='feedback-overlay'>
                <div class='big-icon'>❌</div>
                <h1 style='color: #dc3545; font-size: 60px;'>ผิดพลาด!</h1>
            </div>
        """, unsafe_allow_html=True)
    
    time.sleep(1.2) # หน่วงเวลาไว้เพื่อให้เห็นเต็มๆ ตา 1.2 วินาที
    st.session_state.feedback = None
    st.rerun()

# ==========================================
# 5. แถบข้าง (Sidebar)
# ==========================================
with st.sidebar:
    st.header("🔢 Maths Studio")
    st.write(f"🌐 IP: {st.session_state.ip}")
    st.write(f"👥 ออนไลน์: {global_tracker.active_count}")
    st.markdown("---")
    for i in range(1, 6):
        disabled = i > st.session_state.unlocked_levels
        if st.button(f"ด่านที่ {i} {'🔒' if disabled else '🟢'}", disabled=disabled, use_container_width=True):
            change_level(i)
            st.rerun()

# ==========================================
# 6. หน้าจอหลัก
# ==========================================
st.title(f"🎮 ด่านที่ {st.session_state.current_level}")

if st.session_state.level_finished:
    score = st.session_state.score
    st.subheader(f"📊 สรุปคะแนน: {score} / 5")
    if score >= 3:
        st.success("🎉 ผ่านด่านแล้ว!")
        if st.session_state.unlocked_levels == st.session_state.current_level:
            st.session_state.unlocked_levels += 1
        if st.button("ถัดไป"):
            change_level(st.session_state.current_level + 1)
            st.rerun()
    else:
        st.error("❌ ไม่ผ่านเกณฑ์ ลองใหม่อีกครั้งนะ")
        if st.button("ลองใหม่"):
            change_level(st.session_state.current_level)
            st.rerun()
else:
    q_data = QUIZ_DATA[st.session_state.current_level][st.session_state.q_index]
    st.markdown(f"<div class='question-box'>{q_data['q']}</div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    for i, opt in enumerate(q_data['options']):
        with (col1 if i < 2 else col2):
            if st.button(opt, key=f"opt_{i}", use_container_width=True):
                check_answer(opt, q_data['ans'])
                st.rerun()
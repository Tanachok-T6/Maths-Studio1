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
        {"q": "2x + 3x ", "options": ["5x", "6x", "5x^2", "x"], "ans": "5x"},
        {"q": "5y - 2y ", "options":["3", "3y", "7y", "10y"], "ans": "3y"},
        {"q": "4a + a ", "options":["4", "5a", "4a^2", "a"], "ans": "5a"},
        {"q": "10b - 4b ", "options":["6", "14b", "6b", "6b^2"], "ans": "6b"},
        {"q": "x + x + x ", "options": ["3x", "x^3", "3", "3x^2"], "ans": "3x"},
    ],
    2:[
        {"q": "x * x ", "options":["2x", "x^2", "x", "1"], "ans": "x^2"},
        {"q": "2x * 3x ", "options": ["5x", "6x", "6x^2", "5x^2"], "ans": "6x^2"},
        {"q": "4y * 2 ", "options": ["6y", "8y", "8", "8y^2"], "ans": "8y"},
        {"q": "(-3a) * 2a ", "options": ["-6a", "-6a^2", "6a^2", "-a"], "ans": "-6a^2"},
        {"q": "5b * (-2b) ", "options": ["-10b^2", "10b^2", "-3b", "-10b"], "ans": "-10b^2"},
    ],
    3:[
        {"q": "2(x + 3) ", "options":["2x + 3", "2x + 6", "5x", "x + 6"], "ans": "2x + 6"},
        {"q": "3(y - 2) ", "options": ["3y - 6", "3y - 2", "y - 6", "-3y"], "ans": "3y - 6"},
        {"q": "-2(a + 4) ", "options":["-2a + 8", "-2a - 4", "-2a - 8", "2a - 8"], "ans": "-2a - 8"},
        {"q": "x(x + 5) ", "options":["x^2 + 5", "x^2 + 5x", "2x + 5", "5x^2"], "ans": "x^2 + 5x"},
        {"q": "2y(y - 3) ", "options":["2y^2 - 3", "2y^2 - 6y", "2y - 6y", "4y^2"], "ans": "2y^2 - 6y"},
    ],
    4:[
        {"q": "(x + 1)(x + 2) ", "options":["x^2 + 3x + 2", "x^2 + 2", "2x + 3", "x^2 + 2x + 1"], "ans": "x^2 + 3x + 2"},
        {"q": "(y - 2)(y + 3) ", "options":["y^2 + y - 6", "y^2 - 6", "y^2 + 5y - 6", "2y + 1"], "ans": "y^2 + y - 6"},
        {"q": "(a + 3)^2 ", "options":["a^2 + 9", "a^2 + 6a + 9", "2a + 6", "a^2 + 3a + 9"], "ans": "a^2 + 6a + 9"},
        {"q": "(b - 4)(b - 4) ", "options":["b^2 - 16", "b^2 - 8b + 16", "b^2 + 16", "2b - 8"], "ans": "b^2 - 8b + 16"},
        {"q": "(x + 5)(x - 5) ", "options":["x^2 - 25", "x^2 + 25", "x^2 - 10x - 25", "2x"], "ans": "x^2 - 25"},
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
        headers = st.context.headers
        if "X-Forwarded-For" in headers: return headers["X-Forwarded-For"].split(",")[0]
        return requests.get('https://api.ipify.org', timeout=5).text
    except:
        return "Unknown IP"

class SessionMonitor:
    def __init__(self, tracker, ip):
        self.tracker = tracker
        self.ip = ip
        self.start_time = datetime.datetime.now(ZoneInfo("Asia/Bangkok")).strftime('%H:%M:%S')
        count = self.tracker.increment()
        print(f"🟢 [เข้าสู่ระบบ] IP: {self.ip} | เวลา: {self.start_time} | ออนไลน์: {count}")
    def __del__(self):
        count = self.tracker.decrement()
        print(f"🔴 [ออกระบบ] IP: {self.ip} | ออนไลน์เหลือ: {count}")

global_tracker = get_global_tracker()
user_ip = get_user_ip()

if 'monitor' not in st.session_state:
    st.session_state.monitor = SessionMonitor(global_tracker, user_ip)

# ==========================================
# 2. การจัดการ State ของเกม (Session State)
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
    is_correct = (selected == correct)
    
    if is_correct:
        st.session_state.score += 1
        st.session_state.feedback = 'correct'
        print(f"✅ [LOG - ถูก] IP: {user_ip} | ด่าน: {st.session_state.current_level} | ข้อ: {st.session_state.q_index + 1} | ตอบ: {selected}")
    else:
        st.session_state.feedback = 'incorrect'
        print(f"❌ [LOG - ผิด] IP: {user_ip} | ด่าน: {st.session_state.current_level} | ข้อ: {st.session_state.q_index + 1} | ตอบ: {selected} (เฉลย: {correct})")
    
    st.session_state.q_index += 1
    if st.session_state.q_index >= 5:
        st.session_state.level_finished = True

# ==========================================
# 3. การตั้งค่าหน้าจอและ CSS
# ==========================================
st.set_page_config(page_title="Maths Studio", page_icon="🔢", layout="wide")

st.markdown("""
<style>
    .school-title { 
        position: fixed; top: 14px; left: 50%; transform: translateX(-50%); 
        z-index: 999999; font-size: 26px; font-weight: 800; 
        color: #FFFFFF !important; pointer-events: none; 
    }
    .ip-box { 
        background-color: #f0f2f6; padding: 12px; border-radius: 12px; 
        text-align: center; border: 1px solid #ddd; margin-bottom: 15px;
    }
    /* Overlay สำหรับเครื่องหมายถูก/ผิด */
    .feedback-overlay {
        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        background: rgba(255, 255, 255, 0.9); z-index: 99999;
        display: flex; flex-direction: column; justify-content: center; align-items: center;
    }
    .icon-correct { font-size: 150px; color: #28a745; animation: pop 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275); text-align: center; }
    .icon-incorrect { font-size: 150px; color: #dc3545; animation: pop 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275); text-align: center; }
    @keyframes pop { 0% { transform: scale(0); opacity: 0; } 100% { transform: scale(1); opacity: 1; } }
    
    /* ตกแต่งกล่องโจทย์ */
    .question-box {
        background: linear-gradient(135deg, #0d6efd, #0056b3);
        color: white; padding: 40px; border-radius: 20px;
        font-size: 32px; font-weight: bold; text-align: center;
        margin-bottom: 30px; box-shadow: 0 10px 20px rgba(0,0,0,0.1);
    }
    .stButton>button { height: 60px; font-size: 20px; font-weight: bold; border-radius: 15px; }
</style>
<div class="school-title">CRMS6</div>
""", unsafe_allow_html=True)

@st.fragment(run_every=3)
def sync_active_users():
    st.markdown(f"""
    <div class="ip-box">
        <div style="font-size: 0.9rem; margin-bottom: 5px;">🌐 IP: <b style="color: #0d6efd;">{user_ip}</b></div>
        <div style="font-size: 0.85rem; color: #555; border-top: 1px solid #ddd; padding-top: 5px;">
            👥 ออนไลน์ขณะนี้: <b>{global_tracker.active_count} คน</b>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# 4. แถบ Sidebar (เลือกด่าน)
# ==========================================
with st.sidebar:
    st.header("🔢 Maths Studio")
    sync_active_users()
    st.markdown("---")
    st.subheader("🗺️ เลือกด่าน")
    
    for i in range(1, 6):
        if i <= st.session_state.unlocked_levels:
            # ด่านที่ปลดล็อกแล้ว ให้กดเข้าเล่นได้
            if st.button(f"🟢 ด่านที่ {i} (ปลดล็อกแล้ว)", key=f"btn_lvl_{i}", use_container_width=True):
                change_level(i)
                st.rerun()
        else:
            # ด่านที่ยังล็อกอยู่
            st.button(f"🔒 ด่านที่ {i} (ล็อก)", key=f"btn_lvl_{i}", disabled=True, use_container_width=True)

# ==========================================
# 5. แสดงผลลัพธ์ (ถูก/ผิด) แบบ Animation เด้งกลางจอ
# ==========================================
if st.session_state.feedback:
    if st.session_state.feedback == 'correct':
        st.markdown("""<div class='feedback-overlay'><div class='icon-correct'>✅<br><span style='font-size: 40px;'>ยอดเยี่ยม!</span></div></div>""", unsafe_allow_html=True)
    else:
        st.markdown("""<div class='feedback-overlay'><div class='icon-incorrect'>❌<br><span style='font-size: 40px;'>ผิดครับ!</span></div></div>""", unsafe_allow_html=True)
    
    time.sleep(1.2) # หน่วงเวลาโชว์เครื่องหมาย 1.2 วินาที
    st.session_state.feedback = None
    st.rerun()

# ==========================================
# 6. หน้าจอหลัก (แสดงโจทย์ / สรุปผลด่าน)
# ==========================================
current_lvl = st.session_state.current_level

st.title(f"🎮 ด่านที่ {current_lvl}")
st.progress(st.session_state.q_index / 5)

if st.session_state.level_finished:
    score = st.session_state.score
    st.markdown("---")
    st.subheader(f"📊 สรุปคะแนนด่านที่ {current_lvl}: {score} / 5")
    
    if score >= 3:
        st.success("🎉 ยินดีด้วย! คุณผ่านเกณฑ์ (ตอบถูก 3 ข้อขึ้นไป)")
        if current_lvl < 5:
            if st.session_state.unlocked_levels <= current_lvl:
                st.session_state.unlocked_levels = current_lvl + 1
            st.info(f"ปลดล็อกด่านที่ {current_lvl + 1} แล้ว! ดูที่แถบด้านซ้ายมือ")
            if st.button("➡️ ไปด่านถัดไป", type="primary"):
                change_level(current_lvl + 1)
                st.rerun()
        else:
            st.balloons()
            st.success("🏆 คุณเคลียร์ครบทุกด่านแล้ว! เก่งมากๆ!")
    else:
        st.error("😢 เสียใจด้วย คุณตอบถูกไม่ถึง 3 ข้อ ต้องทำด่านนี้ใหม่อีกครั้ง")
        if st.button("🔄 ลองทำใหม่อีกครั้ง", type="primary"):
            change_level(current_lvl)
            st.rerun()

else:
    # แสดงโจทย์ปัจจุบัน
    q_data = QUIZ_DATA[current_lvl][st.session_state.q_index]
    
    st.markdown(f"<div class='question-box'>ข้อที่ {st.session_state.q_index + 1}: <br>{q_data['q']}</div>", unsafe_allow_html=True)
    
    # วาดปุ่มตัวเลือก 4 ปุ่ม เป็น Grid 2x2
    col1, col2 = st.columns(2)
    options = q_data['options']
    ans = q_data['ans']
    
    with col1:
        if st.button(options[0], use_container_width=True): check_answer(options[0], ans)
        if st.button(options[1], use_container_width=True): check_answer(options[1], ans)
    with col2:
        if st.button(options[2], use_container_width=True): check_answer(options[2], ans)
        if st.button(options[3], use_container_width=True): check_answer(options[3], ans)

# Footer เวลา
bangkok_now = datetime.datetime.now(ZoneInfo("Asia/Bangkok"))
st.markdown("<br><br><hr>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; color: gray;'>เวลาที่เข้าใช้งาน (TH): {bangkok_now.strftime('%d/%m/%Y %H:%M:%S')}</p>", unsafe_allow_html=True)
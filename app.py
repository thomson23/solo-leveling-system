import streamlit as st
import requests

# 1. ตั้งค่าหน้าจอและดีไซน์ (Glassmorphic & Neon Theme)
st.set_page_config(page_title="Solo Leveling System", page_icon="⚔️", layout="centered")

st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    div[data-testid="stVerticalBlock"] > div.element-container {
        background: rgba(255, 255, 255, 0.02);
        border-radius: 15px;
        border: 1px solid rgba(0, 242, 255, 0.15);
        padding: 5px;
    }
    .quest-title {
        font-size: 26px !important;
        font-weight: bold;
        color: #00f2ff;
        text-shadow: 0 0 8px rgba(0, 242, 255, 0.4);
        margin-bottom: 2px;
    }
    .quest-caption {
        font-size: 16px !important;
        color: #bbbbbb;
    }
    .stButton > button {
        width: 100%;
        border-radius: 10px;
        border: 1px solid #00f2ff;
        background: rgba(0, 242, 255, 0.08);
        color: white;
        font-size: 18px !important;
        height: 50px;
        transition: 0.3s;
    }
    .stButton > button:hover {
        background: #00f2ff;
        color: black;
        box-shadow: 0 0 15px #00f2ff;
    }
    .reset-btn button {
        background-color: rgba(255, 75, 75, 0.1) !important;
        border: 1px solid #ff4b4b !important;
        color: #ff4b4b !important;
        font-size: 15px !important;
        height: 42px !important;
    }
    div[data-testid="stMetricValue"] {
        font-size: 55px !important;
        color: #00f2ff !important;
    }
</style>
""", unsafe_allow_html=True)

# ดึงลิงก์เชื่อมโยงตัวใหม่จากระบบ Secrets
try:
    API_URL = st.secrets["connections"]["gsheets"]["spreadsheet"]
except:
    API_URL = ""

# ฟังก์ชันโหลดข้อมูลตอนเปิดแอป
def load_data_from_system():
    if not API_URL:
        return {"level": 1, "exp": 0}
    try:
        response = requests.get(f"{API_URL}?action=get")
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return {"level": 1, "exp": 0}

# ฟังก์ชันสั่ง Auto-Save ลงฐานข้อมูลจริง
def save_data_to_system(level, exp):
    if not API_URL:
        return
    try:
        requests.get(f"{API_URL}?action=set&level={int(level)}&exp={int(exp)}")
    except:
        pass

# --- เริ่มดึงข้อมูลระบบ ---
if 'level' not in st.session_state:
    saved_data = load_data_from_system()
    st.session_state.level = int(saved_data.get('level', 1))
    st.session_state.exp = int(saved_data.get('exp', 0))
    st.session_state.max_exp = 100 * (1.5 ** (st.session_state.level - 1))

def add_reward(stat_name, stat_val, exp_reward):
    st.session_state.exp += exp_reward
    while st.session_state.exp >= st.session_state.max_exp:
        st.session_state.exp -= st.session_state.max_exp
        st.session_state.level += 1
        st.session_state.max_exp *= 1.5
    
    # สั่งบันทึกข้อมูลสดใหม่ลง Google Sheets ทันทีที่อัปเวลหรือได้แต้ม
    save_data_to_system(st.session_state.level, st.session_state.exp)

# --- โครงสร้างหน้าจอหลัก ---
st.markdown("<h1 style='text-align: center; color: #00f2ff;'>SYSTEM : SOLO LEVELING</h1>", unsafe_allow_html=True)

col1, col2 = st.columns([1, 1])
with col1:
    st.metric(label="PLAYER LEVEL", value=st.session_state.level)
with col2:
    progress = min(st.session_state.exp / st.session_state.max_exp, 1.0)
    st.write(f"### EXP: {int(st.session_state.exp)} / {int(st.session_state.max_exp)}")
    st.progress(progress)

st.markdown("---")

quests = [
    {"name": "🏋️ Push-Ups (วิดพื้น)", "unit": "ครั้ง", "stat": "STR", "val": 0.2, "exp": 2},
    {"name": "🏃 Running (วิ่ง)", "unit": "กิโลเมตร", "stat": "AGI", "val": 5.0, "exp": 50},
    {"name": "📚 Reading (อ่านหนังสือ)", "unit": "หน้า", "stat": "INT", "val": 0.5, "exp": 5},
    {"name": "🧘 Meditation (นั่งสมาธิ)", "unit": "นาที", "stat": "MND", "val": 0.2, "exp": 2}
]

st.markdown("### 📋 [ รายการเควสประจำวัน ]")

for i, q in enumerate(quests):
    with st.container():
        st.markdown(f"<div class='quest-title'>{q['name']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='quest-caption'>เกณฑ์ฐาน: 1 {q['unit']} = +{q['val']} {q['stat']} | +{q['exp']} EXP</div>", unsafe_allow_html=True)
        
        col_in, col_bt = st.columns([1, 1])
        with col_in:
            count = st.number_input(f"ระบุจำนวนครั้ง ({q['unit']})", min_value=1, value=10, key=f"num_{i}")
        with col_bt:
            exp_gain = int(q['exp'] * count)
            st.write("") 
            if st.button(f"COMPLETE (+{exp_gain} XP)", key=f"btn_{i}"):
                add_reward(q['stat'], q['val'] * count, exp_gain)
                st.success("SYSTEM UPDATED & SAVED!")
                st.rerun()
    st.write("") 

with st.sidebar:
    st.markdown("## ⚙️ SYSTEM SETTINGS")
    st.write("ตัวเลือกการจัดการระบบ")
    
    st.markdown('<div class="reset-btn">', unsafe_allow_html=True)
    if st.button("🚨 RESET ALL LEVEL", key="reset_all"):
        st.session_state.level = 1
        st.session_state.exp = 0
        st.session_state.max_exp = 100
        save_data_to_system(1, 0)
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("---")
    st.caption("Solo Leveling Glass UI v3.2")

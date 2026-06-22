import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. การตั้งค่าธีมและสไตล์ (Glassmorphism & Neon)
st.set_page_config(page_title="Solo Leveling System", page_icon="⚔️", layout="centered")

# CSS สำหรับ UI โปร่งแสงและตัวหนังสือขนาดใหญ่
st.markdown("""
<style>
    /* พื้นหลังและโทนสีหลัก */
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    
    /* กรอบเควสแบบโปร่งแสง (Glassmorphism) */
    div[data-testid="stVerticalBlock"] > div.element-container {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 15px;
        border: 1px solid rgba(0, 242, 255, 0.2);
    }

    /* ปรับขนาดตัวหนังสือเควสให้ใหญ่ (Mobile Friendly) */
    .quest-title {
        font-size: 28px !important;
        font-weight: bold;
        color: #00f2ff;
        text-shadow: 0 0 10px rgba(0, 242, 255, 0.5);
        margin-bottom: 5px;
    }
    .quest-caption {
        font-size: 18px !important;
        color: #aaaaaa;
    }

    /* ปรับแต่งปุ่มกดให้ดูเหมือนปุ่มระบบ */
    .stButton > button {
        width: 100%;
        border-radius: 10px;
        border: 1px solid #00f2ff;
        background: rgba(0, 242, 255, 0.1);
        color: white;
        font-size: 20px !important;
        height: 55px;
        transition: 0.3s;
    }
    .stButton > button:hover {
        background: #00f2ff;
        color: black;
        box-shadow: 0 0 20px #00f2ff;
    }

    /* ปรับแต่งปุ่ม Reset ให้สีแดงเด่นชัด */
    .reset-btn button {
        background-color: rgba(255, 75, 75, 0.2) !important;
        border: 1px solid #ff4b4b !important;
        color: #ff4b4b !important;
        font-size: 16px !important;
        height: 45px !important;
    }

    /* ปรับระดับ Level ให้ใหญ่ */
    div[data-testid="stMetricValue"] {
        font-size: 60px !important;
        color: #00f2ff !important;
    }
</style>
""", unsafe_allow_html=True)

# 2. เชื่อมต่อ Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        df = conn.read(worksheet="save_state", ttl=0)
        return dict(zip(df['key'], df['value']))
    except:
        return {"level": 1, "exp": 0}

def save_data(level, exp):
    save_df = pd.DataFrame([{"key": "level", "value": int(level)}, {"key": "exp", "value": int(exp)}])
    conn.update(worksheet="save_state", data=save_df)

# 3. เริ่มต้นระบบ Logic
if 'level' not in st.session_state:
    data = load_data()
    st.session_state.level = int(data.get("level", 1))
    st.session_state.exp = int(data.get("exp", 0))
    st.session_state.max_exp = 100 * (1.5 ** (st.session_state.level - 1))
    st.session_state.stats = {"STR": 10, "VIT": 10, "AGI": 10, "INT": 10, "MND": 10}

def add_reward(stat_name, stat_val, exp_reward):
    st.session_state.exp += exp_reward
    while st.session_state.exp >= st.session_state.max_exp:
        st.session_state.exp -= st.session_state.max_exp
        st.session_state.level += 1
        st.session_state.max_exp *= 1.5
    save_data(st.session_state.level, st.session_state.exp)

# --- หน้าตา UI ---
st.markdown("<h1 style='text-align: center; color: #00f2ff;'>SYSTEM : SOLO LEVELING</h1>", unsafe_allow_html=True)

col1, col2 = st.columns([1, 1])
with col1:
    st.metric(label="PLAYER LEVEL", value=st.session_state.level)
with col2:
    progress = min(st.session_state.exp / st.session_state.max_exp, 1.0)
    st.write(f"### EXP: {int(st.session_state.exp)} / {int(st.session_state.max_exp)}")
    st.progress(progress)

st.markdown("---")

# รายการเควส
quests = [
    {"name": "🏋️ Push-Ups (วิดพื้น)", "unit": "ครั้ง", "stat": "STR", "val": 0.2, "exp": 2},
    {"name": "🏃 Running (วิ่ง)", "unit": "km", "stat": "AGI", "val": 5.0, "exp": 50},
    {"name": "📚 Reading (อ่านหนังสือ)", "unit": "หน้า", "stat": "INT", "val": 0.5, "exp": 5},
]

st.markdown("### [ Daily Quests ]")

for i, q in enumerate(quests):
    with st.container():
        # แสดงหัวข้อเควสขนาดใหญ่
        st.markdown(f"<div class='quest-title'>{q['name']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='quest-caption'>1 {q['unit']} = +{q['val']} {q['stat']} | +{q['exp']} EXP</div>", unsafe_allow_html=True)
        
        col_in, col_bt = st.columns([1, 1])
        with col_in:
            count = st.number_input(f"จำนวน", min_value=1, value=10, key=f"num_{i}")
        with col_bt:
            exp_gain = int(q['exp'] * count)
            st.write("") # เว้นระยะให้ปุ่มตรงกับช่องกรอก
            if st.button(f"COMPLETE (+{exp_gain} XP)", key=f"btn_{i}"):
                add_reward(q['stat'], q['val'] * count, exp_gain)
                st.success("SYNCING WITH SYSTEM...")
                st.rerun()
    st.write("") # ระยะห่างระหว่างเควส

# Sidebar สำหรับปุ่มรีเซ็ตที่หายไป
with st.sidebar:
    st.markdown("## SYSTEM SETTINGS")
    st.write("จัดการข้อมูลเลเวลของคุณ")
    
    # วางปุ่มรีเซ็ตเลเวลไว้ในคลาสพิเศษเพื่อให้สีแดง
    st.markdown('<div class="reset-btn">', unsafe_allow_html=True)
    if st.button("🚨 RESET LEVEL (เริ่มใหม่)", key="reset_all"):
        save_data(1, 0)
        st.session_state.clear()
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.caption("Solo Leveling System v2.0 - Glass Edition")

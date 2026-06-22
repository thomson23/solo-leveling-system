import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. ตั้งค่าหน้าจอและดีไซน์ (Glassmorphic & Neon Theme)
st.set_page_config(page_title="Solo Leveling System", page_icon="⚔️", layout="centered")

st.markdown("""
<style>
    /* พื้นหลังโทนดาร์ก */
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    
    /* กรอบเควสแบบโปร่งแสง (Transparent Glassmorphism) */
    div[data-testid="stVerticalBlock"] > div.element-container {
        background: rgba(255, 255, 255, 0.02);
        border-radius: 15px;
        border: 1px solid rgba(0, 242, 255, 0.15);
        padding: 5px;
    }

    /* ขยายฟอนต์เควสให้ใหญ่ อ่านง่ายบนโทรศัพท์ */
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

    /* ดีไซน์ปุ่มกดระบบ */
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

    /* ปุ่ม Reset ด้านข้าง ให้มีสีแดงเตือน */
    .reset-btn button {
        background-color: rgba(255, 75, 75, 0.1) !important;
        border: 1px solid #ff4b4b !important;
        color: #ff4b4b !important;
        font-size: 15px !important;
        height: 42px !important;
    }

    /* ค่าเลเวลขนาดใหญ่ */
    div[data-testid="stMetricValue"] {
        font-size: 55px !important;
        color: #00f2ff !important;
    }
</style>
""", unsafe_allow_html=True)

# 2. เปิดการเชื่อมต่อ Google Sheets ผ่าน st.connection ตรงๆ
conn = st.connection("gsheets", type=GSheetsConnection)

# ฟังก์ชันดึงค่าจาก Google Sheets
def load_data_from_sheets():
    try:
        df = conn.read(worksheet="save_state", ttl=0) # ttl=0 เพื่อให้อ่านค่าล่าสุดเสมอ
        data_dict = dict(zip(df['key'], df['value']))
        return data_dict
    except:
        return None

# ฟังก์ชันบันทึกค่ากลับไปยัง Google Sheets (รอบนี้ใส่โค้ดบันทึกของจริงแล้วครับ)
def save_data_to_sheets(level, exp):
    try:
        # เตรียมโครงสร้างตาราง DataFrame ให้เหมือนใน Google Sheets
        save_df = pd.DataFrame([
            {"key": "level", "value": int(level)},
            {"key": "exp", "value": int(exp)}
        ])
        # สั่งอัปเดตข้อมูลทับลงในชีตชื่อ save_state ทันที
        conn.update(worksheet="save_state", data=save_df)
    except Exception as e:
        st.error(f"ระบบบันทึกขัดข้อง: {e}")

# --- เริ่มการโหลดข้อมูลตอนเข้าแอป ---
if 'level' not in st.session_state:
    sheets_data = load_data_from_sheets()
    
    if sheets_data and 'level' in sheets_data:
        st.session_state.level = int(sheets_data['level'])
        st.session_state.exp = int(sheets_data['exp'])
    else:
        st.session_state.level = 1
        st.session_state.exp = 0
        
    st.session_state.max_exp = 100 * (1.5 ** (st.session_state.level - 1))
    st.session_state.stats = {"STR": 10, "VIT": 10, "AGI": 10, "INT": 10, "MND": 10}

def add_reward(stat_name, stat_val, exp_reward):
    st.session_state.exp += exp_reward
    while st.session_state.exp >= st.session_state.max_exp:
        st.session_state.exp -= st.session_state.max_exp
        st.session_state.level += 1
        st.session_state.max_exp *= 1.5
    
    # เรียกใช้ฟังก์ชันเซฟข้อมูลลง Google Sheets ทุกครั้งที่มีการส่งเควสสำเร็จ
    save_data_to_sheets(st.session_state.level, st.session_state.exp)

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

# รายการเควสประจำวัน
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
                st.success("SAVED TO GOOGLE SHEETS!")
                st.rerun()
    st.write("") 

# แถบด้านข้างพร้อมปุ่มรีเซ็ต
with st.sidebar:
    st.markdown("## ⚙️ SYSTEM SETTINGS")
    st.write("ตัวเลือกการจัดการระบบ")
    
    st.markdown('<div class="reset-btn">', unsafe_allow_html=True)
    if st.button("🚨 RESET ALL LEVEL", key="reset_all"):
        st.session_state.level = 1
        st.session_state.exp = 0
        st.session_state.max_exp = 100
        save_data_to_sheets(1, 0)
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("---")
    st.caption("Solo Leveling Glass UI v3.0")

import streamlit as st
import gspread
import pandas as pd

# ตั้งค่าหน้าจอแอป ให้ฟีล Dark Mode แบบระบบในเรื่อง
st.set_page_config(page_title="Solo Leveling System", page_icon="⚔️", layout="centered")

# ฟังก์ชันโหลดข้อมูลจาก Google Sheets (เข้าถึงแบบสาธารณะผ่านลิงก์แชร์)
@st.cache_data(ttl=0) # อัปเดตค่าใหม่ตลอด ไม่จำค่าเก่าค้าง
def load_data_from_sheets(sheet_url):
    try:
        # เปิดอ่านข้อมูลจากลิงก์โดยตรง
        gc = gspread.oauth() # เปิดใช้งานเบื้องต้น
    except:
        # หากยังไม่ได้ตั้งค่าเซฟแบบยืนยันตัวตน ให้ใช้วิธีอ่านค่าผ่านตารางเปิดสาธารณะแทน
        try:
            csv_url = sheet_url.replace('/edit?usp=sharing', '/gviz/tq?tqx=out:csv&sheet=save_state')
            df = pd.read_csv(csv_url)
            data_dict = dict(zip(df['key'], df['value']))
            return data_dict
        except:
            return None

# ดึงลิงก์แชร์จาก secrets.toml
try:
    SHEET_URL = st.secrets["connections"]["gsheets"]["spreadsheet"]
except:
    SHEET_URL = ""

# --- โหลดเซฟเมื่อเปิดแอปครั้งแรก ---
if 'level' not in st.session_state:
    sheets_data = load_data_from_sheets(SHEET_URL)
    
    if sheets_data and 'level' in sheets_data:
        st.session_state.level = int(sheets_data['level'])
        st.session_state.exp = int(sheets_data['exp'])
    else:
        st.session_state.level = 1
        st.session_state.exp = 0
        
    st.session_state.max_exp = 100
    st.session_state.stats = {"STR": 10, "VIT": 10, "AGI": 10, "INT": 10, "MND": 10}
    st.session_state.history = []

# ฟังก์ชันคำนวณแต้มเมื่อส่งเควส
def add_reward(stat_name, final_stat_val, final_exp_reward, activity_name, count, unit):
    st.session_state.exp += final_exp_reward
    st.session_state.stats[stat_name] += final_stat_val
    st.session_state.stats[stat_name] = round(st.session_state.stats[stat_name], 1)
    
    # ระบบ Level Up
    leveled_up = False
    while st.session_state.exp >= st.session_state.max_exp:
        st.session_state.exp -= st.session_state.max_exp
        st.session_state.level += 1
        leveled_up = True
        
    st.session_state.history.append(
        f"สำเร็จเควส: {activity_name} {count} {unit} (+{final_exp_reward} EXP)"
    )
    return leveled_up

# --- หน้าตา UI ของแอป ---
st.title("🚨 โหมดผู้ปลุกพลัง (Awakened System)")
st.subheader("ผู้เล่น: สอง (เซฟข้อมูลออนไลน์ผ่าน Google Sheets)")
st.markdown("---")

col1, col2 = st.columns([1, 2])
with col1:
    st.metric(label="LEVEL", value=st.session_state.level)
    progress = min(st.session_state.exp / st.session_state.max_exp, 1.0)
    st.progress(progress)
    st.caption(f"EXP: {int(st.session_state.exp)} / {st.session_state.max_exp}")

with col2:
    st.markdown("### **[ สเตตัสของคุณ ]**")
    for stat, val in st.session_state.stats.items():
        st.text(f"🔹 {stat} : {val}")

st.markdown("---")
st.markdown("### 📋 เควสประจำวัน")

quests = [
    {"name": "🏋️ วิดพื้น", "unit": "ครั้ง", "stat": "STR", "stat_val": 0.2, "exp": 1.5},
    {"name": "🏃 วิ่ง", "unit": "กิโลเมตร", "stat": "AGI", "stat_val": 2.0, "exp": 30.0},
    {"name": "📚 อ่านหนังสือ", "unit": "หน้า", "stat": "INT", "stat_val": 0.2, "exp": 4.0},
    {"name": "🧘 นั่งสมาธิ", "unit": "นาที", "stat": "MND", "stat_val": 0.2, "exp": 1.5}
]

for index, quest in enumerate(quests):
    with st.container():
        col_name, col_input, col_btn = st.columns([2, 1, 1])
        with col_name:
            st.markdown(f"**{quest['name']}**")
            st.caption(f"1 {quest['unit']} = +{quest['stat_val']} {quest['stat']} | +{quest['exp']} EXP")
        with col_input:
            count = st.number_input(f"จำนวน ({quest['unit']})", min_value=1, value=10, key=f"in_{index}", label_visibility="collapsed")
        with col_btn:
            calculated_stat = round(quest['stat_val'] * count, 1)
            calculated_exp = int(quest['exp'] * count)
            if st.button(f"ส่งเควส (+{calculated_exp} XP)", key=f"btn_{index}", use_container_width=True):
                lv_up = add_reward(quest['stat'], calculated_stat, calculated_exp, quest['name'], count, quest['unit'])
                st.success("อัปเดตข้อมูลสำเร็จ!")
                if lv_up: st.balloons()
                st.rerun()
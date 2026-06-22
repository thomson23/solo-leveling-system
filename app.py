import streamlit as st
import requests

# ตั้งค่าหน้าจอ
st.set_page_config(page_title="Solo Leveling System", page_icon="⚔️", layout="centered")

# [สไตล์ CSS ของเดิมของคุณหมั่น ให้ใส่ไว้ที่นี่เหมือนเดิมครับ]
st.markdown("""
<style>
    .stApp { background-color: #060810; color: #ffffff; }
    div[data-testid="stMainBlockContainer"] { background: rgba(10, 16, 32, 0.85); border: 2px solid #00f2ff; border-radius: 12px; padding: 30px; }
    .system-title { font-size: 32px !important; font-weight: 800; color: #ffffff; text-align: center; }
</style>
""", unsafe_allow_html=True)

# ดึง URL จาก Secrets
API_URL = st.secrets["connections"]["gsheets"]["spreadsheet"]

# --- ฟังก์ชันจัดการข้อมูล ---
def load_player_data(player_name):
    try:
        res = requests.get(f"{API_URL}?action=get&player={player_name}")
        return res.json()
    except:
        return {"level": 1, "exp": 0}

def save_player_data(player_name, level, exp):
    requests.get(f"{API_URL}?action=set&player={player_name}&level={int(level)}&exp={int(exp)}")

# --- โหลดรายชื่อปาร์ตี้ ---
if 'players' not in st.session_state:
    st.session_state.players = ["หมั่น", "บีม", "ผู้เล่น 3", "ผู้เล่น 4", "ผู้เล่น 5", "ผู้เล่น 6", "ผู้เล่น 7", "ผู้เล่น 8"]

# --- แถบข้าง (Sidebar) ---
with st.sidebar:
    st.markdown("### 👥 PARTY SETTINGS")
    current_player = st.selectbox("เลือกผู้เล่น", st.session_state.players)
    
    # ปุ่มเปลี่ยนชื่อผู้เล่น
    with st.expander("📝 เปลี่ยนชื่อสมาชิก"):
        with st.form("rename_form"):
            new_name = st.text_input("ชื่อใหม่สำหรับ " + current_player)
            if st.form_submit_button("ยืนยันการเปลี่ยนชื่อ"):
                idx = st.session_state.players.index(current_player)
                st.session_state.players[idx] = new_name
                st.rerun()

# --- ซิงค์ข้อมูลผู้เล่นที่เลือก ---
if 'current_active' != current_player:
    st.session_state.current_active = current_player
    data = load_player_data(current_player)
    st.session_state.level = int(data.get('level', 1))
    st.session_state.exp = int(data.get('exp', 0))

# คำนวณ EXP ที่ต้องใช้
st.session_state.max_exp = 100 * (1.5 ** (st.session_state.level - 1))

# --- แสดงผลหน้าหลัก ---
st.markdown(f"<h3 style='color: #00f2ff;'>👤 {current_player} (LVL: {st.session_state.level})</h3>", unsafe_allow_html=True)

# แถบแสดง EXP
progress = min(st.session_state.exp / st.session_state.max_exp, 1.0)
st.progress(progress)
st.markdown(f"**EXP:** {int(st.session_state.exp)} / {int(st.session_state.max_exp)} (ขาดอีก {int(st.session_state.max_exp - st.session_state.exp)} จะเลเวลอัป!)")

# ปุ่มเควส (เหมือนเดิม)
# ... [ใส่โค้ดแสดงรายการเควสของคุณไว้ตรงนี้] ...

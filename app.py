import streamlit as st
import requests

# ตั้งค่าหน้าจอ
st.set_page_config(page_title="Solo Leveling System", page_icon="⚔️", layout="centered")

# --- CSS Design ---
st.markdown("""
<style>
    .stApp { background-color: #060810; color: #ffffff; }
    div[data-testid="stMainBlockContainer"] { background: rgba(10, 16, 32, 0.85); border: 2px solid #00f2ff; border-radius: 12px; padding: 30px; }
    .system-title { font-size: 32px !important; font-weight: 800; color: #ffffff; text-align: center; }
</style>
""", unsafe_allow_html=True)

API_URL = st.secrets["connections"]["gsheets"]["spreadsheet"]

# --- ฟังก์ชันข้อมูลผู้เล่น ---
def load_player_data(player_name):
    try:
        res = requests.get(f"{API_URL}?action=get&player={player_name}")
        return res.json()
    except:
        return {"level": 1, "exp": 0}

def save_player_data(player_name, level, exp):
    requests.get(f"{API_URL}?action=set&player={player_name}&level={int(level)}&exp={int(exp)}")

# --- ฟังก์ชันข้อมูลเควส ---
def load_quests():
    try:
        res = requests.get(f"{API_URL}?action=get_quests")
        return res.json() if res.status_code == 200 else []
    except:
        return []

# --- ระบบปาร์ตี้ ---
if 'players' not in st.session_state:
    st.session_state.players = ["หมั่น", "บีม", "ผู้เล่น 3", "ผู้เล่น 4", "ผู้เล่น 5", "ผู้เล่น 6", "ผู้เล่น 7", "ผู้เล่น 8"]

with st.sidebar:
    st.markdown("### 👥 PARTY SETTINGS")
    current_player = st.selectbox("เลือกผู้เล่น", st.session_state.players)
    
    with st.expander("📝 เปลี่ยนชื่อสมาชิก"):
        with st.form("rename_form"):
            new_name = st.text_input("ชื่อใหม่สำหรับ " + current_player)
            if st.form_submit_button("ยืนยัน"):
                idx = st.session_state.players.index(current_player)
                st.session_state.players[idx] = new_name
                st.rerun()

    st.markdown("---")
    st.markdown("### ➕ ADD CUSTOM QUEST")
    with st.form("add_quest_form", clear_on_submit=True):
        new_name = st.text_input("ชื่อเควส")
        new_exp = st.number_input("EXP ต่อหน่วย", min_value=1, value=10)
        new_unit = st.text_input("หน่วย (เช่น ครั้ง, นาที)", value="ครั้ง")
        
        if st.form_submit_button("บันทึกเควสใหม่"):
            if new_name:
                try:
                    requests.get(f"{API_URL}?action=add_quest&name={new_name}&exp={new_exp}&unit={new_unit}")
                    st.toast("เพิ่มเควสเรียบร้อยแล้ว!")
                    st.rerun() 
                except:
                    st.error("เกิดข้อผิดพลาดในการเชื่อมต่อ")
            else:
                st.warning("กรุณากรอกชื่อเควส")

# --- ซิงค์ข้อมูล ---
if 'current_active' not in st.session_state or st.session_state.current_active != current_player:
    st.session_state.current_active = current_player
    data = load_player_data(current_player)
    st.session_state.level = int(data.get('level', 1))
    st.session_state.exp = int(data.get('exp', 0))

st.session_state.max_exp = 100 * (1.5 ** (st.session_state.level - 1))

# --- หน้าจอหลัก ---
st.markdown(f"<h3 style='color: #00f2ff;'>👤 {current_player} (LVL: {st.session_state.level})</h3>", unsafe_allow_html=True)

# แถบ EXP
progress = min(st.session_state.exp / st.session_state.max_exp, 1.0)
st.progress(progress)
st.markdown(f"**EXP:** {int(st.session_state.exp)} / {int(st.session_state.max_exp)} (ขาดอีก {int(st.session_state.max_exp - st.session_state.exp)} จะเลเวลอัป!)")

# --- ส่วนแสดงรายการเควส (ที่ปรับปรุงการจัดตำแหน่ง) ---
st.markdown("### 📜 DAILY TASKS")
quests = load_quests()

if quests:
    for i, q in enumerate(quests):
        # ใช้ vertical_alignment="center" เพื่อให้ชื่อเควสและปุ่มอยู่แนวเดียวกัน
        col1, col2, col3 = st.columns([5, 2, 2], vertical_alignment="center")
        
        with col1:
            st.write(f"**{q['name']}** (+{q['exp_per_unit']} EXP)")
        
        with col2:
            count = st.number_input(f" ", min_value=0, key=f"input_{i}", label_visibility="collapsed")
            
        with col3:
            if st.button("COMPLETE", key=f"btn_{i}"):
                if count > 0:
                    gained = count * int(q['exp_per_unit'])
                    st.session_state.exp += gained
                    
                    # ตรรกะเลเวลอัปแบบต่อเนื่อง
                    while st.session_state.exp >= st.session_state.max_exp:
                        st.session_state.exp -= st.session_state.max_exp
                        st.session_state.level += 1
                        st.session_state.max_exp = 100 * (1.5 ** (st.session_state.level - 1))
                    
                    save_player_data(current_player, st.session_state.level, st.session_state.exp)
                    st.toast(f"ได้รับ {gained} EXP! 🔥")
                    st.rerun()
else:
    st.info("ไม่พบเควสในระบบ หรือกำลังโหลดข้อมูล...")

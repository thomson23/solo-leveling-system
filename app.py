import streamlit as st
import requests

# ตั้งค่าหน้าจอธีมระบบ
st.set_page_config(page_title="Solo Leveling System", page_icon="⚔️", layout="centered")

# --- โค้ดปรับแต่งดีไซน์ ---
st.markdown("""
<style>
    .stApp { background-color: #060810; color: #ffffff; font-family: 'Inter', sans-serif; }
    div[data-testid="stMainBlockContainer"] { background: rgba(10, 16, 32, 0.85); border: 2px solid #00f2ff; border-radius: 12px; padding: 30px !important; box-shadow: 0 0 25px rgba(0, 242, 255, 0.25); margin-top: 20px; }
    .system-title { font-size: 32px !important; font-weight: 800; color: #ffffff; letter-spacing: 2px; text-align: center; margin-bottom: 5px; }
    .system-subtitle { font-size: 14px !important; color: #8da4be; text-align: center; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 25px; }
    .info-header { font-size: 16px !important; color: #00f2ff; text-align: center; border-bottom: 1px solid rgba(0, 242, 255, 0.3); padding-bottom: 8px; margin-bottom: 20px; text-transform: uppercase; }
    .penalty-warning { background: rgba(255, 59, 48, 0.08); border: 1px solid #ff3b30; border-radius: 6px; padding: 12px; font-size: 12px !important; color: #ff453a; text-align: center; font-weight: bold; margin-top: 35px; }
    .stButton > button { width: 100%; border-radius: 6px; border: 1px solid #00f2ff; background: rgba(0, 242, 255, 0.05); color: #00f2ff; font-weight: bold; height: 38px; margin-top: 28px; }
    .stButton > button:hover { background: #00f2ff; color: #000000; }
</style>
""", unsafe_allow_html=True)

# ดึงลิงก์เชื่อมโยง
try:
    API_URL = st.secrets["connections"]["gsheets"]["spreadsheet"]
except:
    API_URL = ""

# --- ฟังก์ชันจัดการข้อมูล ---
def load_player_data(player_name):
    try:
        response = requests.get(f"{API_URL}?action=get&player={player_name}")
        return response.json() if response.status_code == 200 else {"level": 1, "exp": 0}
    except: return {"level": 1, "exp": 0}

def save_player_data(player_name, level, exp):
    requests.get(f"{API_URL}?action=set&player={player_name}&level={int(level)}&exp={int(exp)}")

def load_quests():
    try:
        response = requests.get(f"{API_URL}?action=get_quests")
        return response.json() if response.status_code == 200 else []
    except: return []

def add_quest_to_sheet(name, exp, unit):
    requests.get(f"{API_URL}?action=add_quest&name={name}&exp={exp}&unit={unit}")

# --- Initialize State ---
if 'players' not in st.session_state:
    st.session_state.players = ["หมั่น", "บีม", "ผู้เล่น 3", "ผู้เล่น 4", "ผู้เล่น 5", "ผู้เล่น 6", "ผู้เล่น 7", "ผู้เล่น 8"]

# โหลดเควสจาก DB
db_quests = load_quests()
st.session_state.quests = db_quests if db_quests else [
    {"name": "🏋️ PUSH-UPS", "exp": 2, "unit": "ครั้ง"},
    {"name": "🏃 OUTDOOR RUN", "exp": 50, "unit": "KM"}
]

# --- Sidebar ---
with st.sidebar:
    st.markdown("### 👥 PARTY SYSTEM")
    current_player = st.selectbox("SELECT ACTIVE PLAYER", st.session_state.players)
    
    st.markdown("### ➕ ADD CUSTOM QUEST")
    with st.form("add_quest_form", clear_on_submit=True):
        new_quest_name = st.text_input("ชื่อเควส")
        new_quest_exp = st.number_input("EXP ต่อหน่วย", min_value=1, value=5)
        new_quest_unit = st.text_input("หน่วย", value="ครั้ง")
        if st.form_submit_button("ADD TO SYSTEM"):
            add_quest_to_sheet(new_quest_name.upper(), new_quest_exp, new_quest_unit)
            st.rerun()

# --- Logic ---
if 'current_active' not in st.session_state or st.session_state.current_active != current_player:
    st.session_state.current_active = current_player
    saved = load_player_data(current_player)
    st.session_state.level = int(saved.get('level', 1))
    st.session_state.exp = int(saved.get('exp', 0))
    st.session_state.max_exp = 100 * (1.5 ** (st.session_state.level - 1))

# --- หน้าจอหลัก ---
st.markdown(f"<h3 style='color: #00f2ff;'>👤 {st.session_state.current_active} | LVL : {st.session_state.level}</h3>", unsafe_allow_html=True)
st.progress(min(st.session_state.exp / st.session_state.max_exp, 1.0))

st.markdown('<div class="system-title">DAILY TASKS</div>', unsafe_allow_html=True)

for i, q in enumerate(st.session_state.quests):
    c1, c2, c3 = st.columns([2, 1, 1])
    with c1: st.write(f"**{q['name']}** (+{q['exp']} XP/{q['unit']})")
    with c2: count = st.number_input("จำนวน", min_value=0, key=f"inp_{i}")
    with c3:
        if st.button("COMPLETE", key=f"btn_{i}"):
            st.session_state.exp += (count * q['exp'])
            save_player_data(st.session_state.current_active, st.session_state.level, st.session_state.exp)
            st.rerun()

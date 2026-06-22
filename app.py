import streamlit as st
import requests

# ตั้งค่าหน้าจอธีมระบบ
st.set_page_config(page_title="Solo Leveling System", page_icon="⚔️", layout="centered")

# --- โค้ดปรับแต่งดีไซน์ระดับมหากาพย์ (Solo Leveling System Style) ---
st.markdown("""
<style>
    /* พื้นหลังแอปสีดำสนิทแนวสมาร์ทโฟนของระบบ */
    .stApp {
        background-color: #060810;
        color: #ffffff;
        font-family: 'Inter', sans-serif;
    }
    
    /* กล่องหน้าต่างเควสเรืองแสง (Quest Info Box) */
    .system-quest-container {
        background: rgba(10, 16, 32, 0.85);
        border: 2px solid #00f2ff;
        border-radius: 12px;
        padding: 25px;
        box-shadow: 0 0 25px rgba(0, 242, 255, 0.25);
        margin-bottom: 20px;
    }
    
    /* หัวข้อ DAILY TASKS */
    .system-title {
        font-size: 32px !important;
        font-weight: 800;
        color: #ffffff;
        letter-spacing: 2px;
        text-align: center;
        margin-bottom: 5px;
    }
    
    /* ซับไตเติล */
    .system-subtitle {
        font-size: 14px !important;
        color: #8da4be;
        text-align: center;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 25px;
    }
    
    /* หัวข้อย่อยตรงกลางกล่อง */
    .info-header {
        font-size: 16px !important;
        color: #00f2ff;
        text-align: center;
        border-bottom: 1px solid rgba(0, 242, 255, 0.3);
        padding-bottom: 8px;
        margin-bottom: 20px;
        text-transform: uppercase;
    }
    
    /* ข้อความเตือนบทลงโทษ (ความดันโลหิตพุ่ง!) */
    .penalty-warning {
        background: rgba(255, 59, 48, 0.08);
        border: 1px solid #ff3b30;
        border-radius: 6px;
        padding: 12px;
        font-size: 12px !important;
        color: #ff453a;
        text-align: center;
        font-weight: bold;
        text-shadow: 0 0 8px rgba(255, 59, 48, 0.4);
        margin-top: 15px;
    }
    
    /* สไตล์ปุ่มกด Complete เควส */
    .stButton > button {
        width: 100%;
        border-radius: 6px;
        border: 1px solid #00f2ff;
        background: rgba(0, 242, 255, 0.05);
        color: #00f2ff;
        font-weight: bold;
        height: 40px;
        transition: 0.2s;
    }
    .stButton > button:hover {
        background: #00f2ff;
        color: #000000;
        box-shadow: 0 0 15px #00f2ff;
    }
    
    /* ซ่อนขอบกล่องเดิมของ streamlit บางส่วนเพื่อให้ดูกลืนกัน */
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.02);
        padding: 10px;
        border-radius: 8px;
        border: 1px solid rgba(255,255,255,0.05);
    }
</style>
""", unsafe_allow_html=True)

# ดึงลิงก์เชื่อมโยงตัวใหม่จากระบบ Secrets
try:
    API_URL = st.secrets["connections"]["gsheets"]["spreadsheet"]
except:
    API_URL = ""

# ฟังก์ชันโหลดข้อมูลแยกตามผู้เล่น
def load_player_data(player_name):
    if not API_URL:
        return {"level": 1, "exp": 0}
    try:
        response = requests.get(f"{API_URL}?action=get&player={player_name}")
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return {"level": 1, "exp": 0}

# ฟังก์ชันเซฟข้อมูลแยกตามผู้เล่น
def save_player_data(player_name, level, exp):
    if not API_URL:
        return
    try:
        requests.get(f"{API_URL}?action=set&player={player_name}&level={int(level)}&exp={int(exp)}")
    except:
        pass

# --- แถบข้างสำหรับระบบปาร์ตี้ (สลับผู้เล่น 2 คนได้ที่นี่) ---
with st.sidebar:
    st.markdown("### 👥 PARTY SYSTEM")
    current_player = st.selectbox(
        "SELECT ACTIVE PLAYER",
        ["Sung Jin-Woo (คุณสอง)", "Cha Hae-In (ผู้เล่นคนที่ 2)"]
    )
    st.caption("ระบบจะสลับและบันทึกข้อมูลแยกโปรไฟล์อัตโนมัติ")
    st.markdown("---")

# ซิงค์ข้อมูลผู้เล่นที่เลือกเข้าสู่ Session State
if 'current_active' not in st.session_state or st.session_state.current_active != current_player:
    st.session_state.current_active = current_player
    saved = load_player_data(current_player)
    st.session_state.level = int(saved.get('level', 1))
    st.session_state.exp = int(saved.get('exp', 0))
    st.session_state.max_exp = 100 * (1.5 ** (st.session_state.level - 1))

def add_reward(exp_reward):
    st.session_state.exp += exp_reward
    while st.session_state.exp >= st.session_state.max_exp:
        st.session_state.exp -= st.session_state.max_exp
        st.session_state.level += 1
        st.session_state.max_exp *= 1.5
    save_player_data(st.session_state.current_active, st.session_state.level, st.session_state.exp)

# --- ส่วนแสดงผลบนหน้าจอแอปตามโมเดลรูปภาพ ---
# 1. ด้านบนสุด: ข้อมูลเลเวลผู้เล่นปัจจุบัน และแถบสถานะหลอด EXP
col_name, col_lvl = st.columns([2, 1])
with col_name:
    st.markdown(f"<h3 style='color: #00f2ff; margin:0;'>👤 {st.session_state.current_active}</h3>", unsafe_allow_html=True)
with col_lvl:
    st.markdown(f"<h3 style='text-align: right; color: #ffaa00; margin:0;'>LVL : {st.session_state.level}</h3>", unsafe_allow_html=True)

progress_ratio = min(st.session_state.exp / st.session_state.max_exp, 1.0)
st.progress(progress_ratio)
st.markdown(f"<p style='text-align: right; font-size:12px; color:#8da4be; margin-top:-10px;'>EXP: {int(st.session_state.exp)} / {int(st.session_state.max_exp)}</p>", unsafe_allow_html=True)

# 2. ตัวโครงกล่องเควสเรืองแสงหลัก (DAILY TASKS WINDOW)
st.markdown('<div class="system-quest-container">', unsafe_allow_html=True)
st.markdown('<div class="system-title">DAILY TASKS</div>', unsafe_allow_html=True)
st.markdown('<div class="system-subtitle">CHALLENGE YOUR LIMITS TO GROW</div>', unsafe_allow_html=True)
st.markdown('<div class="info-header">ℹ️ QUEST INFO</div>', unsafe_allow_html=True)

# รายการเควส
quests = [
    {"name": "🏋️ 12 PUSH-UPS", "exp": 15},
    {"name": "🏃 2 KM OUTDOOR RUN", "exp": 50},
    {"name": "📚 10 PAGES READING", "exp": 20},
    {"name": "🧘 15 MIN MEDITATION", "exp": 15}
]

for i, q in enumerate(quests):
    col_q_text, col_q_btn = st.columns([2, 1])
    with col_q_text:
        # แสดงรายการเควสสไตล์เรียบๆ แบบกล่องระบบเกมส์
        st.markdown(f"<p style='font-size:16px; font-weight:bold; margin-top:8px;'>{q['name']} <span style='color:#00f2ff; font-size:12px;'>[+{q['exp']} XP]</span></p>", unsafe_allow_html=True)
    with col_q_btn:
        if st.button("COMPLETE", key=f"q_{i}"):
            add_reward(q['exp'])
            st.toast(f"Quest Complete! ได้รับ {q['exp']} EXP")
            st.rerun()

# 3. ข้อความแจ้งเตือนบทลงโทษใต้กล่องเควสเป๊ะๆ ตามในภาพ
st.markdown("""
<div class="penalty-warning">
    ⚠️ WARNING: FAILURE TO COMPLETE THE DAILY QUEST WILL RESULT IN AN APPROPRIATE PENALTY.
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True) # ปิดกล่องใหญ่

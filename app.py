import streamlit as st
import requests

# ตั้งค่าหน้าจอธีมระบบ
st.set_page_config(page_title="Solo Leveling System", page_icon="⚔️", layout="centered")

# --- โค้ดปรับแต่งดีไซน์ (Solo Leveling System Style) ---
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
    
    /* ข้อความเตือนบทลงโทษ */
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
        margin-top: 25px;
    }
    
    /* สไตล์ปุ่มกด Complete เควส */
    .stButton > button {
        width: 100%;
        border-radius: 6px;
        border: 1px solid #00f2ff;
        background: rgba(0, 242, 255, 0.05);
        color: #00f2ff;
        font-weight: bold;
        height: 38px;
        margin-top: 28px;
        transition: 0.2s;
    }
    .stButton > button:hover {
        background: #00f2ff;
        color: #000000;
        box-shadow: 0 0 15px #00f2ff;
    }
    
    /* ตกแต่งสไตล์ของช่องกรอกตัวเลข */
    div[data-testid="stNumberInput"] label {
        color: #8da4be !important;
        font-size: 12px !important;
    }
</style>
""", unsafe_allow_html=True)

# ดึงลิงก์เชื่อมโยงจากระบบ Secrets
try:
    API_URL = st.secrets["connections"]["gsheets"]["spreadsheet"]
except:
    API_URL = ""

# ฟังก์ชันโหลดข้อมูลผู้เล่น
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

# ฟังก์ชันเซฟข้อมูลผู้เล่น
def save_player_data(player_name, level, exp):
    if not API_URL:
        return
    try:
        requests.get(f"{API_URL}?action=set&player={player_name}&level={int(level)}&exp={int(exp)}")
    except:
        pass

# --- ระบบคลังเควส (Default Quests) ---
if 'quests' not in st.session_state:
    st.session_state.quests = [
        {"name": "🏋️ PUSH-UPS", "exp_per_unit": 2, "unit": "ครั้ง"},
        {"name": "🏃 OUTDOOR RUN", "exp_per_unit": 50, "unit": "KM"},
        {"name": "📚 READING", "exp_per_unit": 5, "unit": "หน้า"},
        {"name": "🧘 MEDITATION", "exp_per_unit": 2, "unit": "นาที"}
    ]

# --- แถบสไลด์บาร์ด้านข้าง (Party System & Quest Creator) ---
with st.sidebar:
    st.markdown("### 👥 PARTY SYSTEM")
    current_player = st.selectbox(
        "SELECT ACTIVE PLAYER",
        ["Sung Jin-Woo (คุณสอง)", "Cha Hae-In (ผู้เล่นคนที่ 2)"]
    )
    st.caption("ระบบจะสลับและบันทึกข้อมูลแยกโปรไฟล์อัตโนมัติ")
    st.markdown("---")
    
    # ฟีเจอร์เพิ่มเควสเองได้ตามต้องการ สั่งเพิ่ม EXP ต่อหน่วยได้เอง
    st.markdown("### ➕ ADD CUSTOM QUEST")
    with st.form("add_quest_form", clear_on_submit=True):
        new_quest_name = st.text_input("ชื่อเควส (เช่น 🥤 ดื่มน้ำ, ⌨️ เขียนโค้ด)")
        new_quest_exp = st.number_input("EXP ที่จะได้รับ ต่อ 1 หน่วย", min_value=1, value=5, step=1)
        new_quest_unit = st.text_input("หน่วยของกิจกรรม (เช่น ครั้ง, หน้า, แก้ว, นาที)", value="ครั้ง")
        submit_btn = st.form_submit_button("ADD TO SYSTEM WINDOW")
        
        if submit_btn and new_quest_name:
            st.session_state.quests.append({
                "name": new_quest_name.upper(),
                "exp_per_unit": int(new_quest_exp),
                "unit": new_quest_unit
            })
            st.toast(f"เพิ่มเควส {new_quest_name} เข้าสู่ระบบสำเร็จ!", icon="⚡")

# ซิงค์ข้อมูลผู้เล่นที่เลือกเข้าสู่ Session State
if 'current_active' not in st.session_state or st.session_state.current_active != current_player:
    st.session_state.current_active = current_player
    saved = load_player_data(current_player)
    st.session_state.level = int(saved.get('level', 1))
    st.session_state.exp = int(saved.get('exp', 0))
    st.session_state.max_exp = 100 * (1.5 ** (st.session_state.level - 1))

# ฟังก์ชันคำนวณและเพิ่ม EXP หลังทำเควสเสร็จ
def add_reward(exp_reward):
    st.session_state.exp += exp_reward
    while st.session_state.exp >= st.session_state.max_exp:
        st.session_state.exp -= st.session_state.max_exp
        st.session_state.level += 1
        st.session_state.max_exp *= 1.5
    save_player_data(st.session_state.current_active, st.session_state.level, st.session_state.exp)

# --- ส่วนแสดงผลหน้าจอแอปหลัก ---
# ด้านบนสุด: หลอดเลเวลและค่า EXP ปัจจุบัน ของผู้เล่นที่เลือก
col_name, col_lvl = st.columns([2, 1])
with col_name:
    st.markdown(f"<h3 style='color: #00f2ff; margin:0;'>👤 {st.session_state.current_active}</h3>", unsafe_allow_html=True)
with col_lvl:
    st.markdown(f"<h3 style='text-align: right; color: #ffaa00; margin:0;'>LVL : {st.session_state.level}</h3>", unsafe_allow_html=True)

progress_ratio = min(st.session_state.exp / st.session_state.max_exp, 1.0)
st.progress(progress_ratio)
st.markdown(f"<p style='text-align: right; font-size:12px; color:#8da4be; margin-top:-10px;'>EXP: {int(st.session_state.exp)} / {int(st.session_state.max_exp)}</p>", unsafe_allow_html=True)

# โครงสร้างกล่องหน้าต่างเควสระบบ (DAILY TASKS WINDOW)
st.markdown('<div class="system-quest-container">', unsafe_allow_html=True)
st.markdown('<div class="system-title">DAILY TASKS</div>', unsafe_allow_html=True)
st.markdown('<div class="system-subtitle">CHALLENGE YOUR LIMITS TO GROW</div>', unsafe_allow_html=True)
st.markdown('<div class="info-header">ℹ️ QUEST INFO (MULTIPLIER SYSTEM)</div>', unsafe_allow_html=True)

# ลูปแสดงรายการเควสทั้งหมด (ทั้งเควสเริ่มต้น และเควสที่คุณสองเพิ่มเข้าไปเอง)
for i, q in enumerate(st.session_state.quests):
    col_q_text, col_q_input, col_q_btn = st.columns([2.2, 1.3, 1.2])
    
    with col_q_text:
        # แสดงชื่อเควส และบอกเรทการคำนวณ EXP ให้ผู้เล่นรู้ชัดเจน
        st.markdown(f"""
        <div style='margin-top: 25px;'>
            <p style='font-size:16px; font-weight:bold; margin-bottom:2px;'>{q['name']}</p>
            <p style='color:#00f2ff; font-size:12px; margin:0;'>+{q['exp_per_unit']} XP / {q['unit']}</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col_q_input:
        # ช่องให้กรอกจำนวนครั้ง/จำนวนหน่วย ได้เองอิสระตามใจชอบ
        count = st.number_input(f"จำนวน ({q['unit']})", min_value=0, value=0, step=1, key=f"input_{i}")
        
    with col_q_btn:
        # ปุ่มกดส่งเพื่อคำนวณ EXP สุทธิ
        if st.button("RECORD", key=f"btn_{i}"):
            if count > 0:
                gained_exp = count * q['exp_per_unit']
                add_reward(gained_exp)
                st.toast(f"บันทึกสำเร็จ! ทำไป {count} {q['unit']} ได้รับ {gained_exp} EXP 🔥")
                st.rerun()
            else:
                st.toast("กรุณาใส่จำนวนก่อนกดบันทึกด้วยครับ!", icon="⚠️")

# ข้อความแจ้งเตือนบทลงโทษท้ายหน้าต่างเควสตามต้นฉบับอนิเมะ
st.markdown("""
<div class="penalty-warning">
    ⚠️ WARNING: FAILURE TO COMPLETE THE DAILY QUEST WILL RESULT IN AN APPROPRIATE PENALTY.
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True) # ปิดกล่องหน้าต่างเควส

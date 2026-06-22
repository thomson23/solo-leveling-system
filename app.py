import streamlit as st
import requests

# ตั้งค่าหน้าจอธีมระบบ
st.set_page_config(page_title="Solo Leveling System", page_icon="⚔️", layout="centered")

# --- โค้ดปรับแต่งดีไซน์ (Bulletproof Solo Leveling Style) ---
st.markdown("""
<style>
    /* พื้นหลังแอปสีดำสนิทแนวสมาร์ทโฟนของระบบ */
    .stApp {
        background-color: #060810;
        color: #ffffff;
        font-family: 'Inter', sans-serif;
    }
    
    /* ปรับแต่ง Main Container หลักให้กลายเป็นหน้าต่างเควสเรืองแสงโดยตรง */
    div[data-testid="stMainBlockContainer"] {
        background: rgba(10, 16, 32, 0.85);
        border: 2px solid #00f2ff;
        border-radius: 12px;
        padding: 30px !important;
        box-shadow: 0 0 25px rgba(0, 242, 255, 0.25);
        margin-top: 20px;
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
        margin-top: 35px;
    }
    
    /* สไตล์ปุ่มกด Complete เควส */
    .stButton > button {
        width: 100%;
        border

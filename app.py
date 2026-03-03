import streamlit as st
import pandas as pd
from datetime import datetime
import os

# ==========================================
# STEP 1: 画面の基本設定とデザイン (UI/UX)
# ==========================================
st.set_page_config(page_title="VICTO-LOG", layout="wide")

st.markdown("""
    <style>
    header {visibility: hidden;}
    footer {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    /* 背景のグリッド模様 */
    .stApp::after {
        content: "";
        position: absolute;
        top: 0; left: 0; width: 100%; height: 100%;
        background-image: linear-gradient(rgba(0, 255, 204, 0.05) 1px, transparent 1px),
                          linear-gradient(90deg, rgba(0, 255, 204, 0.05) 1px, transparent 1px);
        background-size: 30px 30px;
        z-index: -1;
    }
    /* 勝敗のネオンカラー設定 */
    .win-text { color: #00ffcc; font-weight: bold; text-shadow: 0 0 10px #00ffcc; }
    .loss-text { color: #ff4b4b; font-weight: bold; text-shadow: 0 0 10px #ff4b4b; }
    h1 { color: #00ffcc; border-left: 5px solid #00ffcc; padding-left: 15px; }
    .stMetric {
        background: rgba(255, 255, 255, 0.05);
        padding: 15px; border-radius: 10px; border: 1px solid rgba(0, 255, 204, 0.2);
    }
    </style>
    """, unsafe_allow_html=True)  

# ==========================================
# STEP 2: データの読み書き設定 (Database)
# ==========================================
FILE_NAME = "data/data.csv"

# フォルダがない場合は作成
if not os.path.exists("data"):
    os.makedirs("data")

def load_data():
    if os.path.exists(FILE_NAME):
        df_loaded = pd.read_csv(FILE_NAME, dtype={"Score": str}).fillna("")
        df_loaded["Date"] = pd.to_datetime(df_loaded["Date"]).dt.date
        return df_loaded
    return pd.DataFrame(columns=["Date", "Game", "Result", "Rank", "Score", "Opponents", "Notes"])

def save_data(df):
    df.to_csv(FILE_NAME, index=False)

df = load_data()
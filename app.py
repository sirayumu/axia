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

# ==========================================
# STEP 3: 統計情報の表示 (Analytics)
# ==========================================
st.title("⚔ VICTO-LOG")
col1, col2, col3 = st.columns(3)
total = len(df)
wins = len(df[df["Result"] == "WIN"])
win_rate = (wins / total * 100) if total > 0 else 0

col1.metric("Win Rate", f"{win_rate:.1f}%")
col2.metric("Total Matches", total)
col3.metric("Wins", wins)
st.divider()

# ==========================================
# STEP 4: 検索とフィルタリング (Search & Filter)
# ==========================================
st.header("Filter History")
search_col1, search_col2 = st.columns(2)

with search_col1:
    # 下の入力フォームのGame Nameと連動させる
    search_query = st.text_input(
        "🔍 Search by Game Name", 
        value=st.session_state.get('sync_game', ""),
        placeholder="Fortnite, Apex, etc..."
    )

with search_col2:
    date_range = st.date_input("📅 Filter by Date Range", value=(datetime.now().date(), datetime.now().date()))

# フィルタ実行
display_df = df.copy()
if search_query:
    display_df = display_df[display_df["Game"].str.contains(search_query, case=False, na=False)]

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
    display_df = display_df[(display_df["Date"] >= start_date) & (display_df["Date"] <= end_date)]

# ==========================================
# STEP 5: 履歴の表示と削除 (History List)
# ==========================================
st.header("Match History")

if not display_df.empty:
    display_df = display_df.sort_values("Date", ascending=False)
    
    # ヘッダー作成
    h_cols = st.columns([2, 2, 1, 1, 1, 2, 3, 1])
    headers = ["DATE", "GAME", "RESULT", "RANK", "SCORE", "OPPONENTS", "NOTES", ""]
    for i, h in enumerate(headers):
        h_cols[i].write(f"**{h}**")

    # データ行作成
    for index, row in display_df.iterrows():
        cols = st.columns([2, 2, 1, 1, 1, 2, 3, 1])
        cols[0].write(row["Date"].strftime("%Y/%m/%d"))
        cols[1].write(row["Game"])
        
        res = row["Result"]
        res_class = "win-text" if res == "WIN" else "loss-text" if res == "LOSS" else ""
        cols[2].markdown(f'<span class="{res_class}">{res}</span>', unsafe_allow_html=True)
        
        cols[3].write(row["Rank"])
        cols[4].write(str(row["Score"]))
        cols[5].write(row["Opponents"])
        cols[6].write(row["Notes"])
        
        if cols[7].button("🗑️", key=f"del_{index}"):
            df = df.drop(index).reset_index(drop=True)
            save_data(df)
            st.rerun()
else:
    st.info("データが見つかりませんでした。")

st.divider()

# ==========================================
# STEP 6: 新規データの入力 (Input Form)
# ==========================================
st.header("Enter Match Result")

# 検索窓と連動させるための入力欄
game_input_val = st.text_input("Game Name", key="sync_game", help="入力すると上の表が自動で絞り込まれます")

with st.form("input_form", clear_on_submit=True):
    c1, c2 = st.columns(2)
    with c1:
        date_input = st.date_input("Date *", datetime.now())
        st.write(f"Adding for: **{game_input_val}**") # 確認用表示
        result_input = st.radio("Result", ["WIN", "LOSS", "DRAW"], horizontal=True)
    with c2:
        rank_input = st.text_input("Rank")
        score_input = st.text_input("Score", placeholder="例: 13-10")
        opp_input = st.text_input("Opponents")
    
    notes_input = st.text_area("Notes", placeholder="メモなど")
    submit = st.form_submit_button("SUBMIT")

    if submit:
        if not game_input_val:
            st.error("Game Nameを入力してください！")
        else:
            new_row = {
                "Date": date_input,
                "Game": game_input_val,
                "Result": result_input,
                "Rank": rank_input,
                "Score": score_input,
                "Opponents": opp_input,
                "Notes": notes_input
            }
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            save_data(df)
            st.success("追加完了！")
            st.rerun()

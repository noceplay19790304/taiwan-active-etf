import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta

# 1. 頁面配置：暗黑模式 + 寬螢幕
st.set_page_config(
    page_title="台股主動式 ETF 績效榜", 
    page_icon="📈", 
    layout="wide"
)

# 2. 自訂 CSS 打造專業財經風格面板
st.markdown("""
<style>
    .stApp {
        background-color: #0E1117;
        color: #E0E0E0;
    }
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #00F2FE 0%, #4FACFE 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        color: #8A99AD;
        font-size: 0.95rem;
        margin-bottom: 1.5rem;
    }
    /* 表格卡片外框 */
    .table-header {
        font-size: 1.2rem;
        font-weight: 700;
        padding: 8px 12px;
        border-radius: 6px 6px 0px 0px;
        text-align: center;
        margin-bottom: -10px;
    }
    .h-5d { background-color: rgba(255, 75, 75, 0.2); color: #FF4B4B; border: 1px solid #FF4B4B; }
    .h-20d { background-color: rgba(255, 193, 7, 0.2); color: #FFC107; border: 1px solid #FFC107; }
    .h-60d { background-color: rgba(79, 172, 254, 0.2); color: #4FACFE; border: 1px solid #4FACFE; }
</style>
""", unsafe_allow_html=True)

# 頁面標題
st.markdown('<div class="main-title">📈 台股主動式 ETF 績效排行榜</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">分別依 5日、20日、60日 累積報酬率獨立排序 (第一名至最後一名)</div>', unsafe_allow_html=True)

# 追蹤標的 (可自由新增或調整代號)
ETF_LIST = ["00980A", "00981A", "00982A", "00400A", "0050"]

@st.cache_data(ttl=3600)
def load_etf_data():
    results = []
    today = datetime.today()
    start_date = (today - timedelta(days=150)).strftime("%Y-%m-%d")
    
    for symbol in ETF_LIST:
        try:
            url = f"https://api.finmindtrade.com/api/v4/data?dataset=TaiwanStockPrice&data_id={symbol}&start_date={start_date}"
            res = requests.get(url, timeout=5)
            data = res.json()
            
            if data.get("msg") == "success" and len(data.get("data", [])) >= 6:
                df = pd.DataFrame(data["data"])
                prices = df['close'].tolist()
                
                latest = prices[-1]
                p_5d = prices[-6]
                
                r5 = round(((latest - p_5d) / p_5d) * 100, 2)
                r20 = round(((latest - prices[-21]) / prices[-21]) * 100, 2) if len(prices) >= 21 else None
                r60 = round(((latest - prices[-61]) / prices[-61]) * 100, 2) if len(prices) >= 61 else None
                
                results.append({
                    "ETF代號": symbol,
                    "最新價": round(latest, 2),
                    "5日績效": r5,
                    "20日績效": r20,
                    "60日績效": r60
                })
        except Exception:
            continue
            
    return pd.DataFrame(results)

with st.spinner('⚡ 正在計算 5D / 20D / 60D 績效排行榜...'):
    raw_df = load_etf_data()

if not raw_df.empty:
    # 色塊呈現邏輯 (正紅負綠)
    def style_performance(val):
        if pd.isna(val):
            return 'color: #777777;'
        elif val > 0:
            return 'background-color: rgba(255, 75, 75, 0.2); color: #FF4B4B; font-weight: bold;'
        elif val < 0:
            return 'background-color: rgba(0, 200, 83, 0.2); color: #00E676; font-weight: bold;'
        else:
            return 'color: #FFFFFF;'

    # 建立三欄平鋪版型
    col1, col2, col3 = st.columns(3)

    # ----------------------------------------------------
    # 表格 1：5日績效排名
    # ----------------------------------------------------
    with col1:
        st.markdown('<div class="table-header h-5d">🔥 近 5 日績效排名</div>', unsafe_allow_html=True)
        df_5d = raw_df.dropna(subset=["5日績效"]).sort_values(by="5日績效", ascending=False).reset_index(drop=True)
        df_5d["名次"] = range(1, len(df_5d) + 1)
        df_5d = df_5d[["名次", "ETF代號", "最新價", "5日績效"]]
        
        styled_5d = (
            df_5d.style
            .map(style_performance, subset=["5日績效"])
            .format({"最新價": "${:.2f}", "5日績效": "{:+.2f}%"})
        )
        st.dataframe(styled_5d, use_container_width=True, hide_index=True)

    # ----------------------------------------------------
    # 表格 2：20日績效排名
    # ----------------------------------------------------
    with col2:
        st.markdown('<div class="table-header h-20d">👑 近 20 日績效排名</div>', unsafe_allow_html=True)
        df_20d = raw_df.dropna(subset=["20日績效"]).sort_values(by="20日績效", ascending=False).reset_index(drop=True)
        df_20d["名次"] = range(1, len(df_20d) + 1)
        df_20d = df_20d[["名次", "ETF代號", "最新價", "20日績效"]]
        
        styled_20d = (
            df_20d.style
            .map(style_performance, subset=["20日績效"])
            .format({"最新價": "${:.2f}", "20日績效": "{:+.2f}%"})
        )
        st.dataframe(styled_20d, use_container_width=True, hide_index=True)

    # ----------------------------------------------------
    # 表格 3：60日績效排名
    # ----------------------------------------------------
    with col3:
        st.markdown('<div class="table-header h-60d">🚀 近 60 日績效排名</div>', unsafe_allow_html=True)
        df_60d = raw_df.dropna(subset=["60日績效"]).sort_values(by="60日績效", ascending=False).reset_index(drop=True)
        df_60d["名次"] = range(1, len(df_60d) + 1)
        df_60d = df_60d[["名次", "ETF代號", "最新價", "60日績效"]]
        
        styled_60d = (
            df_60d.style
            .map(style_performance, subset=["60日績效"])
            .format({"最新價": "${:.2f}", "60日績效": "{:+.2f}%"})
        )
        st.dataframe(styled_60d, use_container_width=True, hide_index=True)

else:
    st.error("⚠️ 資料載入失敗，請確認網路連線或 ETF 代號。")

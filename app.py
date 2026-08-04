import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta

# 1. 頁面配置：暗黑模式 + 寬螢幕
st.set_page_config(
    page_title="台股主動式 ETF 績效終端", 
    page_icon="📈", 
    layout="wide"
)

# 2. 自訂 CSS 打造專業財經風格面板
st.markdown("""
<style>
    /* 全域背景與字體優化 */
    .stApp {
        background-color: #0E1117;
        color: #E0E0E0;
    }
    
    /* 標題與副標題樣式 */
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

    /* Metric 卡片樣式重置 */
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem !important;
        font-weight: 700;
    }
    
    /* 自訂提醒盒樣式 */
    .info-box {
        background: #1E232A;
        border-left: 4px solid #00F2FE;
        padding: 10px 15px;
        border-radius: 4px;
        font-size: 0.85rem;
        color: #B0C0D0;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# 頁面標題
st.markdown('<div class="main-title">📈 台股主動式 ETF 績效終端</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">即時追蹤近 5日 / 20日 / 60日 多週期累積報酬率 (Data powered by FinMind)</div>', unsafe_allow_html=True)

# 追蹤標的 (包含熱門主動式/被動式 ETF 作為對照)
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
                    "最新價(元)": round(latest, 2),
                    "5日績效": r5,
                    "20日績效": r20,
                    "60日績效": r60
                })
        except Exception:
            continue
            
    return pd.DataFrame(results)

with st.spinner('⚡ 正在載入金融市場數據...'):
    df = load_etf_data()

if not df.empty:
    # 預設按 20日績效 降序排序
    df = df.sort_values(by="20日績效", ascending=False).reset_index(drop=True)

    # ----------------------------------------------------
    # 頂部看板 (Top Market Leaders)
    # ----------------------------------------------------
    col1, col2, col3 = st.columns(3)
    
    # 防呆過濾以避免抓取資料不全導致 KeyError
    df_5d = df.dropna(subset=["5日績效"]).sort_values(by="5日績效", ascending=False)
    df_20d = df.dropna(subset=["20日績效"]).sort_values(by="20日績效", ascending=False)
    df_60d = df.dropna(subset=["60日績效"]).sort_values(by="60日績效", ascending=False)

    with col1:
        if not df_5d.empty:
            b5 = df_5d.iloc[0]
            st.metric(
                label="🔥 近 5 日強勢王", 
                value=f"{b5['ETF代號']} (${b5['最新價(元)']})", 
                delta=f"{b5['5日績效']}% (5D)"
            )
    with col2:
        if not df_20d.empty:
            b20 = df_20d.iloc[0]
            st.metric(
                label="👑 近 20 日冠軍", 
                value=f"{b20['ETF代號']} (${b20['最新價(元)']})", 
                delta=f"{b20['20日績效']}% (20D)"
            )
    with col3:
        if not df_60d.empty:
            b60 = df_60d.iloc[0]
            st.metric(
                label="🚀 近 60 日長線王", 
                value=f"{b60['ETF代號']} (${b60['最新價(元)']})", 
                delta=f"{b60['60日績效']}% (60D)"
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # ----------------------------------------------------
    # 全績效比較大表 (一目瞭然 + 色塊標示)
    # ----------------------------------------------------
    st.subheader("📊 全週期績效排行榜")
    st.markdown('<div class="info-box">💡 點擊下方表格欄位標題（如：5日績效）即可自動依該週期重新排序。</div>', unsafe_allow_html=True)

    # 設定台股漲跌色塊 (紅漲綠跌/正紅負綠)
    def style_performance(val):
        if pd.isna(val):
            return 'color: #777777;'
        elif val > 0:
            return 'background-color: rgba(255, 75, 75, 0.2); color: #FF4B4B; font-weight: bold;'
        elif val < 0:
            return 'background-color: rgba(0, 200, 83, 0.2); color: #00E676; font-weight: bold;'
        else:
            return 'color: #FFFFFF;'

    # 套用 Style 到 5日、20日、60日 欄位 (使用最新 .map 語法)
    styled_df = (
        df.style
        .map(style_performance, subset=["5日績效", "20日績效", "60日績效"])
        .format({
            "最新價(元)": "{:.2f}",
            "5日績效": "{:+.2f}%",
            "20日績效": "{:+.2f}%",
            "60日績效": "{:+.2f}%"
        }, na_rep="N/A")
    )

    # 渲染專業風格表格
    st.dataframe(
        styled_df,
        use_container_width=True,
        hide_index=True,
        height=300
    )

else:
    st.error("⚠️ 資料載入失敗，請確認網路連線或 ETF 代號。")

import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta

# 1. 頁面配置
st.set_page_config(
    page_title="台股主動式 ETF 績效終端", 
    page_icon="📈", 
    layout="wide"
)

# 2. 自訂高對比度 CSS (字體加粗加亮、深色高對比背景)
st.markdown("""
<style>
    /* 全域背景與高對比文字 */
    .stApp {
        background-color: #0B0E14;
        color: #FFFFFF !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    }
    
    /* 大標題與副標題 */
    .main-title {
        font-size: 2.4rem;
        font-weight: 900;
        color: #00F2FE;
        letter-spacing: 0.5px;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        color: #D1D5DB !important;
        font-size: 1.05rem;
        font-weight: 600;
        margin-bottom: 1.5rem;
    }

    /* 區塊小標題 */
    .section-title {
        font-size: 1.3rem;
        font-weight: 800;
        color: #FFFFFF;
        border-left: 5px solid #00F2FE;
        padding-left: 10px;
        margin-top: 15px;
        margin-bottom: 15px;
    }

    /* 表格標題頭部 */
    .table-header {
        font-size: 1.25rem;
        font-weight: 900;
        padding: 10px 12px;
        border-radius: 6px 6px 0px 0px;
        text-align: center;
        margin-bottom: -5px;
        letter-spacing: 0.5px;
    }
    .h-bench { background-color: #1E293B; color: #38BDF8; border: 2px solid #38BDF8; }
    .h-5d { background-color: #3B0764; color: #FF708F; border: 2px solid #FF4B4B; }
    .h-20d { background-color: #451A03; color: #FCD34D; border: 2px solid #F59E0B; }
    .h-60d { background-color: #064E3B; color: #34D399; border: 2px solid #10B981; }

    /* Streamlit 原生表格內文字加粗與高對比 */
    div[data-testid="stDataFrame"] {
        font-size: 1.05rem !important;
        font-weight: 700 !important;
    }
</style>
""", unsafe_allow_html=True)

# 頁面標題
st.markdown('<div class="main-title">📈 台股主動式 ETF 績效終端</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">頂部設定大盤基準線，下方即時對比純主動式 ETF 5日 / 20日 / 60日 累積報酬率</div>', unsafe_allow_html=True)

# 1. 大盤基準清單 (被動/指數型)
BENCHMARK_LIST = ["0050", "009816"]

# 2. 純主動式 ETF 清單
ACTIVE_ETF_LIST = ["00980A", "00981A", "00982A", "00400A"]

@st.cache_data(ttl=3600)
def fetch_stock_data(symbol_list):
    results = []
    today = datetime.today()
    start_date = (today - timedelta(days=150)).strftime("%Y-%m-%d")
    
    for symbol in symbol_list:
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

with st.spinner('⚡ 正在載入金融市場數據...'):
    bench_df = fetch_stock_data(BENCHMARK_LIST)
    active_df = fetch_stock_data(ACTIVE_ETF_LIST)

# 正紅負綠高對比色塊樣式 (字體加粗與提高彩度)
def style_performance(val):
    if pd.isna(val):
        return 'color: #9CA3AF; font-weight: bold;'
    elif val > 0:
        return 'background-color: #7F1D1D; color: #FF6B6B; font-weight: 900; font-size: 1.05rem;'
    elif val < 0:
        return 'background-color: #064E3B; color: #4ADE80; font-weight: 900; font-size: 1.05rem;'
    else:
        return 'color: #FFFFFF; font-weight: bold;'

# ----------------------------------------------------
# 頂部：獨立大盤與基準對照區 (Benchmark)
# ----------------------------------------------------
st.markdown('<div class="section-title">📌 大盤與市場基準對照 (Benchmark)</div>', unsafe_allow_html=True)

if not bench_df.empty:
    st.markdown('<div class="table-header h-bench">⚖️ 基準對照標的 (0050 / 009816)</div>', unsafe_allow_html=True)
    styled_bench = (
        bench_df.style
        .map(style_performance, subset=["5日績效", "20日績效", "60日績效"])
        .format({"最新價": "${:.2f}", "5日績效": "{:+.2f}%", "20日績效": "{:+.2f}%", "60日績效": "{:+.2f}%"})
    )
    st.dataframe(styled_bench, use_container_width=True, hide_index=True)
else:
    st.warning("⚠️ 基準資料載入中或無法取得...")

st.markdown("<br>", unsafe_allow_html=True)

# ----------------------------------------------------
# 下方：三大天期純主動式 ETF 獨立排行榜
# ----------------------------------------------------
st.markdown('<div class="section-title">🏆 主動式 ETF 全週期績效排行榜</div>', unsafe_allow_html=True)

if not active_df.empty:
    col1, col2, col3 = st.columns(3)

    # 1. 5日績效
    with col1:
        st.markdown('<div class="table-header h-5d">🔥 近 5 日績效排名</div>', unsafe_allow_html=True)
        df_5d = active_df.dropna(subset=["5日績效"]).sort_values(by="5日績效", ascending=False).reset_index(drop=True)
        df_5d["名次"] = range(1, len(df_5d) + 1)
        df_5d = df_5d[["名次", "ETF代號", "最新價", "5日績效"]]
        
        styled_5d = (
            df_5d.style
            .map(style_performance, subset=["5日績效"])
            .format({"最新價": "${:.2f}", "5日績效": "{:+.2f}%"})
        )
        st.dataframe(styled_5d, use_container_width=True, hide_index=True)

    # 2. 20日績效
    with col2:
        st.markdown('<div class="table-header h-20d">👑 近 20 日績效排名</div>', unsafe_allow_html=True)
        df_20d = active_df.dropna(subset=["20日績效"]).sort_values(by="20日績效", ascending=False).reset_index(drop=True)
        df_20d["名次"] = range(1, len(df_20d) + 1)
        df_20d = df_20d[["名次", "ETF代號", "最新價", "20日績效"]]
        
        styled_20d = (
            df_20d.style
            .map(style_performance, subset=["20日績效"])
            .format({"最新價": "${:.2f}", "20日績效": "{:+.2f}%"})
        )
        st.dataframe(styled_20d, use_container_width=True, hide_index=True)

    # 3. 60日績效
    with col3:
        st.markdown('<div class="table-header h-60d">🚀 近 60 日績效排名</div>', unsafe_allow_html=True)
        df_60d = active_df.dropna(subset=["60日績效"]).sort_values(by="60日績效", ascending=False).reset_index(drop=True)
        df_60d["名次"] = range(1, len(df_60d) + 1)
        df_60d = df_60d[["名次", "ETF代號", "最新價", "60日績效"]]
        
        styled_60d = (
            df_60d.style
            .map(style_performance, subset=["60日績效"])
            .format({"最新價": "${:.2f}", "60日績效": "{:+.2f}%"})
        )
        st.dataframe(styled_60d, use_container_width=True, hide_index=True)

else:
    st.error("⚠️ 資料載入失敗，請確認網路連線或代號。")

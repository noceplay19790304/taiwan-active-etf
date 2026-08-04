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

# 2. 自訂深藍底 + 全黃字高對比 CSS
st.markdown("""
<style>
    /* 全域極致深藍背景 */
    .stApp {
        background-color: #030712 !important;
        color: #FFE81F !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
    }
    
    /* 大標題黃金霓虹效果 */
    .main-title {
        font-size: 2.5rem;
        font-weight: 900;
        text-align: center;
        color: #FFE81F;
        text-shadow: 0px 0px 20px rgba(255, 232, 31, 0.5);
        margin-bottom: 0.3rem;
    }
    .sub-title {
        color: #FDE047 !important;
        font-size: 1.05rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 2rem;
    }

    /* 區塊標題 */
    .section-title {
        font-size: 1.35rem;
        font-weight: 900;
        color: #FFE81F;
        border-left: 5px solid #FACC15;
        padding-left: 12px;
        margin-top: 10px;
        margin-bottom: 15px;
        text-shadow: 0 0 10px rgba(250, 204, 21, 0.3);
    }

    /* 深藍晶透表頭 */
    .table-header {
        font-size: 1.2rem;
        font-weight: 900;
        padding: 12px 15px;
        border-radius: 12px 12px 0px 0px;
        text-align: center;
        margin-bottom: -5px;
        letter-spacing: 1px;
        background: #0F172A !important;
        color: #FFE81F !important;
        border: 2px solid #3B82F6 !important;
    }

    /* 強制 Streamlit 原生表格內容居中、深藍底、粗黃字 */
    div[data-testid="stDataFrame"] table {
        text-align: center !important;
    }
    div[data-testid="stDataFrame"] td, div[data-testid="stDataFrame"] th {
        text-align: center !important;
        font-size: 1.1rem !important;
        font-weight: 900 !important;
        color: #FFE81F !important;
        background-color: #1E293B !important;
        border-color: #334155 !important;
    }
    div[data-testid="stDataFrame"] th {
        background-color: #0F172A !important;
    }
</style>
""", unsafe_allow_html=True)

# 頁面標題
st.markdown('<div class="main-title">📈 台股主動式 ETF 績效終端</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">頂部設定大盤基準線，下方即時對比純主動式 ETF 5日 / 20日 / 60日 累積報酬率</div>', unsafe_allow_html=True)

# 1. 大盤基準清單
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

with st.spinner('⚡ 正在載入深藍高對比金融數據...'):
    bench_df = fetch_stock_data(BENCHMARK_LIST)
    active_df = fetch_stock_data(ACTIVE_ETF_LIST)

# 🎨 深藍底 + 鮮黃字樣式定義
def style_rank(val):
    return 'background-color: #0F172A; color: #FFE81F; font-weight: 900; text-align: center; border: 1px solid #3B82F6;'

def style_symbol(val):
    return 'background-color: #0F172A; color: #FFE81F; font-weight: 900; text-align: center; border: 1px solid #FACC15;'

def style_price(val):
    return 'background-color: #1E293B; color: #FFE81F; font-weight: 900; text-align: center;'

def style_performance(val):
    # 統一採用深藍底 + 鮮黃字包覆（帶微黃線框增強對比）
    return 'background-color: #0F172A; color: #FFE81F; font-weight: 900; text-align: center; border: 1px solid #FACC15; border-radius: 4px;'

# ----------------------------------------------------
# 頂部：獨立大盤與基準對照區 (Benchmark)
# ----------------------------------------------------
st.markdown('<div class="section-title">📌 大盤與市場基準對照 (Benchmark)</div>', unsafe_allow_html=True)

if not bench_df.empty:
    st.markdown('<div class="table-header">⚖️ 基準對照標的 (0050 / 009816)</div>', unsafe_allow_html=True)
    styled_bench = (
        bench_df.style
        .map(style_symbol, subset=["ETF代號"])
        .map(style_price, subset=["最新價"])
        .map(style_performance, subset=["5日績效", "20日績效", "60日績效"])
        .format({"最新價": "${:.2f}", "5日績效": "{:+.2f}%", "20日績效": "{:+.2f}%", "60日績效": "{:+.2f}%"})
    )
    st.dataframe(styled_bench, use_container_width=True, hide_index=True)

st.markdown("<br>", unsafe_allow_html=True)

# ----------------------------------------------------
# 下方：三大天期純主動式 ETF 獨立排行榜
# ----------------------------------------------------
st.markdown('<div class="section-title">🏆 主動式 ETF 全週期績效排行榜</div>', unsafe_allow_html=True)

if not active_df.empty:
    col1, col2, col3 = st.columns(3)

    # 1. 5日績效
    with col1:
        st.markdown('<div class="table-header">🔥 近 5 日績效排名</div>', unsafe_allow_html=True)
        df_5d = active_df.dropna(subset=["5日績效"]).sort_values(by="5日績效", ascending=False).reset_index(drop=True)
        df_5d["名次"] = [f"N°{i}" for i in range(1, len(df_5d) + 1)]
        df_5d = df_5d[["名次", "ETF代號", "最新價", "5日績效"]]
        
        styled_5d = (
            df_5d.style
            .map(style_rank, subset=["名次"])
            .map(style_symbol, subset=["ETF代號"])
            .map(style_price, subset=["最新價"])
            .map(style_performance, subset=["5日績效"])
            .format({"最新價": "${:.2f}", "5日績效": "{:+.2f}%"})
        )
        st.dataframe(styled_5d, use_container_width=True, hide_index=True)

    # 2. 20日績效
    with col2:
        st.markdown('<div class="table-header">👑 近 20 日績效排名</div>', unsafe_allow_html=True)
        df_20d = active_df.dropna(subset=["20日績效"]).sort_values(by="20日績效", ascending=False).reset_index(drop=True)
        df_20d["名次"] = [f"N°{i}" for i in range(1, len(df_20d) + 1)]
        df_20d = df_20d[["名次", "ETF代號", "最新價", "20日績效"]]
        
        styled_20d = (
            df_20d.style
            .map(style_rank, subset=["名次"])
            .map(style_symbol, subset=["ETF代號"])
            .map(style_price, subset=["最新價"])
            .map(style_performance, subset=["20日績效"])
            .format({"最新價": "${:.2f}", "20日績效": "{:+.2f}%"})
        )
        st.dataframe(styled_20d, use_container_width=True, hide_index=True)

    # 3. 60日績效
    with col3:
        st.markdown('<div class="table-header">🚀 近 60 日績效排名</div>', unsafe_allow_html=True)
        df_60d = active_df.dropna(subset=["60日績效"]).sort_values(by="60日績效", ascending=False).reset_index(drop=True)
        df_60d["名次"] = [f"N°{i}" for i in range(1, len(df_60d) + 1)]
        df_60d = df_60d[["名次", "ETF代號", "最新價", "60日績效"]]
        
        styled_60d = (
            df_60d.style
            .map(style_rank, subset=["名次"])
            .map(style_symbol, subset=["ETF代號"])
            .map(style_price, subset=["最新價"])
            .map(style_performance, subset=["60日績效"])
            .format({"最新價": "${:.2f}", "60日績效": "{:+.2f}%"})
        )
        st.dataframe(styled_60d, use_container_width=True, hide_index=True)

else:
    st.error("⚠️ 資料載入失敗，請確認網路連線。")

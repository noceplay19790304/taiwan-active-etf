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

# 2. 自訂 Cyberpunk 晶透毛玻璃與全高對比 CSS
st.markdown("""
<style>
    /* 全域暗黑底色與背景微光 */
    .stApp {
        background: radial-gradient(circle at 50% 10%, #1a1c29 0%, #080a11 100%);
        color: #FFFFFF !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
    }
    
    /* 大標題霓虹果凍效果 */
    .main-title {
        font-size: 2.5rem;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(135deg, #00F2FE 0%, #4FACFE 50%, #00C6FF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0px 0px 20px rgba(0, 242, 254, 0.3);
        margin-bottom: 0.3rem;
    }
    .sub-title {
        color: #94A3B8 !important;
        font-size: 1.05rem;
        font-weight: 600;
        text-align: center;
        margin-bottom: 2rem;
    }

    /* 區塊標題 */
    .section-title {
        font-size: 1.35rem;
        font-weight: 800;
        color: #38BDF8;
        border-left: 5px solid #00F2FE;
        padding-left: 12px;
        margin-top: 10px;
        margin-bottom: 15px;
        text-shadow: 0 0 10px rgba(56, 189, 248, 0.4);
    }

    /* 晶透毛玻璃表頭 (Glassmorphism Table Header) */
    .table-header {
        font-size: 1.2rem;
        font-weight: 900;
        padding: 12px 15px;
        border-radius: 12px 12px 0px 0px;
        text-align: center;
        margin-bottom: -5px;
        letter-spacing: 1px;
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }
    .h-bench { 
        background: rgba(30, 41, 59, 0.7); 
        color: #38BDF8; 
        border: 1px solid rgba(56, 189, 248, 0.5); 
    }
    .h-5d { 
        background: rgba(131, 24, 67, 0.6); 
        color: #FF70A6; 
        border: 1px solid rgba(255, 112, 166, 0.5); 
    }
    .h-20d { 
        background: rgba(120, 53, 15, 0.6); 
        color: #FBBF24; 
        border: 1px solid rgba(251, 191, 36, 0.5); 
    }
    .h-60d { 
        background: rgba(6, 78, 59, 0.6); 
        color: #34D399; 
        border: 1px solid rgba(52, 211, 153, 0.5); 
    }

    /* 全表格內容強行置中與高對比字體 */
    div[data-testid="stDataFrame"] table {
        text-align: center !important;
    }
    div[data-testid="stDataFrame"] td, div[data-testid="stDataFrame"] th {
        text-align: center !important;
        font-size: 1.05rem !important;
        font-weight: 800 !important;
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

with st.spinner('⚡ 正在載入金融市場數據...'):
    bench_df = fetch_stock_data(BENCHMARK_LIST)
    active_df = fetch_stock_data(ACTIVE_ETF_LIST)

# 🎨 全欄位高對比色彩 & 果凍色塊設定
def style_rank(val):
    return 'background-color: rgba(99, 102, 241, 0.25); color: #A5B4FC; font-weight: 900; text-align: center;'

def style_symbol(val):
    return 'background-color: rgba(14, 165, 233, 0.25); color: #38BDF8; font-weight: 900; text-align: center;'

def style_price(val):
    return 'background-color: rgba(234, 179, 8, 0.2); color: #FDE047; font-weight: 900; text-align: center;'

def style_performance(val):
    if pd.isna(val):
        return 'color: #6B7280; text-align: center;'
    elif val > 0:
        return 'background-color: rgba(239, 68, 68, 0.35); color: #FF6B6B; font-weight: 900; text-align: center; border-radius: 4px;'
    elif val < 0:
        return 'background-color: rgba(34, 197, 94, 0.35); color: #4ADE80; font-weight: 900; text-align: center; border-radius: 4px;'
    else:
        return 'color: #FFFFFF; font-weight: 900; text-align: center;'

# ----------------------------------------------------
# 頂部：獨立大盤與基準對照區 (Benchmark)
# ----------------------------------------------------
st.markdown('<div class="section-title">📌 大盤與市場基準對照 (Benchmark)</div>', unsafe_allow_html=True)

if not bench_df.empty:
    st.markdown('<div class="table-header h-bench">⚖️ 基準對照標的 (0050 / 009816)</div>', unsafe_allow_html=True)
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
        st.markdown('<div class="table-header h-5d">🔥 近 5 日績效排名</div>', unsafe_allow_html=True)
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
        st.markdown('<div class="table-header h-20d">👑 近 20 日績效排名</div>', unsafe_allow_html=True)
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
        st.markdown('<div class="table-header h-60d">🚀 近 60 日績效排名</div>', unsafe_allow_html=True)
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

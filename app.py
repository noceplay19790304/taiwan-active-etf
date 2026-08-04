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

# 2. 深藍底 + 全黃字高對比 CSS 樣式
st.markdown("""
<style>
    /* 全域背景：極致深黑底 */
    .stApp {
        background-color: #030712 !important;
        color: #FFE81F !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    }
    
    /* 大標題與副標題 */
    .main-title {
        font-size: 2.5rem;
        font-weight: 900;
        text-align: center;
        color: #FFE81F;
        text-shadow: 0 0 20px rgba(255, 232, 31, 0.5);
        margin-bottom: 0.2rem;
    }
    .sub-title {
        color: #FDE047 !important;
        font-size: 1.1rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 2rem;
    }

    .section-title {
        font-size: 1.4rem;
        font-weight: 900;
        color: #FFE81F;
        border-left: 6px solid #FACC15;
        padding-left: 12px;
        margin-top: 20px;
        margin-bottom: 15px;
        text-shadow: 0 0 10px rgba(250, 204, 21, 0.3);
    }

    /* 全深藍底表格結構 */
    .custom-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0 8px; /* 列與列間距 */
        margin-bottom: 20px;
    }
    
    /* 統一標頭：深藍背景 + 鮮黃字 + 亮線邊框 */
    .custom-table th {
        background-color: #0F172A !important;
        color: #FFE81F !important;
        font-size: 1.2rem !important;
        font-weight: 900 !important;
        padding: 14px 10px;
        text-align: center !important;
        border: 2px solid #3B82F6 !important;
        letter-spacing: 0.5px;
    }

    /* 統一資料格：極致深藍背景 + 全鮮黃字 + 藍色線條框 */
    .custom-table td {
        background-color: #1E293B !important;
        color: #FFE81F !important;
        padding: 14px 10px;
        text-align: center !important;
        font-size: 1.15rem !important;
        font-weight: 900 !important;
        border-top: 1px solid #334155 !important;
        border-bottom: 1px solid #334155 !important;
    }

    /* 邊框膠囊包覆增強可讀性 */
    .yellow-badge {
        background-color: #0F172A;
        color: #FFE81F !important;
        font-weight: 900 !important;
        font-size: 1.2rem !important;
        padding: 6px 14px;
        border-radius: 8px;
        border: 1px solid #FACC15;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)

# 標題
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

# 全黃字數值格式化工具
def render_yellow_perf(val):
    if pd.isna(val) or val is None:
        return '<span class="yellow-badge">N/A</span>'
    elif val > 0:
        return f'<span class="yellow-badge">+{val:.2f}%</span>'
    elif val < 0:
        return f'<span class="yellow-badge">{val:.2f}%</span>'
    else:
        return f'<span class="yellow-badge">0.00%</span>'

with st.spinner('⚡ 正在載入高清晰深藍黃字數據...'):
    bench_df = fetch_stock_data(BENCHMARK_LIST)
    active_df = fetch_stock_data(ACTIVE_ETF_LIST)

# ----------------------------------------------------
# 頂部：基準對照區 (Benchmark)
# ----------------------------------------------------
st.markdown('<div class="section-title">📌 大盤與市場基準對照 (Benchmark)</div>', unsafe_allow_html=True)

if not bench_df.empty:
    html_code = """
    <table class="custom-table">
        <thead>
            <tr>
                <th>代號</th>
                <th>最新價</th>
                <th>5日績效</th>
                <th>20日績效</th>
                <th>60日績效</th>
            </tr>
        </thead>
        <tbody>
    """
    for _, row in bench_df.iterrows():
        html_code += f"""
        <tr>
            <td><span class="yellow-badge">{row['ETF代號']}</span></td>
            <td>${row['最新價']:.2f}</td>
            <td>{render_yellow_perf(row['5日績效'])}</td>
            <td>{render_yellow_perf(row['20日績效'])}</td>
            <td>{render_yellow_perf(row['60日績效'])}</td>
        </tr>
        """
    html_code += "</tbody></table>"
    st.markdown(html_code, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ----------------------------------------------------
# 下方：三大天期獨立排行榜 (深藍底 + 全黃字)
# ----------------------------------------------------
st.markdown('<div class="section-title">🏆 主動式 ETF 全週期績效排行榜</div>', unsafe_allow_html=True)

if not active_df.empty:
    col1, col2, col3 = st.columns(3)

    # 1. 近 5 日
    with col1:
        df_5d = active_df.dropna(subset=["5日績效"]).sort_values(by="5日績效", ascending=False).reset_index(drop=True)
        html_5d = """
        <table class="custom-table">
            <thead>
                <tr>
                    <th colspan="4">🔥 近 5 日績效排名</th>
                </tr>
                <tr>
                    <th>名次</th>
                    <th>代號</th>
                    <th>最新價</th>
                    <th>報酬率</th>
                </tr>
            </thead>
            <tbody>
        """
        for idx, row in df_5d.iterrows():
            html_5d += f"""
            <tr>
                <td>N°{idx+1}</td>
                <td><span class="yellow-badge">{row['ETF代號']}</span></td>
                <td>${row['最新價']:.2f}</td>
                <td>{render_yellow_perf(row['5日績效'])}</td>
            </tr>
            """
        html_5d += "</tbody></table>"
        st.markdown(html_5d, unsafe_allow_html=True)

    # 2. 近 20 日
    with col2:
        df_20d = active_df.dropna(subset=["20日績效"]).sort_values(by="20日績效", ascending=False).reset_index(drop=True)
        html_20d = """
        <table class="custom-table">
            <thead>
                <tr>
                    <th colspan="4">👑 近 20 日績效排名</th>
                </tr>
                <tr>
                    <th>名次</th>
                    <th>代號</th>
                    <th>最新價</th>
                    <th>報酬率</th>
                </tr>
            </thead>
            <tbody>
        """
        for idx, row in df_20d.iterrows():
            html_20d += f"""
            <tr>
                <td>N°{idx+1}</td>
                <td><span class="yellow-badge">{row['ETF代號']}</span></td>
                <td>${row['最新價']:.2f}</td>
                <td>{render_yellow_perf(row['20日績效'])}</td>
            </tr>
            """
        html_20d += "</tbody></table>"
        st.markdown(html_20d, unsafe_allow_html=True)

    # 3. 近 60 日
    with col3:
        df_60d = active_df.dropna(subset=["60日績效"]).sort_values(by="60日績效", ascending=False).reset_index(drop=True)
        html_60d = """
        <table class="custom-table">
            <thead>
                <tr>
                    <th colspan="4">🚀 近 60 日績效排名</th>
                </tr>
                <tr>
                    <th>名次</th>
                    <th>代號</th>
                    <th>最新價</th>
                    <th>報酬率</th>
                </tr>
            </thead>
            <tbody>
        """
        for idx, row in df_60d.iterrows():
            html_60d += f"""
            <tr>
                <td>N°{idx+1}</td>
                <td><span class="yellow-badge">{row['ETF代號']}</span></td>
                <td>${row['最新價']:.2f}</td>
                <td>{render_yellow_perf(row['60日績效'])}</td>
            </tr>
            """
        html_60d += "</tbody></table>"
        st.markdown(html_60d, unsafe_allow_html=True)

else:
    st.error("⚠️ 資料載入失敗，請確認網路連線。")

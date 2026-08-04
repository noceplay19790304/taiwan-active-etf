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

# 2. 超高對比強效 CSS 樣式
st.markdown("""
<style>
    /* 全域背景：極致深黑 */
    .stApp {
        background-color: #08090C !important;
        color: #FFFFFF !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    }
    
    /* 標題與副標題 */
    .main-title {
        font-size: 2.5rem;
        font-weight: 900;
        text-align: center;
        color: #00F2FE;
        text-shadow: 0 0 15px rgba(0, 242, 254, 0.6);
        margin-bottom: 0.2rem;
    }
    .sub-title {
        color: #CBD5E1 !important;
        font-size: 1.1rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 2rem;
    }

    .section-title {
        font-size: 1.4rem;
        font-weight: 900;
        color: #38BDF8;
        border-left: 6px solid #00F2FE;
        padding-left: 12px;
        margin-top: 20px;
        margin-bottom: 15px;
    }

    /* 自訂超高對比 HTML 表格樣式 */
    .custom-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0 8px; /* 列與列之間的間隔 */
        margin-bottom: 20px;
    }
    
    .custom-table th {
        background-color: #1E293B;
        color: #38BDF8;
        font-size: 1.15rem;
        font-weight: 900;
        padding: 12px;
        text-align: center;
        border: 1px solid #334155;
    }
    
    /* 表頭專屬色彩 */
    .th-bench { background-color: #0F172A !important; color: #38BDF8 !important; border: 2px solid #0284C7 !important; }
    .th-5d { background-color: #4C0519 !important; color: #FF70A6 !important; border: 2px solid #E11D48 !important; }
    .th-20d { background-color: #451A03 !important; color: #FCD34D !important; border: 2px solid #D97706 !important; }
    .th-60d { background-color: #064E3B !important; color: #34D399 !important; border: 2px solid #059669 !important; }

    .custom-table td {
        padding: 12px 8px;
        text-align: center;
        font-size: 1.1rem;
        font-weight: 900;
        background-color: #111827;
        border-top: 1px solid #1F2937;
        border-bottom: 1px solid #1F2937;
    }

    /* 欄位高對比爆亮色彩 */
    .badge-rank { background-color: #312E81; color: #A5B4FC; font-size: 1.1rem; padding: 6px 12px; border-radius: 6px; border: 1px solid #4338CA; }
    .badge-symbol { background-color: #0C4A6E; color: #38BDF8; font-size: 1.15rem; padding: 6px 12px; border-radius: 6px; border: 1px solid #0284C7; }
    .badge-price { color: #FDE047; font-size: 1.15rem; font-weight: 900; }
    
    /* 漲跌純爆亮色塊 */
    .pos-val { background-color: #991B1B !important; color: #FFD1D1 !important; font-size: 1.2rem !important; font-weight: 900 !important; border-radius: 6px; padding: 6px 10px; border: 1px solid #EF4444; }
    .neg-val { background-color: #065F46 !important; color: #D1FAE5 !important; font-size: 1.2rem !important; font-weight: 900 !important; border-radius: 6px; padding: 6px 10px; border: 1px solid #10B981; }
    .zero-val { color: #FFFFFF !important; font-size: 1.1rem !important; }
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

# HTML 數值格式化工具
def render_perf_cell(val):
    if pd.isna(val) or val is None:
        return '<span class="zero-val">N/A</span>'
    elif val > 0:
        return f'<span class="pos-val">+{val:.2f}%</span>'
    elif val < 0:
        return f'<span class="neg-val">{val:.2f}%</span>'
    else:
        return f'<span class="zero-val">0.00%</span>'

with st.spinner('⚡ 正在載入高清晰金融數據...'):
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
                <th class="th-bench">代號</th>
                <th class="th-bench">最新價</th>
                <th class="th-bench">5日績效</th>
                <th class="th-bench">20日績效</th>
                <th class="th-bench">60日績效</th>
            </tr>
        </thead>
        <tbody>
    """
    for _, row in bench_df.iterrows():
        html_code += f"""
        <tr>
            <td><span class="badge-symbol">{row['ETF代號']}</span></td>
            <td><span class="badge-price">${row['最新價']:.2f}</span></td>
            <td>{render_perf_cell(row['5日績效'])}</td>
            <td>{render_perf_cell(row['20日績效'])}</td>
            <td>{render_perf_cell(row['60日績效'])}</td>
        </tr>
        """
    html_code += "</tbody></table>"
    st.markdown(html_code, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ----------------------------------------------------
# 下方：三大天期獨立排行榜 (HTML 高對比渲染)
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
                    <th class="th-5d" colspan="4">🔥 近 5 日績效排名</th>
                </tr>
                <tr>
                    <th class="th-5d">名次</th>
                    <th class="th-5d">代號</th>
                    <th class="th-5d">最新價</th>
                    <th class="th-5d">報酬率</th>
                </tr>
            </thead>
            <tbody>
        """
        for idx, row in df_5d.iterrows():
            html_5d += f"""
            <tr>
                <td><span class="badge-rank">N°{idx+1}</span></td>
                <td><span class="badge-symbol">{row['ETF代號']}</span></td>
                <td><span class="badge-price">${row['最新價']:.2f}</span></td>
                <td>{render_perf_cell(row['5日績效'])}</td>
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
                    <th class="th-20d" colspan="4">👑 近 20 日績效排名</th>
                </tr>
                <tr>
                    <th class="th-20d">名次</th>
                    <th class="th-20d">代號</th>
                    <th class="th-20d">最新價</th>
                    <th class="th-20d">報酬率</th>
                </tr>
            </thead>
            <tbody>
        """
        for idx, row in df_20d.iterrows():
            html_20d += f"""
            <tr>
                <td><span class="badge-rank">N°{idx+1}</span></td>
                <td><span class="badge-symbol">{row['ETF代號']}</span></td>
                <td><span class="badge-price">${row['最新價']:.2f}</span></td>
                <td>{render_perf_cell(row['20日績效'])}</td>
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
                    <th class="th-60d" colspan="4">🚀 近 60 日績效排名</th>
                </tr>
                <tr>
                    <th class="th-60d">名次</th>
                    <th class="th-60d">代號</th>
                    <th class="th-60d">最新價</th>
                    <th class="th-60d">報酬率</th>
                </tr>
            </thead>
            <tbody>
        """
        for idx, row in df_60d.iterrows():
            html_60d += f"""
            <tr>
                <td><span class="badge-rank">N°{idx+1}</span></td>
                <td><span class="badge-symbol">{row['ETF代號']}</span></td>
                <td><span class="badge-price">${row['最新價']:.2f}</span></td>
                <td>{render_perf_cell(row['60日績效'])}</td>
            </tr>
            """
        html_60d += "</tbody></table>"
        st.markdown(html_60d, unsafe_allow_html=True)

else:
    st.error("⚠️ 資料載入失敗，請確認網路連線。")

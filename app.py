import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
from datetime import datetime

# ==========================================
# 1. 頁面設定
# ==========================================
st.set_page_config(
    page_title="台股主動式 ETF 績效排行榜",
    page_icon="📈",
    layout="wide"
)

st.title("📈 台股主動式 ETF 績效排行榜")
st.caption("自動即時計算 5 日 (週)、20 日 (月)、60 日 (季) 還原報酬率")

# ==========================================
# 2. 追蹤清單設定 (可在此自由新增或修改代號)
# ==========================================
# 註：台股上市股票/ETF 需在代號後加上 .TW，上櫃加上 .TWO
DEFAULT_ETF_MAP = {
    "00981A.TW": "主動式台股增長",
    "00992A.TW": "主動式科技創新",
    "00999A.TW": "主動式高股息",
    "0050.TW": "元大台灣50 (對照組)",
    "0056.TW": "元大高股息 (對照組)",
    "00878.TW": "國泰永續高股息 (對照組)"
}

# ==========================================
# 3. 數據抓取與計算邏輯 (快取 1 小時以利效能)
# ==========================================
@st.cache_data(ttl=3600)
def fetch_and_calculate(etf_dict):
    records = []
    raw_history = {}

    for ticker, name in etf_dict.items():
        try:
            # 抓取近 4 個月數據以確保足夠計算 60 個交易日
            df = yf.download(ticker, period="4m", progress=False)
            
            # 修正 yfinance MultiIndex 欄位結構
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            
            if len(df) < 61:
                continue

            # 優先採用還原收盤價 (Adj Close)，若無則使用 Close
            close_series = df['Adj Close'] if 'Adj Close' in df else df['Close']
            raw_history[ticker] = close_series

            latest_price = float(close_series.iloc[-1])
            p_5d = float(close_series.iloc[-6])
            p_20d = float(close_series.iloc[-21])
            p_60d = float(close_series.iloc[-61])

            # 計算報酬率 (%)
            ret_5d = ((latest_price - p_5d) / p_5d) * 100
            ret_20d = ((latest_price - p_20d) / p_20d) * 100
            ret_60d = ((latest_price - p_60d) / p_60d) * 100

            records.append({
                "代號": ticker.replace(".TW", "").replace(".TWO", ""),
                "名稱": name,
                "最新價": round(latest_price, 2),
                "5日報酬 (%)": round(ret_5d, 2),
                "20日報酬 (%)": round(ret_20d, 2),
                "60日報酬 (%)": round(ret_60d, 2),
                "_raw_ticker": ticker
            })
        except Exception as e:
            st.error(f"抓取 {ticker} 失敗: {e}")

    return pd.DataFrame(records), raw_history

# 載入資料
with st.spinner("更新數據中，請稍候..."):
    df_perf, raw_data = fetch_and_calculate(DEFAULT_ETF_MAP)

# ==========================================
# 4. 前端介面與表格顯示
# ==========================================
if not df_perf.empty:
    # 側邊欄控制項
    st.sidebar.header("⚙️ 篩選與設定")
    search_keyword = st.sidebar.text_input("搜尋 ETF 代號或名稱", "")
    
    # 關鍵字過濾
    if search_keyword:
        df_perf = df_perf[
            df_perf['代號'].str.contains(search_keyword, case=False) |
            df_perf['名稱'].str.contains(search_keyword, case=False)
        ]

    # 台股配色渲染 (正數為紅、負數為綠)
    def style_returns(val):
        if isinstance(val, (int, float)):
            if val > 0:
                return 'color: #ff3b30; font-weight: bold;'
            elif val < 0:
                return 'color: #34c759; font-weight: bold;'
        return ''

    # 隱藏內部屬性後進行表格格式化
    display_df = df_perf.drop(columns=["_raw_ticker"])
    
    styled_df = display_df.style\
        .map(style_returns, subset=["5日報酬 (%)", "20日報酬 (%)", "60日報酬 (%)"])\
        .format({"最新價": "{:.2f}", "5日報酬 (%)": "{:+.2f}%", "20日報酬 (%)": "{:+.2f}%", "60日報酬 (%)": "{:+.2f}%"})

    st.subheader("📊 績效排名表")
    st.dataframe(
        styled_df,
        use_container_width=True,
        height=300
    )

    # ==========================================
    # 5. 單一 ETF 圖表分析
    # ==========================================
    st.divider()
    st.subheader("📈 個股走勢圖分析")
    
    selected_name = st.selectbox(
        "選擇要檢視的 ETF",
        options=df_perf["名稱"].tolist()
    )

    selected_row = df_perf[df_perf["名稱"] == selected_name].iloc[0]
    selected_ticker = selected_row["_raw_ticker"]
    history_series = raw_data[selected_ticker]

    fig = px.line(
        history_series,
        x=history_series.index,
        y=history_series.values,
        title=f"{selected_name} ({selected_row['代號']}) 近期走勢圖",
        labels={"x": "日期", "y": "價格 (元)"}
    )
    fig.update_traces(line_color="#0066cc", line_width=2)
    st.plotly_chart(fig, use_container_width=True)

else:
    st.warning("查無數據，請確認網路連線或代號設定。")

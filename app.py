import streamlit as st
import yfinance as yf
import pandas as pd

# 設定網頁標題與寬度
st.set_page_config(page_title="台股主動式 ETF 績效榜", layout="wide")

st.title("📊 台股主動式 ETF 績效排行榜")
st.write("自動抓取最新數據，計算近 5日、20日、60日 報酬率。")

# 1. 定義台股主動式 ETF 清單 (可自由增減代號)
ETF_LIST = ["00980A.TW", "00981A.TW", "00982A.TW", "00400A.TW"]

# 2. 抓取並計算資料
@st.cache_data(ttl=3600)  # 快取 1 小時，避免頻繁發送 API 請求
def load_etf_data():
    results = []
    for symbol in ETF_LIST:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="6m") # 抓 6 個月歷史日 K
        
        if len(df) >= 61:
            latest = df['Close'].iloc[-1]
            p_5d = df['Close'].iloc[-6]
            p_20d = df['Close'].iloc[-21]
            p_60d = df['Close'].iloc[-61]
            
            # 計算報酬率 %
            r5 = round(((latest - p_5d) / p_5d) * 100, 2)
            r20 = round(((latest - p_20d) / p_20d) * 100, 2)
            r60 = round(((latest - p_60d) / p_60d) * 100, 2)
            
            results.append({
                "ETF 代號": symbol.replace(".TW", ""),
                "最新價 (元)": round(latest, 2),
                "5日績效 (%)": r5,
                "20日績效 (%)": r20,
                "60日績效 (%)": r60
            })
    return pd.DataFrame(results)

# 顯示載入中動畫
with st.spinner('正在計算最新 ETF 績效...'):
    data = load_etf_data()

# 3. 畫面元件：選擇排序方式
sort_option = st.selectbox(
    "請選擇排序依據：",
    ("20日績效 (%)", "5日績效 (%)", "60日績效 (%)")
)

# 排序並顯示互動表格
sorted_data = data.sort_values(by=sort_option, ascending=False)

# 渲染表格 (會根據正負值自動顯示顏色/樣式)
st.dataframe(
    sorted_data,
    use_container_width=True,
    hide_index=True
)
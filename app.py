import streamlit as st
import requests
import pandas as pd
import datetime

st.set_page_config(page_title="台股主動式 ETF 績效榜", layout="wide")

st.title("📊 台股主動式 ETF 績效排行榜")
st.write("資料來源：台灣證券交易所 (TWSE) 官方 API")

# 1. 填入你想追蹤的台股主動式 ETF 清單 (只需寫代號，例如 00980A)
ETF_LIST = ["00980A", "00981A", "00982A", "00400A", "0050"]

@st.cache_data(ttl=3600)  # 快取 1 小時
def get_twse_data():
    # 取得近半年（180天）的日期範圍
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=180)
    
    start_str = start_date.strftime("%Y%m%d")
    end_str = end_date.strftime("%Y%m%d")

    results = []
    
    for symbol in ETF_LIST:
        try:
            # 呼叫證交所歷史收盤價 API
            url = f"https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL"
            # 備用官方路徑：抓取個股近期成交資訊
            response = requests.get(f"https://www.twse.com.tw/rwd/zh/afterTrading/STOCK_DAY?date={end_str}&stockNo={symbol}&response=json")
            data = response.json()
            
            if data.get("stat") == "OK" and "data" in data:
                raw_data = data["data"]
                # 提取日期與收盤價
                prices = []
                for row in raw_data:
                    # 清除字串中的逗號，轉為浮點數
                    price_str = row[6].replace(",", "")
                    try:
                        prices.append(float(price_str))
                    except ValueError:
                        continue
                
                # 確保至少有 6 天資料（計算5日績效）
                if len(prices) >= 6:
                    latest = prices[-1]
                    p_5d = prices[-6]
                    r5 = round(((latest - p_5d) / p_5d) * 100, 2)
                    
                    r20 = round(((latest - prices[-21]) / prices[-21]) * 100, 2) if len(prices) >= 21 else None
                    r60 = round(((latest - prices[-61]) / prices[-61]) * 100, 2) if len(prices) >= 61 else None
                    
                    results.append({
                        "ETF 代號": symbol,
                        "最新價 (元)": round(latest, 2),
                        "5日績效 (%)": r5,
                        "20日績效 (%)": r20,
                        "60日績效 (%)": r60
                    })
        except Exception:
            continue
            
    return pd.DataFrame(results)

with st.spinner('正在從證交所讀取最新數據...'):
    data = get_twse_data()

# 顯示表格與排序
if not data.empty:
    sort_option = st.selectbox(
        "請選擇排序依據：",
        ("5日績效 (%)", "20日績效 (%)", "60日績效 (%)")
    )
    
    sorted_data = data.sort_values(by=sort_option, ascending=False)
    
    st.dataframe(
        sorted_data,
        use_container_width=True,
        hide_index=True
    )
else:
    st.warning("⚠️ 證交所 API 響應延遲或今日非交易日，請稍後再試。")

import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="台股主動式 ETF 績效榜", layout="wide")

st.title("📊 台股主動式 ETF 績效排行榜")
st.write("資料來源：FinMind 台股歷史資料 API")

# 1. 填入你想追蹤的台股主動式 ETF 清單 (只需寫數字與字母，例如 00980A)
ETF_LIST = ["00980A", "00981A", "00982A", "00400A", "0050"]

@st.cache_data(ttl=3600)  # 快取 1 小時，避免過度呼叫
def load_etf_data_finmind():
    results = []
    
    # 計算近 120 天的日期範圍（確保扣除例假日後有足夠的 60 個交易日）
    today = datetime.today()
    start_date = (today - timedelta(days=120)).strftime("%Y-%m-%d")
    
    for symbol in ETF_LIST:
        try:
            url = f"https://api.finmindtrade.com/api/v4/data?dataset=TaiwanStockPrice&data_id={symbol}&start_date={start_date}"
            res = requests.get(url)
            data = res.json()
            
            if data.get("msg") == "success" and len(data.get("data", [])) >= 6:
                df = pd.DataFrame(data["data"])
                prices = df['close'].tolist()
                
                latest = prices[-1]
                
                # 計算 5日績效
                p_5d = prices[-6]
                r5 = round(((latest - p_5d) / p_5d) * 100, 2)
                
                # 計算 20日績效
                r20 = round(((latest - prices[-21]) / prices[-21]) * 100, 2) if len(prices) >= 21 else None
                
                # 計算 60日績效
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

with st.spinner('正在從 FinMind 取得近 120 天歷史股價...'):
    data = load_etf_data_finmind()

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
    st.error("⚠️ 資料抓取失敗，請確認網路連線或 ETF 代號。")

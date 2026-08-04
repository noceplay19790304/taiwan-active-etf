import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="台股主動式 ETF 績效榜", layout="wide")

st.title("📊 台股主動式 ETF 績效排行榜")
st.write("自動抓取最新數據，計算近 5日、20日、60日 報酬率。")

# 台股主動式 ETF 清單 (可自由替換或新增代號)
ETF_LIST = ["00980A.TW", "00981A.TW", "00982A.TW", "00400A.TW", "0050.TW"]

@st.cache_data(ttl=3600)
def load_etf_data():
    results = []
    for symbol in ETF_LIST:
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period="6m")
            
            # 必須至少有 6 天資料才能算出 5日績效
            if len(df) >= 6:
                latest = df['Close'].iloc[-1]
                
                # 計算 5日績效
                p_5d = df['Close'].iloc[-6]
                r5 = round(((latest - p_5d) / p_5d) * 100, 2)
                
                # 計算 20日績效 (若天數不足給 None)
                if len(df) >= 21:
                    p_20d = df['Close'].iloc[-21]
                    r20 = round(((latest - p_20d) / p_20d) * 100, 2)
                else:
                    r20 = None
                
                # 計算 60日績效 (若天數不足給 None)
                if len(df) >= 61:
                    p_60d = df['Close'].iloc[-61]
                    r60 = round(((latest - p_60d) / p_60d) * 100, 2)
                else:
                    r60 = None
                
                results.append({
                    "ETF 代號": symbol.replace(".TW", ""),
                    "最新價 (元)": round(latest, 2),
                    "5日績效 (%)": r5,
                    "20日績效 (%)": r20,
                    "60日績效 (%)": r60
                })
        except Exception as e:
            continue
            
    return pd.DataFrame(results)

with st.spinner('正在抓取最新 ETF 數據...'):
    data = load_etf_data()

# 安全檢查：確保抓得到資料才進行排序與繪製
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
    st.warning("⚠️ 目前抓取不到資料，請檢查 ETF 代號是否正確或 Yahoo Finance 是否暫時無資料。")

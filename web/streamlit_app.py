import json, os, time
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Attack Map (GeoLite2)", layout="wide")
st.title("🌍 Attack Map (GeoLite2 only)")

EVENTS_PATH = os.path.join("web", "events.json")

@st.cache_data(ttl=5)
def load_events():
    if not os.path.exists(EVENTS_PATH):
        return pd.DataFrame(columns=["lat","lon","ip","port","ts","country","city","label"])
    with open(EVENTS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    df = pd.DataFrame(data)
    # 결측 처리
    for col in ["lat","lon"]:
        if col not in df.columns: df[col] = None
    return df.dropna(subset=["lat","lon"])

df = load_events()

left, right = st.columns([2,1])
with left:
    st.map(df[["lat","lon"]], latitude="lat", longitude="lon", zoom=1)
with right:
    st.subheader("Recent Events")
    st.caption(f"{len(df)} events • last refresh: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    if not df.empty:
        st.dataframe(df.sort_values("ts", ascending=False), height=500)
    else:
        st.info("events.json에 데이터가 없어요. 먼저 IP → 좌표 변환 스크립트를 실행해 주세요.")

st.divider()
st.caption("This product includes GeoLite2 Data created by MaxMind.")

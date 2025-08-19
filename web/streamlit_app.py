import json, os, time
import pandas as pd
import streamlit as st
import pydeck as pdk

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
    for col in ["lat","lon"]:
        if col not in df.columns: df[col] = None
    df = df.dropna(subset=["lat","lon"])

    # 목적지 좌표 임의 추가 (서울 허니팟)
    dst_lat = 37.5665
    dst_lon = 126.9780
    df["dst_lat"] = dst_lat
    df["dst_lon"] = dst_lon

    return df

df = load_events()

left, right = st.columns([2,1])
with left:
    # ArcLayer로 공격 흐름 시각화
    layer = pdk.Layer(
        "ArcLayer",
        df,
        get_source_position=["lon", "lat"],
        get_target_position=["dst_lon", "dst_lat"],
        get_source_color=[255, 0, 0],
        get_target_color=[0, 0, 255],
        get_width=5,
        pickable=True
    )
    view_state = pdk.ViewState(latitude=37.5665, longitude=126.9780, zoom=1.5)
    st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state))

with right:
    st.subheader("Recent Events")
    st.caption(f"{len(df)} events • last refresh: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    if not df.empty:
        st.dataframe(df.sort_values("ts", ascending=False), height=500)
    else:
        st.info("events.json에 데이터가 없어요. 먼저 IP → 좌표 변환 스크립트를 실행해 주세요.")

st.divider()
st.caption("This product includes GeoLite2 Data created by MaxMind.")
        st.info("events.json에 데이터가 없어요. 먼저 IP → 좌표 변환 스크립트를 실행해 주세요.")

st.divider()
st.caption("This product includes GeoLite2 Data created by MaxMind.")

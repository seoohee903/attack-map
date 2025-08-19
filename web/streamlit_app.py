import json, os, time
import pandas as pd
import streamlit as st
import pydeck as pdk
from datetime import datetime, timedelta

st.set_page_config(page_title="Attack Map (GeoLite2)", layout="wide")
st.title("🌍 Attack Map (GeoLite2 only)")

EVENTS_PATH = os.path.join("web", "events.json")

@st.cache_data(ttl=5)
def load_events():
    if not os.path.exists(EVENTS_PATH):
        return pd.DataFrame(columns=["lat", "lon", "src_ip", "port", "ts", "country", "label", "severity"])
    with open(EVENTS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    df = pd.DataFrame(data)

    # 결측 처리
    for col in ["lat", "lon"]:
        if col not in df.columns:
            df[col] = None
    df = df.dropna(subset=["lat", "lon"])

    # 목적지 좌표 임의 추가 (서울 허니팟)
    dst_lat = 37.5665
    dst_lon = 126.9780
    df["dst_lat"] = dst_lat
    df["dst_lon"] = dst_lon

    # 최근 30초 이내 이벤트만 필터링
    now = datetime.utcnow()
    df["ts"] = pd.to_datetime(df["ts"], errors="coerce")
    df = df[df["ts"] > now - timedelta(seconds=30)]

    return df

df = load_events()

# 색상 매핑: 공격 유형별 RGB
LABEL_COLORS = {
    "bruteforce": [255, 0, 0],
    "malware-drop": [0, 255, 0],
    "scanner": [0, 0, 255],
    "miner": [255, 255, 0],
    "worm": [255, 0, 255]
}

# 색상과 굵기 컬럼 생성
df["color"] = df["label"].map(LABEL_COLORS).fillna([128, 128, 128])
df["width"] = df["severity"].clip(1, 10)

left, right = st.columns([2, 1])
with left:
    # ArcLayer로 공격 흐름 시각화
    layer = pdk.Layer(
        "ArcLayer",
        df,
        get_source_position=["lon", "lat"],
        get_target_position=["dst_lon", "dst_lat"],
        get_source_color="color",
        get_target_color="color",
        get_width="width",
        pickable=True,
        auto_highlight=True
    )

    tooltip = {
        "html": "<b>IP:</b> {src_ip}<br><b>Label:</b> {label}<br><b>Severity:</b> {severity}",
        "style": {"backgroundColor": "white", "color": "black"}
    }

    view_state = pdk.ViewState(latitude=37.5665, longitude=126.9780, zoom=1.5)
    st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip=tooltip))

with right:
    st.subheader("Recent Events")
    st.caption(f"{len(df)} events • last refresh: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    if not df.empty:
        st.dataframe(df.sort_values("ts", ascending=False), height=500)
    else:
        st.info("최근 30초 이내의 이벤트가 없습니다. 잠시 후 다시 확인해 주세요.")

st.divider()
st.caption("This product includes GeoLite2 Data created by MaxMind.")

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import time
from datetime import datetime

# 1. 初始化状态
if 'lang' not in st.session_state: st.session_state.lang = '中文'
if 'blackout' not in st.session_state: st.session_state.blackout = False
if 'chart_data' not in st.session_state:
    st.session_state.chart_data = pd.DataFrame([50.0] * 30, columns=['Hz'])

# 2. 语言字典
texts = {
    '中文': {
        'title': "智能 EMS 实时指挥终端",
        'grid_f': "实时频率 (Hz)", 'amp': "母排电流 (A)", 'soc': "储能状态 (SOC)",
        'btn_sim': "🚨 模拟全船失电", 'btn_reset': "🔄 恢复系统",
        'status': "运行状态", 'safe': "运行正常", 'danger': "紧急切换中",
        'lang_btn': "English Version"
    },
    'English': {
        'title': "Smart EMS Live Command",
        'grid_f': "Live Frequency (Hz)", 'amp': "Bus Current (A)", 'soc': "Energy SOC",
        'btn_sim': "🚨 SIMULATE BLACKOUT", 'btn_reset': "🔄 RECOVER SYSTEM",
        'status': "Status", 'safe': "OPERATIONAL", 'danger': "EMERGENCY SWITCH",
        'lang_btn': "中文版本"
    }
}
t = texts[st.session_state.lang]

st.set_page_config(page_title=t['title'], layout="wide")

# 3. 侧边栏：语言与学校信息
with st.sidebar:
    st.markdown(f"### 🏫 {'山东理工职业学院' if st.session_state.lang=='中文' else 'Shandong Polytechnic'}")
    if st.button(t['lang_btn'], use_container_width=True):
        st.session_state.lang = 'English' if st.session_state.lang == '中文' else '中文'
        st.rerun()
    st.divider()
    st.info("Project: Heterogeneous Compensation EESS")

# 4. 主界面布局
st.title(t['title'])

# 创建实时更新的容器
metric_row = st.empty()
chart_placeholder = st.empty()

# 5. 交互按钮
if not st.session_state.blackout:
    if st.button(t['btn_sim'], use_container_width=True, type="primary"):
        st.session_state.blackout = True
        st.balloons()
else:
    if st.button(t['btn_reset'], use_container_width=True):
        st.session_state.blackout = False
        st.session_state.chart_data = pd.DataFrame([50.0] * 30, columns=['Hz'])

# 6. 核心动态实时循环
# 我们使用一个 while True 循环来模拟实时刷新（在比赛演示时效果极佳）
while True:
    # --- 数据模拟算法 ---
    if not st.session_state.blackout:
        new_freq = 50.0 + np.random.uniform(-0.05, 0.05)
        new_amp = 1200 + np.random.uniform(-10, 10)
        status_color = "normal"
    else:
        # 失电瞬间频率暴跌，然后由 EMS 拉回
        new_freq = 49.2 + np.random.uniform(-0.1, 0.1)
        new_amp = 0 + np.random.uniform(0, 5) # 主电源消失，只有应急电流
        status_color = "inverse"

    # 更新历史数据用于画图
    new_row = pd.DataFrame([[new_freq]], columns=['Hz'])
    st.session_state.chart_data = pd.concat([st.session_state.chart_data, new_row], ignore_index=True).iloc[-30:]

    # --- 渲染实时指标 ---
    with metric_row.container():
        c1, c2, c3 = st.columns(3)
        c1.metric(t['grid_f'], f"{new_freq:.2f}", f"{new_freq-50:.3f}")
        c2.metric(t['amp'], f"{new_amp:.1f} A", "-5.2%" if not st.session_state.blackout else "-100%")
        if st.session_state.blackout:
            c3.error(f"⚠️ {t['danger']}")
        else:
            c3.success(f"✅ {t['safe']}")

    # --- 渲染实时折线图 ---
    with chart_placeholder.container():
        st.line_chart(st.session_state.chart_data, height=300)

    # 稍微停顿一下，模拟采样率（0.5秒刷新一次）
    time.sleep(0.5)

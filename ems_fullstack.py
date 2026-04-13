import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime

# 1. 移动端优化配置
st.set_page_config(
    page_title="Smart Marine EMS",
    page_icon="⚓",
    layout="centered", # 手机端居中对齐更好看
    initial_sidebar_state="collapsed"
)

# 自定义 CSS：打造高科技暗黑模式卡片
st.markdown("""
    <style>
    .main { background-color: #050a10; }
    div[data-testid="stMetricValue"] { font-size: 24px; color: #00f2ff; }
    .stProgress > div > div > div > div { background-image: linear-gradient(to right, #00c6ff, #0072ff); }
    .vessel-card {
        background: rgba(255, 255, 255, 0.05);
        padding: 15px;
        border-radius: 15px;
        border-left: 5px solid #00f2ff;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# 2. 模拟核心数据
if 'alert' not in st.session_state: st.session_state.alert = False

# 3. 手机端顶部导航（使用 Tabs 模拟 App 底部菜单）
tab1, tab2, tab3 = st.tabs(["📊 实时监控", "🔋 能效中心", "🌍 全球任务"])

# --- TAB 1: 实时监控 (核心逻辑) ---
with tab1:
    st.title("EMS Live")
    
    # 紧急状态通知
    if st.session_state.alert:
        st.error("🆘 BLACKOUT DETECTED: Heterogeneous System Active!")
        if st.button("RESET SYSTEM", type="primary", use_container_width=True):
            st.session_state.alert = False
            st.rerun()
    
    # 卡片式数据看板
    m1, m2 = st.columns(2)
    with m1:
        st.metric("Grid Freq", "50.01 Hz", "Normal")
        st.metric("Bus Load", "64%", "-2%")
    with m2:
        st.metric("EESS Temp", "32.5°C", "Stable")
        st.metric("Fuel Saving", "12.4kg/h", "Eco Mode")

    # 动态曲线图
    st.subheader("Microgrid Stability")
    chart_data = pd.DataFrame(np.random.randn(20, 1), columns=['Frequency'])
    st.line_chart(chart_data, height=200)

    # 模拟触发按钮
    if not st.session_state.alert:
        if st.button("🚨 TEST BLACKOUT RESPONSE", use_container_width=True):
            st.session_state.alert = True
            st.balloons()
            st.rerun()

# --- TAB 2: 能效中心 (异构动力管理) ---
with tab2:
    st.subheader("Energy Storage & Health")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.write("**Battery A (Lifepo4)**")
        st.progress(85)
        st.caption("SOC: 85% | SOH: 98%")
    with col_b:
        st.write("**Battery B (Emergency)**")
        st.progress(100)
        st.caption("SOC: 100% | SOH: 100%")

    st.divider()
    
    st.subheader("Optimization Logic")
    st.toggle("Auto Load Shedding", value=True)
    st.toggle("SOLAS 0s Seamless Mode", value=True)
    
    # 策略分布图
    df = pd.DataFrame({"Source": ["Solar", "Battery", "Gen"], "Power": [30, 50, 20]})
    fig = px.pie(df, values='Power', names='Source', hole=.4, 
                 color_discrete_sequence=['#00f2ff', '#0072ff', '#555555'])
    fig.update_layout(margin=dict(l=20, r=20, t=20, b=20), height=250, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

# --- TAB 3: 全球任务 (针对达飞、中远海运等合作背景) ---
with tab3:
    st.subheader("Fleet Global Task")
    
    # 模拟任务卡片
    tasks = [
        {"vessel": "CMA CGM ANTOINE", "loc": "Suez Canal", "status": "Eco Cruising"},
        {"vessel": "COSCO SHIPPING", "loc": "Singapore Port", "status": "Charging"},
        {"vessel": "MAERSK ESSEN", "loc": "North Sea", "status": "Maintenance"}
    ]
    
    for t in tasks:
        st.markdown(f"""
        <div class="vessel-card">
            <b>🚢 {t['vessel']}</b><br>
            <small>📍 Location: {t['loc']}</small><br>
            <span style="color: #00f2ff;">● {t['status']}</span>
        </div>
        """, unsafe_allow_html=True)

# 4. 底部版权信息
st.divider()
st.caption("© 2026 Smart Marine Tech | Powered by Heterogeneous Compensation Algorithm")
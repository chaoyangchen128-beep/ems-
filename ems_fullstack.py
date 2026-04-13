import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import time

# 1. 初始化 Session State (状态管理)
if 'lang' not in st.session_state: st.session_state.lang = '中文'
if 'blackout' not in st.session_state: st.session_state.blackout = False

# 2. 中英文语境配置
texts = {
    '中文': {
        'title': "智能 EMS 智慧终端",
        'subtitle': "远洋船舶异构动力调度系统",
        'tab1': "实时监控", 'tab2': "能效分析", 'tab3': "系统设置",
        'grid_f': "电网频率", 'voltage': "主母排电压", 'soc': "电池荷电状态",
        'btn_sim': "🚨 模拟全船失电 (紧急)", 'btn_reset': "🔄 重置系统",
        'msg_safe': "SOLAS 状态: 合规", 'msg_crit': "SOLAS 缺口: 0s 补偿中",
        'log_start': "🟢 系统进入监测状态...",
        'log_err': "🔴 检测到动力真空！异构系统秒级切入...",
        'lang_btn': "English Version"
    },
    'English': {
        'title': "Smart EMS Terminal",
        'subtitle': "Marine Heterogeneous Power Dispatch",
        'tab1': "Live Monitor", 'tab2': "Energy Analysis", 'tab3': "Settings",
        'grid_f': "Grid Freq", 'voltage': "Bus Voltage", 'soc': "Battery SOC",
        'btn_sim': "🚨 SIMULATE BLACKOUT", 'btn_reset': "🔄 RESET SYSTEM",
        'msg_safe': "SOLAS: Compliant", 'msg_crit': "SOLAS Gap: 0s Compensating",
        'log_start': "🟢 System monitoring active...",
        'log_err': "🔴 Power Vacuum! Heterogeneous system triggered...",
        'lang_btn': "中文版本"
    }
}
t = texts[st.session_state.lang]

# 3. 页面配置与 CSS 动画增强
st.set_page_config(page_title=t['title'], layout="wide")

st.markdown(f"""
    <style>
    /* 全屏闪烁动画 */
    @keyframes shake {{ 0% {{ transform: translate(1px, 1px) rotate(0deg); }} 10% {{ transform: translate(-1px, -2px) rotate(-1deg); }} 20% {{ transform: translate(-3px, 0px) rotate(1deg); }} }}
    .stApp {{ background-color: #0a1118; color: white; }}
    .blackout-active {{ animation: shake 0.5s infinite; border: 5px solid red; }}
    .metric-card {{ background: rgba(255,255,255,0.05); padding: 20px; border-radius: 10px; border: 1px solid #1e3a5f; }}
    </style>
""", unsafe_allow_html=True)

# 4. 侧边栏：多页面切换与语言开关
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/ship.png")
    st.title("Control Center")
    
    # 语言切换按钮 (强反馈效果)
    if st.button(t['lang_btn'], use_container_width=True):
        st.session_state.lang = 'English' if st.session_state.lang == '中文' else '中文'
        st.rerun()
    
    st.divider()
    page = st.radio("Menu", [t['tab1'], t['tab2'], t['tab3']])

# 5. 核心逻辑渲染
if page == t['tab1']:
    st.title(t['title'])
    st.caption(t['subtitle'])

    # 顶部卡片
    c1, c2, c3 = st.columns(3)
    with c1: st.metric(t['grid_f'], "50.02 Hz", "Normal")
    with c2: st.metric(t['voltage'], "440.5 V", "Stable")
    with c3:
        if st.session_state.blackout:
            st.error(t['msg_crit'])
        else:
            st.success(t['msg_safe'])

    # 图表区
    chart_data = pd.DataFrame(np.random.randn(20, 1) * 0.1 + 50, columns=['Hz'])
    if st.session_state.blackout:
        chart_data.iloc[-5:] = 40.0 # 模拟跌落
    st.line_chart(chart_data)

    # 交互按钮
    st.divider()
    if not st.session_state.blackout:
        if st.button(t['btn_sim'], use_container_width=True, type="primary"):
            st.session_state.blackout = True
            st.toast("🚨 ALERT: Power Grid Failed!") # 弹出吐司提示
            st.balloons()
            st.rerun()
    else:
        if st.button(t['btn_reset'], use_container_width=True):
            st.session_state.blackout = False
            st.rerun()

elif page == t['tab2']:
    st.header(t['tab2'])
    # 模拟能效分布
    df = pd.DataFrame({'Source': ['Solar', 'ESS-A', 'ESS-B', 'Gen'], 'Value': [25, 45, 20, 10]})
    fig = px.pie(df, values='Value', names='Source', hole=0.5, template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)
    
    st.info("💡 Optimization Tip: Battery SOH is at 98.2%. Recommendation: Maintain discharge C-rate < 0.5C.")

else:
    st.header(t['tab3'])
    st.toggle("Auto-Mode (AI)")
    st.toggle("Cloud Sync")
    st.slider("Alarm Threshold (Hz)", 45.0, 55.0, 49.5)

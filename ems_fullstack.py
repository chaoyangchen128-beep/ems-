import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import time

# --- 1. 全局配置与状态初始化 ---
if 'lang' not in st.session_state: st.session_state.lang = '中文'
if 'blackout_stage' not in st.session_state: st.session_state.blackout_stage = "normal" # normal, danger, success
if 'page' not in st.session_state: st.session_state.page = "实时监控"

# 纯净语言字典
texts = {
    '中文': {
        'school': "山东理工职业学院", 'major': "轮机工程技术项目组",
        'm1': "实时监控", 'm2': "能效分析", 'm3': "系统设置",
        'f_label': "电网频率 (Hz)", 'v_label': "母排电压 (V)",
        'btn_sim': "🚨 模拟全船失电 (执行抢电)", 'btn_reset': "🔄 强制系统复位",
        'msg_safe': "✅ 运行状态：正常", 'msg_danger': "❌ 警告：正在执行抢电...", 'msg_success': "⚡ 抢电成功：异构动力介入",
        'lang_btn': "English", 'analysis_title': "电池组健康度 (SOH) 深度分析",
        'set_title': "EMS 系统参数配置", 'set_save': "应用更改",
        'set_conn': "设备通信状态", 'set_priority': "负载优先级调度",
        'set_cloud': "岸基数据实时同步 (达飞海运)", 'set_threshold': "抢电触发阈值 (Hz)"
    },
    'English': {
        'school': "Shandong Polytechnic", 'major': "Marine Engineering Tech Team",
        'm1': "Live Monitor", 'm2': "Energy Analysis", 'm3': "Settings",
        'f_label': "Grid Frequency (Hz)", 'v_label': "Bus Voltage (V)",
        'btn_sim': "🚨 SIMULATE BLACKOUT (EXECUTE)", 'btn_reset': "🔄 FORCE SYSTEM RESET",
        'msg_safe': "✅ Status: Operational", 'msg_danger': "❌ Warning: Competing...", 'msg_success': "⚡ Success: EESS Active",
        'lang_btn': "中文", 'analysis_title': "Battery SOH Deep Analysis",
        'set_title': "EMS System Configuration", 'set_save': "Apply Changes",
        'set_conn': "Device Connectivity", 'set_priority': "Load Priority Dispatch",
        'set_cloud': "Shore-based Sync (CMA CGM)", 'set_threshold': "Trigger Threshold (Hz)"
    }
}
t = texts[st.session_state.lang]

st.set_page_config(page_title="Marine EMS Pro", layout="wide")

# --- 2. 增强反馈 CSS (红闪 -> 绿屏 -> 恢复) ---
# 定义不同的动画背景
bg_style = ""
if st.session_state.blackout_stage == "danger":
    bg_style = "animation: flash-red 0.4s 3;" # 红闪 3 次
elif st.session_state.blackout_stage == "success":
    bg_style = "background-color: #d4edda; transition: 0.5s;" # 绿屏背景

st.markdown(f"""
    <style>
    .stApp {{ background-color: #ffffff; color: #112640; {bg_style} }}
    @keyframes flash-red {{
        0% {{ background-color: #ffffff; }}
        50% {{ background-color: #ffcccc; }}
        100% {{ background-color: #ffffff; }}
    }}
    .stButton>button:active {{ transform: scale(0.95); transition: 0.1s; }}
    div[data-testid="stMetricValue"] {{ 
        color: {"#d94111" if st.session_state.blackout_stage=="danger" else ("#28a745" if st.session_state.blackout_stage=="success" else "#008b8b")}; 
        font-weight: 800; 
    }}
    </style>
""", unsafe_allow_html=True)

# --- 3. 侧边栏 ---
with st.sidebar:
    st.markdown(f"### **{t['school']}**")
    st.caption(t['major'])
    st.divider()
    if st.button(f"🌐 {t['lang_btn']}", use_container_width=True):
        st.session_state.lang = 'English' if st.session_state.lang == '中文' else '中文'
        st.rerun()
    choice = st.radio("Menu", [t['m1'], t['m2'], t['m3']], label_visibility="collapsed")
    st.divider()
    st.image("https://img.icons8.com/ios-filled/100/112640/ship.png", width=60)

# --- 4. 页面内容 ---

# A. 实时监控页 (包含“抢电动作序列”)
if choice == t['m1']:
    st.title(f"⚓ {t['m1']}")
    m_area = st.empty()
    c_area = st.empty()

    # 抢电触发器
    if st.session_state.blackout_stage == "normal":
        if st.button(t['btn_sim'], use_container_width=True, type="primary"):
            # 步骤 1: 触发红色闪烁警报
            st.session_state.blackout_stage = "danger"
            st.rerun()
    else:
        if st.button(t['btn_reset'], use_container_width=True):
            st.session_state.blackout_stage = "normal"
            st.rerun()

    # 自动执行抢电成功序列
    if st.session_state.blackout_stage == "danger":
        time.sleep(1.2) # 模拟红闪 3 次的时间
        st.session_state.blackout_stage = "success"
        st.rerun()
    elif st.session_state.blackout_stage == "success":
        time.sleep(2.0) # 绿色保持时间
        st.session_state.blackout_stage = "normal"
        st.rerun()

    # 模拟数据
    while choice == t['m1']:
        if st.session_state.blackout_stage == "normal":
            f, v, msg = 50.0 + np.random.uniform(-0.02, 0.02), 440.0 + np.random.uniform(-1, 1), t['msg_safe']
        elif st.session_state.blackout_stage == "danger":
            f, v, msg = 48.5 + np.random.uniform(-0.2, 0.2), 380.0 + np.random.uniform(-10, 10), t['msg_danger']
        else:
            f, v, msg = 50.0 + np.random.uniform(-0.01, 0.01), 440.0, t['msg_success']

        with m_area.container():
            c1, c2, c3 = st.columns(3)
            c1.metric(t['f_label'], f"{f:.2f} Hz")
            c2.metric(t['v_label'], f"{v:.1f} V")
            if st.session_state.blackout_stage == "danger": c3.error(msg)
            elif st.session_state.blackout_stage == "success": c3.success(msg)
            else: c3.info(msg)
        
        df = pd.DataFrame(np.random.randn(20, 1)*0.02 + f, columns=["Live Data"])
        c_area.line_chart(df, height=250)
        time.sleep(0.5)
        if choice != t['m1'] or st.session_state.blackout_stage != "normal": break

# B. 能效分析页
elif choice == t['m2']:
    st.title(f"🔋 {t['analysis_title']}")
    st.plotly_chart(px.pie(pd.DataFrame({'C': ['A', 'B'], 'V': [70, 30]}), values='V', names='C', hole=0.5), use_container_width=True)

# C. 系统设置页 (功能大幅增强)
elif choice == t['m3']:
    st.title(f"⚙️ {t['set_title']}")
    with st.form("enhanced_settings"):
        st.write(f"### 📋 {t['set_priority']}")
        st.checkbox("Tier 1: 通讯与导航雷达 (Critical Navigation)", value=True)
        st.checkbox("Tier 2: 机舱应急照明 (Emergency Lighting)", value=True)
        st.checkbox("Tier 3: 生活区电力 (Accommodation)", value=False)
        
        st.divider()
        st.write(f"### 🌐 {t['set_conn']}")
        st.select_slider(t['set_threshold'], options=[48.5, 49.0, 49.5, 49.8], value=49.5)
        st.toggle(t['set_cloud'], value=True)
        
        if st.form_submit_button(t['set_save']):
            st.toast("Settings Applied! / 配置已生效！")

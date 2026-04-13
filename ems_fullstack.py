import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import time

# --- 1. 初始状态与全局配置 ---
if 'lang' not in st.session_state: st.session_state.lang = '中文'
if 'blackout' not in st.session_state: st.session_state.blackout = False
if 'page' not in st.session_state: st.session_state.page = "实时监控"
if 'threshold' not in st.session_state: st.session_state.threshold = 49.5

texts = {
    '中文': {
        'school': "山东理工职业学院",
        'major': "轮机工程技术项目组",
        'm1': "实时监控", 'm2': "能效分析", 'm3': "系统设置",
        'f_label': "电网频率", 'v_label': "母排电压", 'i_label': "负载电流",
        'btn_sim': "🚨 模拟全船失电", 'btn_reset': "🔄 恢复动力系统",
        'msg_safe': "✅ 运行状态：正常", 'msg_danger': "❌ 紧急：0s 异构补偿中",
        'lang_btn': "English", 'analysis_title': "电池组健康度 (SOH) 深度分析",
        'set_title': "控制参数设定", 'set_save': "保存设置"
    },
    'English': {
        'school': "Shandong Polytechnic",
        'major': "Marine Engineering Tech Team",
        'm1': "Live Monitor", 'm2': "Energy Analysis", 'm3': "Settings",
        'f_label': "Grid Freq", 'v_label': "Bus Voltage", 'i_label': "Load Current",
        'btn_sim': "🚨 SIMULATE BLACKOUT", 'btn_reset': "🔄 RECOVER POWER",
        'msg_safe': "✅ Status: Normal", 'msg_danger': "❌ Emergency: 0s Competing",
        'lang_btn': "中文", 'analysis_title': "Battery SOH Deep Analysis",
        'set_title': "Control Parameter Setup", 'set_save': "Save Settings"
    }
}
t = texts[st.session_state.lang]

st.set_page_config(page_title="Marine EMS Pro", layout="wide")

# --- 2. 全新统一色调 CSS (深海极客风) ---
st.markdown("""
    <style>
    /* 全局背景与文字基础色 */
    .stApp { background-color: #030d1a; color: #d8e8f8; }
    
    /* 侧边栏背景调整 */
    [data-testid="stSidebar"] { background-color: #061426; border-right: 1px solid #112640; }
    
    /* 统一大数字（Metric）颜色并增加霓虹发光 */
    div[data-testid="stMetricValue"] { 
        color: #00f2ff; 
        text-shadow: 0 0 15px rgba(0, 242, 255, 0.4); 
        font-weight: 700; 
    }
    
    /* 统一所有按钮样式为暗色线框风 */
    .stButton>button { 
        background-color: transparent; 
        color: #00f2ff; 
        border: 1px solid #00f2ff; 
        border-radius: 6px;
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        background-color: rgba(0, 242, 255, 0.1);
        box-shadow: 0 0 10px rgba(0, 242, 255, 0.3);
    }
    .stButton>button:active { transform: scale(0.95); }
    
    /* 针对主要警报按钮的特殊覆盖（红色警报风） */
    button[kind="primary"] { 
        border-color: #ff4b4b !important; 
        color: #ff4b4b !important; 
        background-color: transparent !important;
    }
    button[kind="primary"]:hover {
        background-color: rgba(255, 75, 75, 0.1) !important;
        box-shadow: 0 0 15px rgba(255, 75, 75, 0.4) !important;
    }
    
    /* 顶部空白微调 */
    .block-container { padding-top: 2rem; }
    </style>
""", unsafe_allow_html=True)

# --- 3. 侧边栏 ---
with st.sidebar:
    st.markdown(f"### 🏫 {t['school']}")
    st.caption(t['major'])
    st.divider()
    
    if st.button(f"🌐 {t['lang_btn']}", use_container_width=True):
        st.session_state.lang = 'English' if st.session_state.lang == '中文' else '中文'
        st.rerun()
    
    menu_options = [t['m1'], t['m2'], t['m3']]
    st.session_state.page = st.radio("Menu", menu_options, label_visibility="collapsed")
    
    st.divider()
    # 核心修改：使用精确色值匹配的单色航海图标
    st.image("https://img.icons8.com/ios-filled/100/00f2ff/ship.png", width=60)

# --- 4. 页面内容分发 ---

if st.session_state.page == t['m1']:
    st.title(f"⚓ {t['m1']}")
    
    m_row = st.empty()
    c_placeholder = st.empty()

    if not st.session_state.blackout:
        if st.button(t['btn_sim'], use_container_width=True, type="primary"):
            st.session_state.blackout = True
            st.rerun()
    else:
        if st.button(t['btn_reset'], use_container_width=True):
            st.session_state.blackout = False
            st.rerun()

    while st.session_state.page == t['m1']:
        freq = 50.0 + np.random.uniform(-0.02, 0.02) if not st.session_state.blackout else st.session_state.threshold - 0.5
        volts = 440 + np.random.uniform(-2, 2) if not st.session_state.blackout else 0.5
        
        with m_row.container():
            col1, col2, col3 = st.columns(3)
            col1.metric(t['f_label'], f"{freq:.2f} Hz", f"{freq-50:.3f}")
            col2.metric(t['v_label'], f"{volts:.1f} V", "-100%" if st.session_state.blackout else "Stable")
            if st.session_state.blackout:
                col3.error(t['msg_danger'])
            else:
                col3.success(t['msg_safe'])
        
        chart_data = pd.DataFrame(np.random.randn(20, 1)*0.05 + freq, columns=['Hz'])
        c_placeholder.line_chart(chart_data, height=250)
        
        time.sleep(0.8)
        if st.session_state.page != t['m1']: break 

elif st.session_state.page == t['m2']:
    st.title(f"🔋 {t['analysis_title']}")
    
    b_type = st.selectbox("Select Battery Pack", ["ESS-01 (Lithium)", "ESS-02 (Emergency Bank)"])
    
    col_l, col_r = st.columns([2, 1])
    with col_l:
        df = pd.DataFrame({'Component': ['Anode', 'Cathode', 'Electrolyte'], 'Health': [95, 88, 92]})
        # 核心修改：强制 Plotly 图表使用主题色系，并融入透明背景
        fig = px.pie(df, values='Health', names='Component', hole=0.6)
        fig.update_traces(marker=dict(colors=['#00f2ff', '#0072ff', '#1e3a5f']))
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)', 
            font=dict(color='#d8e8f8'),
            margin=dict(t=20, b=20, l=20, r=20)
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col_r:
        st.metric("SOH (State of Health)", "98.2%", "Optimal")
        st.write("---")
        st.write("📋 **Maintenance Log:**")
        st.caption("2026-04-10: Cell Balancing Complete")
        st.caption("2026-04-12: Thermal Test Passed")

elif st.session_state.page == t['m3']:
    st.title(f"⚙️ {t['set_title']}")
    
    with st.form("settings_form"):
        new_freq = st.slider("Blackout Threshold (Hz)", 48.0, 49.9, st.session_state.threshold)
        st.toggle("AI Predictive Dispatch", value=True)
        st.toggle("Remote Cloud Sync (CMA CGM Server)", value=False)
        
        if st.form_submit_button(t['set_save']):
            st.session_state.threshold = new_freq
            st.success("Settings Saved! / 设置已保存！")

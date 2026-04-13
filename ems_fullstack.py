import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import time

# --- 1. 全局配置与状态初始化 ---
if 'lang' not in st.session_state: st.session_state.lang = '中文'
if 'blackout' not in st.session_state: st.session_state.blackout = False
if 'page' not in st.session_state: st.session_state.page = "实时监控"

# 绝对纯净的语言字典
texts = {
    '中文': {
        'school': "山东理工职业学院",
        'major': "轮机工程技术项目组",
        'm1': "实时监控", 'm2': "能效分析", 'm3': "系统设置",
        'f_label': "电网频率 (赫兹)", 'v_label': "母排电压 (伏特)", 'i_label': "负载电流 (安培)",
        'btn_sim': "🚨 模拟全船失电 (触发抢电)", 'btn_reset': "🔄 恢复动力系统",
        'msg_safe': "运行状态：正常", 'msg_danger': "紧急状态：异构补偿中",
        'lang_btn': "切换至英文界面", 'analysis_title': "电池组健康度深度分析",
        'set_title': "控制参数设定", 'set_save': "保存设置",
        'unit_v': "伏特", 'unit_h': "正常", 'unit_d': "危险"
    },
    'English': {
        'school': "Shandong Polytechnic",
        'major': "Marine Engineering Tech Team",
        'm1': "Live Monitor", 'm2': "Energy Analysis", 'm3': "Settings",
        'f_label': "Grid Frequency (Hz)", 'v_label': "Bus Voltage (V)", 'i_label': "Load Current (A)",
        'btn_sim': "🚨 SIMULATE BLACKOUT", 'btn_reset': "🔄 RECOVER POWER SYSTEM",
        'msg_safe': "Status: Operational", 'msg_danger': "Critical: Heterogeneous Competing",
        'lang_btn': "Switch to Chinese", 'analysis_title': "Battery SOH Deep Analysis",
        'set_title': "Control Parameter Setup", 'set_save': "Save Settings",
        'unit_v': "Volts", 'unit_h': "Healthy", 'unit_d': "Danger"
    }
}
t = texts[st.session_state.lang]

st.set_page_config(page_title="Marine EMS Pro", layout="wide")

# --- 2. 增强反馈 CSS (包含全屏报警闪烁与震动动画) ---
st.markdown(f"""
    <style>
    /* 全局字体与背景 */
    .stApp {{ background-color: #ffffff; color: #112640; }}
    
    /* 强力反馈：失电时的全屏红色脉冲闪烁 */
    {'.stApp { animation: flash-red 0.5s infinite; }' if st.session_state.blackout else ''}
    @keyframes flash-red {{
        0% {{ background-color: #ffffff; }}
        50% {{ background-color: #ffcccc; }}
        100% {{ background-color: #ffffff; }}
    }}

    /* 按钮点击震动效果 */
    .stButton>button:active {{
        animation: shake 0.2s;
        transform: scale(0.9);
    }}
    @keyframes shake {{
        0% {{ transform: translate(1px, 1px) rotate(0deg); }}
        20% {{ transform: translate(-1px, -2px) rotate(-1deg); }}
        60% {{ transform: translate(-3px, 1px) rotate(0deg); }}
        100% {{ transform: translate(1px, -1px) rotate(1deg); }}
    }}

    /* 指标卡片发光 */
    div[data-testid="stMetricValue"] {{
        color: {"#d94111" if st.session_state.blackout else "#008b8b"} !important;
        font-size: 2.5rem !important;
        font-weight: 800;
    }}
    </style>
""", unsafe_allow_html=True)

# --- 3. 侧边栏导航 ---
with st.sidebar:
    st.markdown(f"### **{t['school']}**")
    st.caption(t['major'])
    st.divider()
    
    if st.button(f"🌐 {t['lang_btn']}", use_container_width=True):
        st.session_state.lang = 'English' if st.session_state.lang == '中文' else '中文'
        st.rerun()
    
    # 动态映射菜单项，确保语言纯净
    menu_map = {t['m1']: "监控", t['m2']: "分析", t['m3']: "设置"}
    choice = st.radio("Menu", [t['m1'], t['m2'], t['m3']], label_visibility="collapsed")
    
    st.divider()
    # 适配色调的图标
    st.image("https://img.icons8.com/ios-filled/100/112640/ship.png", width=60)

# --- 4. 逻辑分发 ---

# A. 实时监控页 (包含强力反馈循环)
if choice == t['m1']:
    st.title(f"⚓ {t['m1']}")
    
    metric_area = st.empty()
    chart_area = st.empty()

    # 底部大型控制按钮
    if not st.session_state.blackout:
        if st.button(t['btn_sim'], use_container_width=True, type="primary"):
            st.session_state.blackout = True
            st.warning("!!! BLACKOUT DETECTED !!!" if st.session_state.lang == 'English' else "!!! 检测到全船失电 !!!")
            st.rerun()
    else:
        if st.button(t['btn_reset'], use_container_width=True):
            st.session_state.blackout = False
            st.success("SYSTEM RECOVERED" if st.session_state.lang == 'English' else "系统已恢复动力")
            st.rerun()

    # 模拟实时数据流
    while choice == t['m1']:
        # 数据生成逻辑
        if not st.session_state.blackout:
            f = 50.0 + np.random.uniform(-0.02, 0.02)
            v = 440.0 + np.random.uniform(-1, 1)
            status_msg = t['msg_safe']
        else:
            f = 49.2 + np.random.uniform(-0.1, 0.1)
            v = 0.5 + np.random.uniform(0, 0.5)
            status_msg = t['msg_danger']

        with metric_area.container():
            c1, c2, c3 = st.columns(3)
            c1.metric(t['f_label'], f"{f:.2f} Hz")
            c2.metric(t['v_label'], f"{v:.1f} {t['unit_v']}")
            if st.session_state.blackout:
                c3.error(status_msg)
            else:
                c3.success(status_msg)
        
        # 实时动态图
        df = pd.DataFrame(np.random.randn(25, 1)*0.03 + f, columns=[t['f_label']])
        chart_area.line_chart(df, height=250)
        
        time.sleep(0.6)
        # 实时检测页面是否切换，防止死循环卡死
        if choice != t['m1']: break

# B. 能效分析页
elif choice == t['m2']:
    st.title(f"🔋 {t['analysis_title']}")
    col_l, col_r = st.columns([2, 1])
    with col_l:
        labels = ['组分 A', '组分 B', '电解液'] if st.session_state.lang == '中文' else ['Part A', 'Part B', 'Electrolyte']
        df_pie = pd.DataFrame({'Comp': labels, 'Val': [95, 88, 92]})
        fig = px.pie(df_pie, values='Val', names='Comp', hole=0.6)
        fig.update_layout(paper_bgcolor='white', plot_bgcolor='white', font=dict(color='#112640'))
        st.plotly_chart(fig, use_container_width=True)
    with col_r:
        st.metric("SOH" if st.session_state.lang == 'English' else "健康度", "98.2%", t['unit_h'])

# C. 系统设置页
elif choice == t['m3']:
    st.title(f"⚙️ {t['set_title']}")
    with st.form("settings"):
        val = st.slider(t['f_label'], 48.0, 49.9, 49.5)
        if st.form_submit_button(t['set_save']):
            st.toast("Success!" if st.session_state.lang == 'English' else "保存成功！")

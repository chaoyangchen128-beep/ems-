import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import time
import sqlite3
from datetime import datetime
from typing import Dict, List

# ==========================================
# Module 1: 核心物理仿真模型 (Physics Simulation Models)
# ==========================================

class BatteryPack:
    """船舶异构储能电池包物理模型"""
    def __init__(self, capacity_kwh: float, initial_soc: float, internal_res: float):
        self.capacity = capacity_kwh
        self.soc = initial_soc
        self.soh = 100.0  # 健康度 State of Health
        self.voltage_base = 48.0
        self.internal_resistance = internal_res
        self.temperature = 25.0
        self.cycle_count = 0

    def simulate_discharge(self, current_amps: float, dt_seconds: float):
        """模拟放电过程及热量计算 (安时积分法)"""
        discharged_ah = (current_amps * (dt_seconds / 3600))
        soc_drop = (discharged_ah / (self.capacity * 1000 / self.voltage_base)) * 100
        self.soc = max(0.0, self.soc - soc_drop)
        
        # 焦耳定律发热模拟: Q = I^2 * R * t
        heat_generated = (current_amps ** 2) * self.internal_resistance * dt_seconds
        self.temperature += heat_generated * 0.0001 - 0.05 # 包含散热系数
        
        return self.soc, self.temperature

class SolarArray:
    """船用共形光伏阵列出力模型"""
    def __init__(self, max_power_kw: float, efficiency: float):
        self.max_power = max_power_kw
        self.efficiency = efficiency

    def get_realtime_power(self, irradiance: float, cloud_cover: float) -> float:
        """基于光照强度的实时功率计算"""
        base_power = self.max_power * (irradiance / 1000.0) * self.efficiency
        return max(0.0, base_power * (1.0 - cloud_cover))

# ==========================================
# Module 2: 控制算法核心 (Control Algorithms)
# ==========================================

class PIDController:
    """频率补偿 PID 核心控制器"""
    def __init__(self, kp: float, ki: float, kd: float):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.integral = 0.0
        self.prev_error = 0.0

    def compute(self, setpoint: float, process_variable: float, dt: float) -> float:
        """计算补偿输出量"""
        error = setpoint - process_variable
        self.integral += error * dt
        derivative = (error - self.prev_error) / dt if dt > 0 else 0.0
        output = (self.kp * error) + (self.ki * self.integral) + (self.kd * derivative)
        self.prev_error = error
        return output

# ==========================================
# Module 3: 数据持久化与日志 (Database & Logging)
# ==========================================

def init_db():
    """初始化 SQLite 数据库，用于软著展示数据存储能力"""
    conn = sqlite3.connect('marine_ems_logs.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS system_logs
                 (timestamp TEXT, event_type TEXT, freq REAL, soc REAL)''')
    conn.commit()
    conn.close()

def log_event(event_type: str, freq: float, soc: float):
    """记录关键事件到数据库"""
    conn = sqlite3.connect('marine_ems_logs.db')
    c = conn.cursor()
    c.execute("INSERT INTO system_logs VALUES (?, ?, ?, ?)",
              (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), event_type, freq, soc))
    conn.commit()
    conn.close()

# ==========================================
# Module 4: 终端 UI 与交互层 (Frontend Views)
# ==========================================

st.set_page_config(page_title="Marine EMS Pro", layout="wide")
init_db()

# --- 全局状态与实例初始化 ---
if 'lang' not in st.session_state: st.session_state.lang = '中文'
if 'blackout' not in st.session_state: st.session_state.blackout = False
if 'page' not in st.session_state: st.session_state.page = "系统概览"
if 'threshold' not in st.session_state: st.session_state.threshold = 49.5

# 初始化物理实体 (存放于 Session State 保持状态)
if 'battery_A' not in st.session_state: st.session_state.battery_A = BatteryPack(500, 85.0, 0.02)
if 'battery_B' not in st.session_state: st.session_state.battery_B = BatteryPack(200, 100.0, 0.01)
if 'pid_core' not in st.session_state: st.session_state.pid_core = PIDController(1.5, 0.1, 0.05)

# --- 字典与 CSS ---
texts = {
    '中文': {'m1': "系统概览", 'm2': "异构动力分析", 'm3': "运行日志与设置", 'btn_sim': "🚨 触发全船失电 (Blackout)"},
    'English': {'m1': "System Overview", 'm2': "Heterogeneous Power", 'm3': "Logs & Settings", 'btn_sim': "🚨 Trigger Blackout"}
}
t = texts[st.session_state.lang]

st.markdown("""
    <style>
    .stApp { background-color: #ffffff; color: #112640; }
    [data-testid="stSidebar"] { background-color: #f8f9fa; border-right: 1px solid #e9ecef; }
    div[data-testid="stMetricValue"] { color: #008b8b; font-weight: 800; }
    button[kind="primary"] { border-color: #d94111 !important; color: #d94111 !important; }
    </style>
""", unsafe_allow_html=True)

# --- 侧边栏 ---
with st.sidebar:
    st.markdown("### **山东理工职业学院**")
    st.caption("《向海借光》项目控制中枢 V1.0")
    st.divider()
    if st.button("🌐 Switch Language / 切换语言", use_container_width=True):
        st.session_state.lang = 'English' if st.session_state.lang == '中文' else '中文'
        st.rerun()
    st.session_state.page = st.radio("Menu", [t['m1'], t['m2'], t['m3']], label_visibility="collapsed")

# --- 路由: 系统概览 (带算法补偿模拟) ---
if st.session_state.page == t['m1']:
    st.title(f"⚓ {t['m1']}")
    m_row, c_placeholder = st.empty(), st.empty()

    if not st.session_state.blackout:
        if st.button(t['btn_sim'], type="primary"):
            st.session_state.blackout = True
            log_event("BLACKOUT_TRIGGERED", 45.0, st.session_state.battery_B.soc)
            st.rerun()
    else:
        if st.button("🔄 System Reset / 系统复位"):
            st.session_state.blackout = False
            log_event("SYSTEM_RESET", 50.0, st.session_state.battery_B.soc)
            st.rerun()

    while st.session_state.page == t['m1']:
        # 获取当前时间步
        dt = 0.5 
        
        if not st.session_state.blackout:
            freq = 50.0 + np.random.uniform(-0.02, 0.02)
            volts = 440 + np.random.uniform(-1, 1)
            comp_power = 0.0
        else:
            # PID 算法介入模拟 0s 抢电
            raw_freq_drop = 42.0 + np.random.uniform(-1, 1) # 失电跌落
            comp_power = st.session_state.pid_core.compute(50.0, raw_freq_drop, dt)
            freq = min(50.0, raw_freq_drop + comp_power * 0.5) # 补偿后的频率
            volts = 440 * (freq / 50.0) # V/f 恒定模拟
            # 扣除应急电池 B 的电量
            st.session_state.battery_B.simulate_discharge(500, dt)

        with m_row.container():
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Grid Freq (Hz)", f"{freq:.2f}")
            col2.metric("Bus Voltage (V)", f"{volts:.1f}")
            col3.metric("ESS-B (Emergency) SOC", f"{st.session_state.battery_B.soc:.2f}%")
            col4.metric("PID Comp. Output (kW)", f"{comp_power:.1f}")
        
        chart_data = pd.DataFrame(np.random.randn(20, 1)*0.05 + freq, columns=['Frequency Trace'])
        c_placeholder.line_chart(chart_data, height=250)
        
        time.sleep(dt)
        if st.session_state.page != t['m1']: break

# --- 路由: 异构动力分析 ---
elif st.session_state.page == t['m2']:
    st.title(f"🔋 {t['m2']}")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Battery A (Lifepo4) Telemetry")
        st.write(f"**Capacity:** {st.session_state.battery_A.capacity} kWh")
        st.write(f"**Temperature:** {st.session_state.battery_A.temperature:.1f} °C")
        st.progress(st.session_state.battery_A.soc / 100, text=f"SOC: {st.session_state.battery_A.soc:.1f}%")
    with c2:
        st.subheader("Energy Distribution")
        df = pd.DataFrame({'Source': ['Solar Array', 'Battery A', 'Diesel Gen'], 'Share': [35, 45, 20]})
        fig = px.pie(df, values='Share', names='Source', hole=0.5)
        fig.update_layout(margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig, use_container_width=True)

# --- 路由: 运行日志与设置 ---
elif st.session_state.page == t['m3']:
    st.title(f"⚙️ {t['m3']}")
    st.subheader("System Event Logs (SQLite)")
    try:
        conn = sqlite3.connect('marine_ems_logs.db')
        logs_df = pd.read_sql_query("SELECT * FROM system_logs ORDER BY timestamp DESC LIMIT 10", conn)
        st.dataframe(logs_df, use_container_width=True)
        conn.close()
    except Exception as e:
        st.warning("No logs available yet.")

    st.subheader("PID Tuning Parameters")
    with st.form("pid_tuning"):
        kp = st.number_input("Proportional (Kp)", value=1.5)
        ki = st.number_input("Integral (Ki)", value=0.1)
        if st.form_submit_button("Update Control Matrix"):
            st.session_state.pid_core.kp = kp
            st.session_state.pid_core.ki = ki
            st.success("Algorithm parameters updated securely.")

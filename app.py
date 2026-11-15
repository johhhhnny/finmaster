"""
FinMaster — 价值投资大师工作站 (Web UI 入口)
主应用调度控制器：负责状态初始化、样式注入与各视图路由调度。
"""
import os
import sys
import streamlit as st

# 添加本地模块搜索路径
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from engine.config import load_app_env
from ui import (
    inject_custom_css,
    render_sidebar,
    render_workbench,
    render_archive,
    render_calculator
)

# 1. 初始化环境变量与页面基础配置
load_app_env()

st.set_page_config(
    page_title="FinMaster — 价值投资大师工作站",
    page_icon="🦅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. 注入全局专业金融终端定制样式
inject_custom_css()

# 3. 渲染侧边栏导航与系统状态
sidebar_state = render_sidebar()

# 4. 核心工作台视图路由调度
if sidebar_state.app_mode == "🚀 智能投研工作台":
    render_workbench(sidebar_state)
elif sidebar_state.app_mode == "📂 历史研报知识库":
    render_archive()
elif sidebar_state.app_mode == "🧮 金融严谨性计算器":
    render_calculator()

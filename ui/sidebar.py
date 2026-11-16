"""
FinMaster UI 侧边栏模块
负责品牌信息展示、工作台功能导航、21 项技能级联精选与系统运行状态快照。
全套系统设置与多数据源配置已迁移至独立的「⚙️ 系统与数据源设置」全屏中台。
"""
import os
import time
from dataclasses import dataclass
import streamlit as st

from engine.config import get_current_config, get_search_config, get_plugin_keys
from engine.skill_manager import skill_manager
from engine.llm import GeminiClient
from engine.executor import ExecutionEngine


@dataclass
class SidebarState:
    app_mode: str
    selected_skill_id: str
    client: GeminiClient
    engine: ExecutionEngine
    enable_search: bool
    saved_model: str
    search_provider: str
    tavily_key: str


def render_sidebar() -> SidebarState:
    """渲染侧边栏导航与状态快照，返回当前选中的状态及初始化的客户端与执行引擎"""
    with st.sidebar:
        # 顶部品牌信息
        st.markdown("""
        <div class="sidebar-header-box">
            <div class="sidebar-main-title">
                <span>🦅</span> FinMaster
                <span style="font-size: 0.65rem; background: #e0f2fe; color: #0284c7; padding: 2px 6px; border-radius: 4px; font-weight: 600; margin-left: auto;">v1.2</span>
            </div>
            <div class="sidebar-sub-caption">价值投资大师工作站 · 多引擎投研操作系统</div>
        </div>
        """, unsafe_allow_html=True)

        # 1. 核心工作台功能导航
        st.markdown('<div class="sidebar-section-title">🧭 工作台导航</div>', unsafe_allow_html=True)
        nav_options = [
            "🚀 智能投研工作台",
            "📂 历史研报知识库",
            "🧮 金融严谨性计算器",
            "⚙️ 系统与数据源设置"
        ]
        app_mode = st.radio(
            "工作台功能导航",
            nav_options,
            index=0,
            label_visibility="collapsed"
        )

        # 2. 投资技能精选库（紧密联动，仅在工作台模式下展示）
        selected_skill_id = "investment-team"
        if app_mode == "🚀 智能投研工作台":
            st.markdown('<div class="sidebar-section-title" style="margin-top: 12px;">📚 投资技能精选 (21 Skills)</div>', unsafe_allow_html=True)
            categories = skill_manager.list_categories()
            selected_category = st.selectbox("投研阶段", categories, index=1)

            skills_in_cat = skill_manager.get_skills_by_category(selected_category)
            skill_options = {s["id"]: f"{s['icon']} {s['title']}" for s in skills_in_cat}

            selected_skill_id = st.selectbox(
                "研究工具",
                options=list(skill_options.keys()),
                format_func=lambda x: skill_options[x],
                index=0
            )

        # 3. 读取当前生效配置并初始化底层推演客户端与引擎
        saved_key, saved_model, saved_temp = get_current_config()
        saved_provider, saved_tavily = get_search_config()
        plugin_keys = get_plugin_keys()

        enable_search = (saved_provider != "none")
        client = GeminiClient(api_key=saved_key, model=saved_model, temperature=saved_temp)
        engine = ExecutionEngine(client)

        # 4. 底部系统运行状态快照 (极简、通透、现代化卡片)
        active_plugins = sum(1 for v in plugin_keys.values() if v and len(v.strip()) > 3)
        prov_display = {
            "auto": "智能自适应",
            "tavily": "Tavily AI",
            "google": "Google 原生",
            "duckduckgo": "DuckDuckGo",
            "none": "默认关闭 (7大底座)",
            "off": "默认关闭 (7大底座)"
        }.get(saved_provider, saved_provider.upper())

        st.markdown('<div class="sidebar-section-title" style="margin-top: 20px;">🖥️ 系统运行状态</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 10px 12px; font-size: 0.74rem; color: #475569; line-height: 1.55; box-shadow: 0 1px 2px rgba(0,0,0,0.02);">
            <div style="display: flex; justify-content: space-between; margin-bottom: 3px;">
                <span style="color: #64748b;">推理模型:</span>
                <span style="font-weight: 600; color: #0f172a; font-family: monospace;">{saved_model}</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 3px;">
                <span style="color: #64748b;">联网检索:</span>
                <span style="font-weight: 600; color: #0284c7;">{prov_display}</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 3px;">
                <span style="color: #64748b;">官方底座:</span>
                <span style="font-weight: 600; color: #166534;">yfinance + SEC + FRED 🟢</span>
            </div>
            <div style="display: flex; justify-content: space-between;">
                <span style="color: #64748b;">扩展插件:</span>
                <span style="font-weight: 600; color: #7c3aed;">{active_plugins}/4 已激活</span>
            </div>
        </div>
        <div style="font-size: 0.68rem; color: #94a3b8; text-align: center; margin-top: 6px;">
            点击上方「⚙️ 系统与数据源设置」修改
        </div>
        """, unsafe_allow_html=True)

        return SidebarState(
            app_mode=app_mode,
            selected_skill_id=selected_skill_id,
            client=client,
            engine=engine,
            enable_search=enable_search,
            saved_model=saved_model,
            search_provider=saved_provider,
            tavily_key=saved_tavily
        )

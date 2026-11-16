"""
FinMaster UI 侧边栏模块
负责品牌信息展示、工作台功能卡片导航、21 项技能阶段微胶囊与卡片直选，以及底部常驻设置与系统运行状态快照。
全套系统设置与多数据源配置已迁移至独立的「⚙️ 系统与数据源设置」全屏中台。
"""
import os
import re
import time
from dataclasses import dataclass
import streamlit as st

from version import __version__
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
        st.markdown(f"""
        <div class="sidebar-header-box">
            <div class="sidebar-main-title">
                <span>🦅</span> FinMaster
                <span style="font-size: 0.65rem; background: #e0f2fe; color: #0284c7; padding: 2px 6px; border-radius: 4px; font-weight: 600; margin-left: auto;">v{__version__}</span>
            </div>
            <div class="sidebar-sub-caption">价值投资大师工作站 · 多引擎投研操作系统</div>
        </div>
        """, unsafe_allow_html=True)

        # 状态初始化
        if "sidebar_app_mode" not in st.session_state:
            st.session_state["sidebar_app_mode"] = "🚀 智能投研工作台"
        if "last_workbench_nav" not in st.session_state:
            st.session_state["last_workbench_nav"] = "🚀 智能投研工作台"

        TOP_NAV_OPTIONS = [
            "🚀 智能投研工作台",
            "📂 历史研报知识库",
            "🧮 金融严谨性计算器",
        ]

        # 1. 核心工作台功能导航（现代浅蓝高光色块卡片）
        st.markdown('<div class="sidebar-section-title">🧭 工作台导航</div>', unsafe_allow_html=True)

        current_app_mode = st.session_state["sidebar_app_mode"]
        current_top_index = (
            TOP_NAV_OPTIONS.index(current_app_mode)
            if current_app_mode in TOP_NAV_OPTIONS
            else None
        )

        def _on_top_nav_change():
            val = st.session_state.get("sidebar_top_nav_radio")
            if val:
                st.session_state["sidebar_app_mode"] = val
                st.session_state["last_workbench_nav"] = val

        selected_top = st.radio(
            "工作台功能导航",
            TOP_NAV_OPTIONS,
            index=current_top_index,
            key="sidebar_top_nav_radio",
            on_change=_on_top_nav_change,
            label_visibility="collapsed",
            width="stretch"
        )
        if selected_top and selected_top != current_app_mode and current_app_mode != "⚙️ 系统与数据源设置":
            st.session_state["sidebar_app_mode"] = selected_top
            st.session_state["last_workbench_nav"] = selected_top

        app_mode = st.session_state["sidebar_app_mode"]

        # 2. 投资技能精选库（方案 A：5 阶段横向微胶囊 + 该阶段技能直选卡片）
        selected_skill_id = st.session_state.get("selected_skill_id", "investment-team")
        if app_mode == "🚀 智能投研工作台":
            st.markdown('<div class="sidebar-section-title" style="margin-top: 14px;">📚 投资技能精选 (21 Skills)</div>', unsafe_allow_html=True)

            STAGE_PILL_NAMES = {
                "1. 🔍 初筛与赛道漏斗": "🔍 初筛",
                "2. 🏢 深度个股研究": "🏢 个股",
                "3. ⚖️ 估值与投资准则": "⚖️ 估值",
                "4. ⏱️ 投后跟踪与风控": "⏱️ 跟踪",
                "5. 📢 成果转化与发布": "📢 发布",
            }
            categories = skill_manager.list_categories()
            default_cat = st.session_state.get("sidebar_selected_stage", "2. 🏢 深度个股研究")
            if default_cat not in categories:
                default_cat = categories[1]

            selected_stage = st.pills(
                "投研阶段",
                categories,
                format_func=lambda c: STAGE_PILL_NAMES.get(c, c),
                default=default_cat,
                key="sidebar_stage_pills",
                label_visibility="collapsed"
            )
            if not selected_stage:
                selected_stage = default_cat
            st.session_state["sidebar_selected_stage"] = selected_stage

            # 获取当前阶段下的所有技能并以卡片形式直选
            skills_in_cat = skill_manager.get_skills_by_category(selected_stage)
            skill_ids = [s["id"] for s in skills_in_cat]
            skill_map = {s["id"]: s for s in skills_in_cat}

            def format_skill_label(sid: str) -> str:
                s = skill_map.get(sid)
                if not s:
                    return sid
                clean_title = re.sub(r'[\(（].*?[\)）]', '', s['title']).strip()
                return f"{s['icon']} {clean_title}"

            current_skill_index = 0
            if selected_skill_id in skill_ids:
                current_skill_index = skill_ids.index(selected_skill_id)

            selected_skill_id = st.radio(
                "技能工具直选",
                options=skill_ids,
                format_func=format_skill_label,
                index=current_skill_index,
                key=f"sidebar_skills_radio_{selected_stage}",
                label_visibility="collapsed",
                width="stretch"
            )
            st.session_state["selected_skill_id"] = selected_skill_id

        # 3. 读取当前生效配置并初始化底层推演客户端与引擎
        saved_key, saved_model, saved_temp = get_current_config()
        saved_provider, saved_tavily = get_search_config()
        plugin_keys = get_plugin_keys()

        enable_search = (saved_provider != "none")
        client = GeminiClient(api_key=saved_key, model=saved_model, temperature=saved_temp)
        engine = ExecutionEngine(client)

        # 4. 底部系统运行状态快照与独立常驻设置栏
        active_plugins = sum(1 for v in plugin_keys.values() if v and len(v.strip()) > 3)
        prov_display = {
            "auto": "智能自适应",
            "tavily": "Tavily AI",
            "google": "Google 原生",
            "duckduckgo": "DuckDuckGo",
            "none": "默认关闭 (7大底座)",
            "off": "默认关闭 (7大底座)"
        }.get(saved_provider, saved_provider.upper())

        st.markdown('<div class="sidebar-section-title" style="margin-top: 18px;">🖥️ 系统运行状态</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 10px 12px; font-size: 0.74rem; color: #475569; line-height: 1.55; box-shadow: 0 1px 2px rgba(0,0,0,0.02); margin-bottom: 8px;">
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
        """, unsafe_allow_html=True)

        # 5. 底部独立常驻设置入口卡片 / 按钮
        is_settings_active = (app_mode == "⚙️ 系统与数据源设置")
        settings_label = "⚙️ 系统与数据源设置 (当前激活)" if is_settings_active else "⚙️ 系统与数据源设置"
        if st.button(
            settings_label,
            key="sidebar_bottom_settings_btn",
            type="primary" if is_settings_active else "secondary",
            use_container_width=True
        ):
            if is_settings_active:
                # 切换回上次的工作台视图
                st.session_state["sidebar_app_mode"] = st.session_state.get("last_workbench_nav", "🚀 智能投研工作台")
                st.session_state["sidebar_top_nav_radio"] = st.session_state["sidebar_app_mode"]
            else:
                # 切换为系统设置全屏中台
                st.session_state["sidebar_app_mode"] = "⚙️ 系统与数据源设置"
                st.session_state["sidebar_top_nav_radio"] = None
            st.rerun()

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

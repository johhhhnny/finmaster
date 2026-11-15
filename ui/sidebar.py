"""
FinMaster UI 侧边栏模块
负责品牌信息展示、工作台功能导航、21 项技能级联精选、多引擎搜索配置（Tavily/Google/DDG）与连通性测试。
"""
import os
import time
from dataclasses import dataclass
import streamlit as st

from engine.config import save_env_config, get_current_config, get_search_config, get_sec_email, get_plugin_keys
from engine.skill_manager import skill_manager
from engine.llm import GeminiClient
from engine.executor import ExecutionEngine
from engine.search_provider import search_manager

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
    """渲染侧边栏导航与设置，返回当前选中的状态及初始化的客户端与执行引擎"""
    with st.sidebar:
        # 顶部品牌信息
        st.markdown("""
        <div class="sidebar-header-box">
            <div class="sidebar-main-title">
                <span>🦅</span> FinMaster
                <span style="font-size: 0.65rem; background: #e0f2fe; color: #0284c7; padding: 2px 6px; border-radius: 4px; font-weight: 600; margin-left: auto;">v1.1</span>
            </div>
            <div class="sidebar-sub-caption">价值投资大师工作站 · 多引擎投研操作系统</div>
        </div>
        """, unsafe_allow_html=True)

        # 1. 核心工作台功能导航
        st.markdown('<div class="sidebar-section-title">🧭 工作台导航</div>', unsafe_allow_html=True)
        app_mode = st.radio(
            "工作台功能导航",
            ["🚀 智能投研工作台", "📂 历史研报知识库", "🧮 金融严谨性计算器"],
            index=0,
            label_visibility="collapsed"
        )

        # 2. 投资技能精选库（紧密联动置于导航正下方）
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

        # 3. 底部系统设置与大模型/搜索引擎配置
        saved_key, saved_model, saved_temp = get_current_config()
        saved_provider, saved_tavily = get_search_config()
        saved_sec_email = get_sec_email()
        plugin_keys = get_plugin_keys()

        if "settings_expanded" not in st.session_state:
            st.session_state["settings_expanded"] = not bool(saved_key)

        st.markdown('<div class="sidebar-section-title" style="margin-top: 16px;">⚙️ 系统与引擎设置</div>', unsafe_allow_html=True)
        with st.expander(f"模型与搜索 · {saved_model}", expanded=st.session_state["settings_expanded"]):
            # 大模型配置
            api_key = st.text_input(
                "Gemini API Key",
                value=saved_key,
                type="password",
                help="支持在此输入并点击「保存配置」，持久化至 .env",
                placeholder="填入您的 Gemini API Key"
            )

            preset_models = [
                "gemini-3.5-flash-lite",
                "gemini-2.5-flash",
                "gemini-2.5-flash-lite",
                "✏️ 自定义模型代码..."
            ]

            if saved_model in preset_models:
                default_idx = preset_models.index(saved_model)
            else:
                preset_models.insert(0, saved_model)
                default_idx = 0

            col_m1, col_m2 = st.columns([7, 5])
            with col_m1:
                selected_model_option = st.selectbox(
                    "大模型",
                    preset_models,
                    index=default_idx,
                    help="选择推荐模型或输入自定义模型代码"
                )
            with col_m2:
                temperature = st.slider("多样性 Temp", 0.0, 1.0, saved_temp, 0.05)

            if selected_model_option == "✏️ 自定义模型代码...":
                model_name = st.text_input(
                    "输入模型代码",
                    value=saved_model if saved_model not in preset_models else "gemini-3.5-flash-lite",
                    placeholder="例如: gemini-3.5-flash-lite"
                )
            else:
                model_name = selected_model_option

            # 搜索引擎与配额优化配置
            st.markdown('<hr style="margin: 10px 0; border: none; border-top: 1px dashed #cbd5e1;">', unsafe_allow_html=True)
            st.markdown('**🌐 实时联网搜索引擎配置**')

            provider_options = {
                "auto": "🤖 智能多级调度 (Auto 优先Tavily/原生Google/DDG)",
                "tavily": "⚡ Tavily AI 搜索 (推荐 · 1,000次/月 独立免限配额)",
                "google": "🌐 Gemini 原生 Google Search (每日限20次)",
                "duckduckgo": "🦆 DuckDuckGo (免Key极简)",
                "none": "🚫 关闭联网 (纯模型深度推演)"
            }

            provider_keys = list(provider_options.keys())
            current_provider_idx = provider_keys.index(saved_provider) if saved_provider in provider_keys else 0

            selected_provider_key = st.selectbox(
                "搜索引擎",
                options=provider_keys,
                format_func=lambda k: provider_options[k],
                index=current_provider_idx,
                help="当 Google Search 每日 20 次用完时，选择 Tavily 或 Auto 调度可彻底摆脱限流！"
            )

            # Tavily API Key 输入框 (当启用 Tavily 或 Auto 调度时展示)
            tavily_key = saved_tavily
            if selected_provider_key in ("auto", "tavily"):
                tavily_key = st.text_input(
                    "Tavily API Key",
                    value=saved_tavily,
                    type="password",
                    placeholder="tvly-xxxxxxxxxxxxxxxxxxxx",
                    help="前往 https://tavily.com 免费注册即可获得每月 1,000 次搜索配额（无需绑定信用卡）"
                )
                if not tavily_key:
                    st.caption("💡 [前往 tavily.com 免费获取 API Key](https://tavily.com) (每月 1000 次，50倍于 Gemini 每日限制)")

            # 结构化硬数据底座状态与 SEC 邮箱配置
            with st.expander("🏛️ 官方硬核数据底座 (yfinance + SEC EDGAR)", expanded=False):
                st.markdown("""
                <div style="font-size: 0.74rem; color: #475569; line-height: 1.45; margin-bottom: 6px;">
                    • <strong>yfinance</strong>: 免 Key 直连各大交易所实时行情与近 4 季度三张表。<br>
                    • <strong>SEC EDGAR</strong>: 美国证监会官方直连。依 SEC 规定已内置合规请求头。您也可填入真实邮箱提升合规级别：
                </div>
                """, unsafe_allow_html=True)
                sec_contact_email = st.text_input(
                    "SEC 联络邮箱 (可选)",
                    value=saved_sec_email,
                    placeholder="例如: your_name@domain.com (留空则使用内置默认标识)",
                    help="SEC 官方要求在 HTTP User-Agent 请求头中声明应用名与联系邮箱，用于超频提醒。"
                )

            # 扩展金融插件数据源配置 (选配 · 填Key即激活)
            with st.expander("🔌 高阶扩展数据源插件 (Finnhub / FMP / Adanos)", expanded=False):
                st.markdown("""
                <div style="font-size: 0.74rem; color: #475569; line-height: 1.45; margin-bottom: 6px;">
                    选配高阶专业投研插件。填入对应 API Key 即可激活对应专业卡片，留空则由 yfinance 基础底座平滑支持：
                </div>
                """, unsafe_allow_html=True)
                
                finnhub_key_input = st.text_input(
                    "Finnhub API Key (华尔街目标价/Surprise)",
                    value=plugin_keys.get("finnhub", ""),
                    type="password",
                    placeholder="例如: cxxxxxxxxxxxxxxx",
                    help="前往 https://finnhub.io 免费注册获取，享 60次/分钟 机构级华尔街目标价与财报Surprise数据。"
                )
                
                fmp_key_input = st.text_input(
                    "FMP API Key (ROIC / 杜邦分析 / DCF模型)",
                    value=plugin_keys.get("fmp", ""),
                    type="password",
                    placeholder="例如: xxxxxxxxxxxxxxxxxxxxxxxx",
                    help="前往 https://financialmodelingprep.com 免费注册获取，享 250次/天 自动化现金流折现与ROIC建模。"
                )
                
                adanos_key_input = st.text_input(
                    "Adanos API Key (散户情绪 / Polymarket盘口)",
                    value=plugin_keys.get("adanos", ""),
                    type="password",
                    placeholder="例如: adanos_xxxxxxxxxxxxxxxx",
                    help="前往 https://adanos.com 免费注册获取，追踪 Reddit/X 讨论热度与预测市场赔率。"
                )

            # 保存与测试按钮组
            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                if st.button("💾 保存配置", use_container_width=True):
                    save_env_config(
                        key=api_key,
                        model=model_name,
                        temp=temperature,
                        tavily_key=tavily_key,
                        search_provider=selected_provider_key,
                        sec_email=sec_contact_email,
                        finnhub_key=finnhub_key_input,
                        fmp_key=fmp_key_input,
                        adanos_key=adanos_key_input
                    )
                    st.session_state["settings_expanded"] = True
                    st.toast(f"✅ 全局配置已保存！搜索模式: {selected_provider_key}")
                    time.sleep(0.3)
                    st.rerun()

            with btn_col2:
                test_btn = st.button("🔌 测试连接", use_container_width=True)

            enable_search = (selected_provider_key != "none")

            client = GeminiClient(api_key=api_key, model=model_name, temperature=temperature)
            engine = ExecutionEngine(client)

            if test_btn:
                st.session_state["settings_expanded"] = True
                # 1. 测试 Gemini 模型连通性
                with st.spinner(f"正在测试模型 {model_name} 连通性..."):
                    test_res = client.test_connection()
                    if test_res["success"]:
                        st.markdown(f'''
                        <div class="sidebar-status-badge sidebar-status-success">
                            <span>✅</span>
                            <span>{test_res["message"]}</span>
                        </div>
                        ''', unsafe_allow_html=True)
                        with st.expander("Gemini 诊断详情", expanded=False):
                            st.caption(test_res["details"])
                    else:
                        st.markdown(f'''
                        <div class="sidebar-status-badge sidebar-status-error">
                            <span>❌</span>
                            <span>{test_res["message"]}</span>
                        </div>
                        ''', unsafe_allow_html=True)
                        with st.expander("Gemini 错误详情", expanded=True):
                            st.caption(test_res["details"])

                # 2. 如果配置了 Tavily，同时测试 Tavily 搜索引擎
                if selected_provider_key in ("auto", "tavily") and tavily_key:
                    with st.spinner("正在测试 Tavily 搜索引擎连通性..."):
                        t_res = search_manager.tavily.test_connection(tavily_key)
                        if t_res["success"]:
                            st.markdown(f'''
                            <div class="sidebar-status-badge sidebar-status-success">
                                <span>⚡</span>
                                <span>{t_res["message"]}</span>
                            </div>
                            ''', unsafe_allow_html=True)
                            with st.expander("Tavily 诊断详情", expanded=False):
                                st.caption(t_res["details"])
                        else:
                            st.markdown(f'''
                            <div class="sidebar-status-badge sidebar-status-warning">
                                <span>⚠️</span>
                                <span>{t_res["message"]}</span>
                            </div>
                            ''', unsafe_allow_html=True)
                            with st.expander("Tavily 详情", expanded=True):
                                st.caption(t_res["details"])

        return SidebarState(
            app_mode=app_mode,
            selected_skill_id=selected_skill_id,
            client=client,
            engine=engine,
            enable_search=enable_search,
            saved_model=saved_model,
            search_provider=selected_provider_key,
            tavily_key=tavily_key
        )

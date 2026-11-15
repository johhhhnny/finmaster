"""
FinMaster UI 智能投研工作台模块
负责 21 项技能执行、四大师并行看板、快捷填选、预检展台与结果渲染。
"""
import time
from typing import Any
import streamlit as st

from engine.skill_manager import skill_manager
from engine.archive_manager import archive_manager
from ui.sidebar import SidebarState

def render_workbench(state: SidebarState):
    """渲染智能投研工作台主界面"""
    selected_skill_id = state.selected_skill_id
    client = state.client
    engine = state.engine
    enable_search = state.enable_search
    saved_model = state.saved_model

    skill_meta = skill_manager.get_skill(selected_skill_id) or {}
    skill_title = skill_meta.get("title", selected_skill_id)
    skill_icon = skill_meta.get("icon", "📄")
    skill_desc = skill_meta.get("description", "")
    skill_mode = skill_meta.get("mode", "single_agent")
    skill_category = skill_meta.get("category", "")

    # 1. 顶部整合式技能看板卡片 (Skill Hero Banner)
    if skill_mode == "multi_agent":
        mode_badge = '<span style="font-size: 0.72rem; font-weight: 600; color: #1d4ed8; background: #eff6ff; border: 1px solid #bfdbfe; padding: 3px 8px; border-radius: 6px;">👥 四大师并行 (Multi-Agent)</span>'
    elif skill_mode == "funnel":
        mode_badge = '<span style="font-size: 0.72rem; font-weight: 600; color: #b45309; background: #fffbeb; border: 1px solid #fde68a; padding: 3px 8px; border-radius: 6px;">🌪️ 漏斗精选 (Funnel)</span>'
    else:
        mode_badge = '<span style="font-size: 0.72rem; font-weight: 600; color: #047857; background: #ecfdf5; border: 1px solid #a7f3d0; padding: 3px 8px; border-radius: 6px;">🤖 单智能体 (Single-Agent)</span>'

    search_provider = getattr(state, "search_provider", "auto")
    has_tavily = bool(getattr(state, "tavily_key", ""))
    if not enable_search:
        search_badge = '<span style="font-size: 0.72rem; color: #64748b; background: #f8fafc; border: 1px solid #cbd5e1; padding: 3px 8px; border-radius: 6px; font-weight: 600;">📊 yfinance + 🏛️ SEC EDGAR (离线模式)</span>'
    elif search_provider == "tavily" or (search_provider == "auto" and has_tavily):
        search_badge = '<span style="font-size: 0.72rem; color: #0284c7; background: #f0f9ff; border: 1px solid #bae6fd; padding: 3px 8px; border-radius: 6px; font-weight: 600;">📊 yfinance + 🏛️ SEC + ⚡ Tavily 混合金融中台</span>'
    elif search_provider == "duckduckgo":
        search_badge = '<span style="font-size: 0.72rem; color: #b45309; background: #fffbeb; border: 1px solid #fde68a; padding: 3px 8px; border-radius: 6px; font-weight: 600;">📊 yfinance + 🏛️ SEC + 🦆 DuckDuckGo</span>'
    else:
        search_badge = '<span style="font-size: 0.72rem; color: #059669; background: #ecfdf5; border: 1px solid #a7f3d0; padding: 3px 8px; border-radius: 6px; font-weight: 600;">📊 yfinance + 🏛️ SEC + 🛡️ Google 实时联网</span>'

    st.markdown(f"""
    <div class="skill-hero-card">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 16px;">
            <div style="flex: 1;">
                <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 6px;">
                    <span style="font-size: 1.6rem; line-height: 1;">{skill_icon}</span>
                    <span style="font-size: 1.32rem; font-weight: 700; color: #0f172a; letter-spacing: -0.01em;">{skill_title}</span>
                    <span style="font-size: 0.72rem; background: #f1f5f9; color: #475569; padding: 2px 8px; border-radius: 9999px; font-weight: 600;">{skill_category}</span>
                </div>
                <div style="font-size: 0.83rem; color: #475569; line-height: 1.45;">
                    <strong style="color: #1e293b;">核心方法论：</strong>{skill_desc}
                </div>
            </div>
            <div style="display: flex; flex-direction: column; align-items: flex-end; gap: 6px;">
                {mode_badge}
                {search_badge}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 2. 现代参数控制台卡片 (Parameter Control Station Card)
    inputs_def = skill_meta.get("inputs", [])
    has_target = any(inp["key"] in ("target", "holdings") for inp in inputs_def)

    try:
        param_card_box = st.container(border=True)
    except TypeError:
        param_card_box = st.container()

    with param_card_box:
        p_head_col1, p_head_col2 = st.columns([1, 2])
        with p_head_col1:
            st.markdown('<div style="font-size: 0.94rem; font-weight: 700; color: #0f172a; margin-top: 2px;">📝 设定研究参数</div>', unsafe_allow_html=True)
        with p_head_col2:
            st.markdown('<div style="text-align: right; font-size: 0.74rem; color: #64748b; margin-top: 3px;">⚡ 点击下方标的标签可 1 键快捷填入</div>', unsafe_allow_html=True)

        if has_target:
            q_cols = st.columns(6)
            samples = [
                ("🍎 苹果 AAPL", "苹果 / AAPL"),
                ("🔍 谷歌 GOOGL", "谷歌 / GOOGL"),
                ("⚡ 特斯拉 TSLA", "特斯拉 / TSLA"),
                ("🍶 贵州茅台", "贵州茅台 / 600519"),
                ("🐧 腾讯控股", "腾讯控股 / 00700"),
                ("💊 伯克希尔", "伯克希尔哈撒韦 / BRK.B")
            ]
            for s_i, (s_name, s_val) in enumerate(samples):
                with q_cols[s_i]:
                    if st.button(s_name, key=f"quick_s_{s_i}", use_container_width=True):
                        st.session_state["target_preset_val"] = s_val
                        st.rerun()

        # 动态输入表单字段
        user_inputs = {}
        if len(inputs_def) == 2:
            form_cols = st.columns(2)
        else:
            form_cols = [st.container() for _ in range(max(1, len(inputs_def)))]

        for idx, inp in enumerate(inputs_def):
            k = inp["key"]
            lbl = inp["label"]
            placeholder = inp.get("placeholder", "")
            req = inp.get("required", False)
            is_textarea = inp.get("type") == "textarea"

            label_display = f"{lbl} *" if req else lbl
            col_ctx = form_cols[idx]

            initial_text = ""
            if k in ("target", "holdings") and "target_preset_val" in st.session_state:
                initial_text = st.session_state["target_preset_val"]

            with col_ctx:
                if is_textarea:
                    user_inputs[k] = st.text_area(label_display, value=initial_text, placeholder=placeholder, height=110)
                else:
                    user_inputs[k] = st.text_input(label_display, value=initial_text, placeholder=placeholder)

        # 启动按钮与系统状态栏
        btn_action_col, hint_action_col = st.columns([1.2, 3.8])
        with btn_action_col:
            start_btn = st.button("🚀 启动投研分析", type="primary", use_container_width=True)
        with hint_action_col:
            if not client.is_configured():
                st.warning("👈 请先在左侧侧边栏填入 Gemini API Key 即可启动！")
            else:
                if not enable_search:
                    net_text = "纯模型推演 (无联网)"
                    net_color = "#64748b"
                elif search_provider == "tavily" or (search_provider == "auto" and has_tavily):
                    net_text = "开启 (Tavily AI 免限)"
                    net_color = "#0284c7"
                elif search_provider == "duckduckgo":
                    net_text = "开启 (DuckDuckGo)"
                    net_color = "#b45309"
                else:
                    net_text = "开启 (Google Search)"
                    net_color = "#059669"

                st.markdown(f'''
                <div style="display: flex; align-items: center; height: 100%; min-height: 2.35rem; font-size: 0.78rem; color: #475569; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 0 12px;">
                    <span>⚡ <strong>引擎状态</strong>：<span style="color: #059669; font-weight: 600;">就绪 ({saved_model})</span></span>
                    <span style="margin: 0 10px; color: #cbd5e1;">|</span>
                    <span>🌐 <strong>实时联网</strong>：<span style="color: {net_color}; font-weight: 600;">{net_text}</span></span>
                    <span style="margin: 0 10px; color: #cbd5e1;">|</span>
                    <span>⏱️ <strong>预计耗时</strong>：<span style="color: #1e293b; font-weight: 600;">{"15~30s" if skill_mode == "multi_agent" else "8~15s"}</span></span>
                </div>
                ''', unsafe_allow_html=True)

    # 3. 未点击启动时的常态化工作区（空间充实利用，展示体系架构与知识库联动）
    if not start_btn:
        st.markdown("""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 14px; margin-bottom: 8px;">
            <div style="font-size: 0.94rem; font-weight: 700; color: #1e293b; display: flex; align-items: center; gap: 6px;">
                <span>📋</span> 投研体系架构、知识库联动与分析规范
            </div>
            <div style="font-size: 0.74rem; color: #64748b;">四大师分工 · 专属执行流程 · 历史研报速览 · 严谨性铁律</div>
        </div>
        """, unsafe_allow_html=True)

        tab_matrix, tab_workflow, tab_archive, tab_rules = st.tabs([
            "👥 四大师投研矩阵与分工",
            "⚡ 本技能专属执行流程",
            "📂 本地历史研报知识库速览",
            "🛡️ 价值投资工作站严谨性铁律"
        ])

        with tab_matrix:
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.markdown("""
                <div class="master-preview-card" style="border-top: 3px solid #10b981;">
                    <div style="font-weight: 700; font-size: 0.92rem; color: #065f46; margin-bottom: 4px;">🟢 段永平视角</div>
                    <div style="font-size: 0.76rem; font-weight: 600; color: #1e293b; margin-bottom: 8px;">商业模式与护城河分析师</div>
                    <ul style="font-size: 0.74rem; color: #475569; padding-left: 16px; margin: 0; line-height: 1.55;">
                        <li><strong>商业模式本质</strong>：谁付钱？为何买单？边际成本如何？</li>
                        <li><strong>财报分部拆解</strong>：最新收入与真实利润分部。</li>
                        <li><strong>五维护城河检验</strong>：品牌心智、网络效应、转换成本、定价权。</li>
                        <li><strong>代际异化</strong>：是轻资产印钞机，还是滑向重资产重工业？</li>
                        <li><strong>商业模式评级</strong>：A+ / A / A- / B 及护城河星级。</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            with c2:
                st.markdown("""
                <div class="master-preview-card" style="border-top: 3px solid #3b82f6;">
                    <div style="font-weight: 700; font-size: 0.92rem; color: #1e40af; margin-bottom: 4px;">🔵 巴菲特视角</div>
                    <div style="font-size: 0.76rem; font-weight: 600; color: #1e293b; margin-bottom: 8px;">财务造血与估值审计分析师</div>
                    <ul style="font-size: 0.74rem; color: #475569; padding-left: 16px; margin: 0; line-height: 1.55;">
                        <li><strong>核心主营穿透</strong>：剔除浮动损益还原核心主营EPS。</li>
                        <li><strong>现金流审计</strong>：经营现金流、CapEx吞噬比、真自由现金流。</li>
                        <li><strong>资产负债表拆解</strong>：纯流动性现金池，测算每股净现金。</li>
                        <li><strong>扣现金估值</strong>：测算 Ex-Cash PE，对比5年中枢。</li>
                        <li><strong>三情景估值推演</strong>：乐观/中性/悲观估值与安全边际。</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            with c3:
                st.markdown("""
                <div class="master-preview-card" style="border-top: 3px solid #f59e0b;">
                    <div style="font-weight: 700; font-size: 0.92rem; color: #92400e; margin-bottom: 4px;">🟠 芒格视角</div>
                    <div style="font-size: 0.76rem; font-weight: 600; color: #1e293b; margin-bottom: 8px;">行业竞争与逆向检验分析师</div>
                    <ul style="font-size: 0.74rem; color: #475569; padding-left: 16px; margin: 0; line-height: 1.55;">
                        <li><strong>市场格局划分</strong>：竞争对手份额拉锯与商业机制分化。</li>
                        <li><strong>范式转移冲击</strong>：新技术带来的创新者窘境与自残防御。</li>
                        <li><strong>芒格式逆向检验</strong>：推演5个导致利润断崖的致命情境。</li>
                        <li><strong>冷酷逆向思维</strong>：寻找足以摧毁护城河的隐蔽阿喀琉斯之踵。</li>
                        <li><strong>竞争护城河星级</strong>：严苛1-5星独立评级。</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            with c4:
                st.markdown("""
                <div class="master-preview-card" style="border-top: 3px solid #8b5cf6;">
                    <div style="font-weight: 700; font-size: 0.92rem; color: #5b21b6; margin-bottom: 4px;">🟣 李录视角</div>
                    <div style="font-size: 0.76rem; font-weight: 600; color: #1e293b; margin-bottom: 8px;">治理风险与文明确定性分析师</div>
                    <ul style="font-size: 0.74rem; color: #475569; padding-left: 16px; margin: 0; line-height: 1.55;">
                        <li><strong>管理层画像</strong>：受托人品行、危机应激纠错、资本配置纪律。</li>
                        <li><strong>反垄断与司法穿透</strong>：监管反垄断与硬性黑天鹅合规边界。</li>
                        <li><strong>治理结构</strong>：双重股权、股权激励（SBC）与回购抵消度。</li>
                        <li><strong>十年文明确定性</strong>：10年维度是否顺应生产力不可逆趋势。</li>
                        <li><strong>综合治理评级</strong>：长期主义现代化文明视角评级。</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)

        with tab_workflow:
            w_col1, w_col2 = st.columns([1, 1])
            with w_col1:
                st.markdown(f"""
                <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 14px; height: 100%;">
                    <div style="font-size: 0.9rem; font-weight: 700; color: #0f172a; margin-bottom: 8px;">🎯 当前技能工作机制与定位</div>
                    <ul style="font-size: 0.77rem; color: #475569; padding-left: 18px; margin: 0; line-height: 1.6;">
                        <li><strong>当前研究工具</strong>：{skill_icon} {skill_title}</li>
                        <li><strong>所属投研阶段</strong>：{skill_category}</li>
                        <li><strong>执行协作模式</strong>：{"👥 四大师并行 Multi-Agent 协作" if skill_mode == "multi_agent" else ("🌪️ 漏斗分级筛选 Funnel 体系" if skill_mode == "funnel" else "🤖 深度认知推演 Single-Agent 体系")}</li>
                        <li><strong>核心方法论</strong>：{skill_desc}</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            with w_col2:
                st.markdown("""
                <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 14px; height: 100%;">
                    <div style="font-size: 0.9rem; font-weight: 700; color: #0f172a; margin-bottom: 8px;">📋 实战参数填写与交付规范</div>
                    <ul style="font-size: 0.77rem; color: #475569; padding-left: 18px; margin: 0; line-height: 1.6;">
                        <li><strong>标的输入标准</strong>：美股代码 (如 AAPL)、A股6位代码 (如 600519)、港股5位代码 (如 00700)。</li>
                        <li><strong>议题定向强化</strong>：在「重点关注议题」中可指定特定顾虑（如资本开支、反垄断、AI回报率）。</li>
                        <li><strong>本地持久归档</strong>：报告生成后自动在 <code>finmaster/reports/标的名/</code> 创建专属文件夹持久归档。</li>
                        <li><strong>格式规范交付</strong>：支持在结果面板中一键下载专业级 GitHub Flavored Markdown 研报。</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)

        with tab_archive:
            all_arc = archive_manager.scan_all_reports()
            arc_left, arc_right = st.columns([1, 2])
            with arc_left:
                st.metric("知识库已归档公司", f"{all_arc['total_companies']} 家")
                st.metric("收录完整投研报告", f"{all_arc['total_files']} 份")
                st.info("💡 点击左侧导航「📂 历史研报知识库」可直接穿透浏览与下载全量研报。")
            with arc_right:
                st.markdown("**近期核心标的档案速览：**")
                recent_cos = list(all_arc["company_reports"].keys())[:6]
                if recent_cos:
                    for co in recent_cos:
                        file_cnt = len(all_arc["company_reports"][co])
                        st.markdown(f"- 📁 **{co}** · 已归档 {file_cnt} 份报告（含四大师分部报告及最终备忘录）")

        with tab_rules:
            r1, r2, r3 = st.columns(3)
            with r1:
                st.markdown("""
                <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 14px; height: 100%;">
                    <div style="font-size: 0.88rem; font-weight: 700; color: #0f172a; margin-bottom: 6px;">🛡️ 防本地历史数据污染</div>
                    <div style="font-size: 0.76rem; color: #475569; line-height: 1.5;">
                        严禁从本地历史缓存中读取最新股价、市值或财报！所有数据必须经由 Gemini 官方 Google Search 检索官方一手 10-Q / 10-K 与最新收盘行情，并强制注明数据截断时间戳。
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with r2:
                st.markdown("""
                <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 14px; height: 100%;">
                    <div style="font-size: 0.88rem; font-weight: 700; color: #0f172a; margin-bottom: 6px;">🧮 确定性高精度十进制算术</div>
                    <div style="font-size: 0.76rem; color: #475569; line-height: 1.5;">
                        所有市盈率（PE）、扣现金市盈率（Ex-Cash PE）、自由现金流（FCF）测算，一律调用内置纯十进制数学引擎（Decimal），杜绝大模型浮点心算与幻觉漂移。
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with r3:
                st.markdown("""
                <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 14px; height: 100%;">
                    <div style="font-size: 0.88rem; font-weight: 700; color: #0f172a; margin-bottom: 6px;">📋 巴菲特买入前 10 项审查</div>
                    <div style="font-size: 0.76rem; color: #475569; line-height: 1.5;">
                        严格执行巴菲特买入前 Checklist 10 项严格审查表。针对商业模式、财务造血、负债率、受托责任等关键指标实行一票否决制，首要原则永远是保护本金安全。
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # 4. 点击启动后的实时执行与报告渲染
    else:
        if not client.is_configured():
            st.error("❌ 无法启动：未配置有效 Gemini API Key，请在左侧侧边栏设置。")
        else:
            target_name = user_inputs.get("target") or user_inputs.get("holdings") or "研究标的"

            # 4.1 旗舰多 Agent 投研流水线（如 investment-team / earnings-team）
            if skill_mode == "multi_agent" and selected_skill_id in ("investment-team", "earnings-team"):
                st.markdown("### ⏳ 四大师投研流水线执行中...")

                progress_bar = st.progress(5)
                status_text = st.empty()

                c1, c2, c3, c4 = st.columns(4)
                card1 = c1.empty()
                card2 = c2.empty()
                card3 = c3.empty()
                card4 = c4.empty()

                card1.info("🟢 **段永平视角**\n\n等待就绪...")
                card2.info("🔵 **巴菲特视角**\n\n等待就绪...")
                card3.info("🟠 **芒格视角**\n\n等待就绪...")
                card4.info("🟣 **李录视角**\n\n等待就绪...")

                def progress_callback(msg: str, pct: int, extra: Any = None):
                    progress_bar.progress(pct)
                    status_text.markdown(f"**当前状态**：{msg}")
                    if extra and isinstance(extra, dict):
                        role = extra.get("role", "")
                        if "段永平" in role:
                            card1.success("🟢 **段永平视角**\n\n✅ 商业模式分析已完成")
                        elif "巴菲特" in role:
                            card2.success("🔵 **巴菲特视角**\n\n✅ 财务估值审计已完成")
                        elif "芒格" in role:
                            card3.success("🟠 **芒格视角**\n\n✅ 逆向检验已完成")
                        elif "李录" in role:
                            card4.success("🟣 **李录视角**\n\n✅ 治理与文明确定性已完成")

                start_time = time.time()
                results = engine.execute_multi_agent_team(
                    target=target_name,
                    focus=user_inputs.get("focus", ""),
                    on_progress=progress_callback,
                    enable_search=enable_search
                )
                elapsed = time.time() - start_time

                st.success(f"🎉 投研团队流水线执行完毕！总耗时: {elapsed:.1f} 秒。报告已归档至 `finmaster/reports/{target_name}/`")

                tab_final, tab_duan, tab_buffett, tab_munger, tab_lilu = st.tabs([
                    "🏛️ 最终综合决策备忘录",
                    "🟢 段永平商业模式",
                    "🔵 巴菲特财务估值",
                    "🟠 芒格竞争与逆向",
                    "🟣 李录风险与治理"
                ])

                with tab_final:
                    final_content = results.get("05_最终综合报告", "生成失败")
                    is_error = "Gemini API 请求失败" in final_content or "unexpected EOF" in final_content or "HTTP 502" in final_content
                    if is_error:
                        st.markdown("""
                        <div style="background: #fffbeb; border: 1px solid #fde68a; border-radius: 8px; padding: 10px 14px; margin-bottom: 12px; color: #92400e; font-size: 0.8rem; line-height: 1.5;">
                            ⚡ <strong>网络代理通道偶发抖动提示</strong>：四位大师的独立研报均已全部成功生成并安全归档（可点击右侧各标签查阅）。最终决策备忘录在主笔汇总时因代理连接波动中断。
                        </div>
                        """, unsafe_allow_html=True)
                        if st.button("🔄 立即重新综合生成决策备忘录 (基于已有四大师报告，耗时仅需数秒)", type="primary", use_container_width=True):
                            with st.spinner("主笔分析师（Team Lead）正在重新汇总生成最终备忘录..."):
                                new_memo = engine.synthesize_memo(target_name, results, user_inputs.get("focus", ""))
                                results["05_最终综合报告"] = new_memo
                                st.rerun()

                    st.markdown(final_content)
                    st.download_button(
                        "📥 下载最终综合报告 (.md)",
                        data=final_content,
                        file_name=f"{target_name}_最终综合报告.md",
                        mime="text/markdown"
                    )

                with tab_duan:
                    st.markdown(results.get("01_段永平商业模式", ""))

                with tab_buffett:
                    st.markdown(results.get("02_巴菲特财务估值", ""))

                with tab_munger:
                    st.markdown(results.get("03_芒格竞争与逆向", ""))

                with tab_lilu:
                    st.markdown(results.get("04_李录风险与治理", ""))

            # 4.2 单智能体深度分析流式模式（Single-Agent）
            else:
                st.markdown(f"### 📄「{skill_title}」深度研报生成中...")
                status_box = st.status(f"正在启动 {skill_title} 分析引擎...", expanded=True)

                def status_callback(msg: str):
                    status_box.write(msg)

                report_placeholder = st.empty()
                full_text = ""

                for chunk in engine.execute_skill_stream(
                    skill_id=selected_skill_id,
                    user_params=user_inputs,
                    on_status=status_callback,
                    enable_search=enable_search
                ):
                    full_text += chunk
                    report_placeholder.markdown(full_text + " ▌")

                report_placeholder.markdown(full_text)
                status_box.update(label=f"✅ {skill_title} 研究完成！已自动归档至 reports/ 目录", state="complete", expanded=False)

                st.download_button(
                    f"📥 下载「{skill_title}」完整研报 (.md)",
                    data=full_text,
                    file_name=f"{target_name}_{selected_skill_id}.md",
                    mime="text/markdown"
                )

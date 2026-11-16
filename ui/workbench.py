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

    st.markdown(f"""
    <div class="skill-hero-card">
        <div style="display: flex; justify-content: space-between; align-items: center; gap: 16px;">
            <div style="flex: 1;">
                <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 4px;">
                    <span style="font-size: 1.5rem; line-height: 1;">{skill_icon}</span>
                    <span style="font-size: 1.25rem; font-weight: 700; color: #0f172a; letter-spacing: -0.01em;">{skill_title}</span>
                    <span style="font-size: 0.72rem; background: #f1f5f9; color: #475569; padding: 2px 8px; border-radius: 9999px; font-weight: 600;">{skill_category}</span>
                </div>
                <div style="font-size: 0.82rem; color: #475569; line-height: 1.4;">
                    <strong style="color: #1e293b;">核心方法论：</strong>{skill_desc}
                </div>
            </div>
            <div>
                {mode_badge}
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
            st.markdown('<div style="font-size: 0.92rem; font-weight: 700; color: #0f172a; display: flex; align-items: center; gap: 6px;"><span>📝</span> 设定研究参数</div>', unsafe_allow_html=True)
        with p_head_col2:
            st.markdown('<div style="text-align: right; font-size: 0.73rem; color: #64748b;">⚡ 点选下方快捷药丸，秒级填入分析代码</div>', unsafe_allow_html=True)

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

        # 搜索调度模式选择器 (默认：关闭全网搜索，依托 7 大确定性金融底座秒级极速出具)
        st.markdown("""
        <div style="margin-top: 10px; margin-bottom: 5px; font-size: 0.78rem; font-weight: 600; color: #334155;">
            🌐 搜索调度策略
        </div>
        """, unsafe_allow_html=True)
        search_mode_options = [
            "🚫 关闭全网搜索 (默认)",
            "🤖 智能自适应调度",
            "🌐 强制全网搜索"
        ]

        if "workbench_search_mode_idx" not in st.session_state:
            st.session_state["workbench_search_mode_idx"] = 0

        selected_mode_str = st.radio(
            "搜索调度策略",
            search_mode_options,
            index=st.session_state["workbench_search_mode_idx"],
            horizontal=True,
            label_visibility="collapsed"
        )

        if "关闭" in selected_mode_str:
            chosen_search_mode = "off"
            st.session_state["workbench_search_mode_idx"] = 0
            mode_desc = '⚡ <strong>确定性优先</strong>：完全依托 FRED / Tiingo / yfinance / AkShare 等 7 大硬核金融底座，0 次网络检索，秒级极速严谨出具。'
            mode_desc_border = "#bbf7d0"
            mode_desc_bg = "#f0fdf4"
            mode_desc_color = "#166534"
        elif "智能" in selected_mode_str:
            chosen_search_mode = "smart"
            st.session_state["workbench_search_mode_idx"] = 1
            mode_desc = '🤖 <strong>智能自适应</strong>：硬核底座优先；仅在检测到未上市公司、无公开财报或突发黑天鹅舆情诉求时按需激活搜索。'
            mode_desc_border = "#bae6fd"
            mode_desc_bg = "#f0f9ff"
            mode_desc_color = "#0369a1"
        else:
            chosen_search_mode = "on"
            st.session_state["workbench_search_mode_idx"] = 2
            mode_desc = '🌐 <strong>广域全网检索</strong>：除硬核底座外，并发检索全网最新商业新闻、即时研报与突发动态。'
            mode_desc_border = "#fde68a"
            mode_desc_bg = "#fffbeb"
            mode_desc_color = "#92400e"

        st.markdown(f'''
        <div style="font-size: 0.74rem; color: {mode_desc_color}; background: {mode_desc_bg}; border: 1px solid {mode_desc_border}; border-radius: 6px; padding: 6px 12px; margin-top: 3px; margin-bottom: 12px; line-height: 1.45;">
            {mode_desc}
        </div>
        ''', unsafe_allow_html=True)

        # 启动按钮与系统状态栏
        btn_action_col, hint_action_col = st.columns([1.1, 2.9])
        with btn_action_col:
            start_btn = st.button("🚀 启动投研分析", type="primary", use_container_width=True)
        with hint_action_col:
            if not client.is_configured():
                st.warning("👈 请先在左侧侧边栏填入 Gemini API Key 即可启动！")
            else:
                est_time = "8~15s" if skill_mode == "multi_agent" else ("3~5s" if chosen_search_mode == "off" else ("5~10s" if chosen_search_mode == "smart" else "12~20s"))
                st.markdown(f'''
                <div style="display: flex; align-items: center; justify-content: space-between; height: 100%; min-height: 2.4rem; font-size: 0.76rem; color: #475569; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 0 14px;">
                    <span>⚡ <strong>推理引擎</strong>：<span style="color: #059669; font-weight: 600;">{saved_model}</span></span>
                    <span style="color: #cbd5e1;">|</span>
                    <span>🏦 <strong>数据底座</strong>：<span style="color: #1d4ed8; font-weight: 600;">7 大官方源就绪</span></span>
                    <span style="color: #cbd5e1;">|</span>
                    <span>⏱️ <strong>预估耗时</strong>：<span style="color: #0f172a; font-weight: 600;">{est_time}</span></span>
                </div>
                ''', unsafe_allow_html=True)

    # 3. 未点击启动时的常态化工作区（空间充实利用，展示体系架构与知识库联动）
    if not start_btn:
        st.markdown("""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 14px; margin-bottom: 8px;">
            <div style="font-size: 0.94rem; font-weight: 700; color: #1e293b; display: flex; align-items: center; gap: 6px;">
                <span>📋</span> 投研体系架构、知识库联动与分析规范
            </div>
            <div style="font-size: 0.73rem; color: #64748b;">⚡ 点选下方分段标签，切换投研分工、流程规范与知识库</div>
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
                    <div style="font-weight: 700; font-size: 0.94rem; color: #065f46; margin-bottom: 2px;">🟢 段永平视角</div>
                    <div style="font-size: 0.74rem; font-weight: 600; color: #64748b; margin-bottom: 10px;">商业模式与护城河分析师</div>
                    <div style="display: flex; flex-direction: column; gap: 8px;">
                        <div style="font-size: 0.77rem; color: #334155; line-height: 1.55;">
                            <strong style="color: #0f172a;">1. 商业模式本质：</strong>谁付钱？为何买单？边际成本与自由现金流能否持续扩张。
                        </div>
                        <div style="font-size: 0.77rem; color: #334155; line-height: 1.55;">
                            <strong style="color: #0f172a;">2. 五维护城河检验：</strong>品牌用户心智、网络效应、转换成本、独占定价权。
                        </div>
                        <div style="font-size: 0.77rem; color: #334155; line-height: 1.55;">
                            <strong style="color: #0f172a;">3. 业务财报穿透：</strong>分部收入拆解，区分轻资产印钞机与重资产陷阱，出具评级。
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with c2:
                st.markdown("""
                <div class="master-preview-card" style="border-top: 3px solid #3b82f6;">
                    <div style="font-weight: 700; font-size: 0.94rem; color: #1e40af; margin-bottom: 2px;">🔵 巴菲特视角</div>
                    <div style="font-size: 0.74rem; font-weight: 600; color: #64748b; margin-bottom: 10px;">财务造血与估值审计分析师</div>
                    <div style="display: flex; flex-direction: column; gap: 8px;">
                        <div style="font-size: 0.77rem; color: #334155; line-height: 1.55;">
                            <strong style="color: #0f172a;">1. 真实主营与现金流：</strong>剔除浮动损益穿透核心EPS，严审 CapEx 与真自由现金流。
                        </div>
                        <div style="font-size: 0.77rem; color: #334155; line-height: 1.55;">
                            <strong style="color: #0f172a;">2. 资产负债表拆解：</strong>穿透纯流动性现金池，测算扣现金估值 (Ex-Cash PE)。
                        </div>
                        <div style="font-size: 0.77rem; color: #334155; line-height: 1.55;">
                            <strong style="color: #0f172a;">3. 三情景内在价值推演：</strong>结合 5 年估值中枢与折现率，给出严格安全边际估值区间。
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with c3:
                st.markdown("""
                <div class="master-preview-card" style="border-top: 3px solid #f59e0b;">
                    <div style="font-weight: 700; font-size: 0.94rem; color: #92400e; margin-bottom: 2px;">🟠 芒格视角</div>
                    <div style="font-size: 0.74rem; font-weight: 600; color: #64748b; margin-bottom: 10px;">行业竞争与逆向检验分析师</div>
                    <div style="display: flex; flex-direction: column; gap: 8px;">
                        <div style="font-size: 0.77rem; color: #334155; line-height: 1.55;">
                            <strong style="color: #0f172a;">1. 行业终局与范式转移：</strong>推演竞争对手份额拉锯，警惕颠覆性技术与创新者窘境。
                        </div>
                        <div style="font-size: 0.77rem; color: #334155; line-height: 1.55;">
                            <strong style="color: #0f172a;">2. 冷酷逆向思维 (Inversion)：</strong>寻找足以击穿护城河的致命隐患与隐蔽阿喀琉斯之踵。
                        </div>
                        <div style="font-size: 0.77rem; color: #334155; line-height: 1.55;">
                            <strong style="color: #0f172a;">3. 五大毁灭情境推演：</strong>若企业未来利润腰斩甚至断崖，最可能源于哪些不可逆风险。
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with c4:
                st.markdown("""
                <div class="master-preview-card" style="border-top: 3px solid #8b5cf6;">
                    <div style="font-weight: 700; font-size: 0.94rem; color: #5b21b6; margin-bottom: 2px;">🟣 李录视角</div>
                    <div style="font-size: 0.74rem; font-weight: 600; color: #64748b; margin-bottom: 10px;">治理风险与文明确定性分析师</div>
                    <div style="display: flex; flex-direction: column; gap: 8px;">
                        <div style="font-size: 0.77rem; color: #334155; line-height: 1.55;">
                            <strong style="color: #0f172a;">1. 管理层画像与资本配置：</strong>考察受托人品行、危机纠错能力与股东资本配置纪律。
                        </div>
                        <div style="font-size: 0.77rem; color: #334155; line-height: 1.55;">
                            <strong style="color: #0f172a;">2. 治理结构与合规边界：</strong>双重股权结构穿透、SBC 股权稀释与监管反垄断安全边界。
                        </div>
                        <div style="font-size: 0.77rem; color: #334155; line-height: 1.55;">
                            <strong style="color: #0f172a;">3. 十年文明现代化确定性：</strong>跨越 10 年维度，企业是否顺应全球生产力演进与不可逆趋势。
                        </div>
                    </div>
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
                        严禁从本地历史缓存中读取最新股价、市值或财报！所有财务与宏观数据必须直接经由 FRED、Tiingo、yfinance、AkShare 等 7 大官方确定性底座及官方一手 10-Q / 10-K 获取，并强制注明数据截断时间戳。
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
                    enable_search=(chosen_search_mode != "off"),
                    search_mode=chosen_search_mode
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

                try:
                    for chunk in engine.execute_skill_stream(
                        skill_id=selected_skill_id,
                        user_params=user_inputs,
                        on_status=status_callback,
                        enable_search=(chosen_search_mode != "off"),
                        search_mode=chosen_search_mode
                    ):
                        full_text += chunk
                        report_placeholder.markdown(full_text + " ▌")

                    report_placeholder.markdown(full_text)
                    if full_text and "❌" not in full_text[:50] and "流式传输偶发中断" not in full_text:
                        status_box.update(label=f"✅ {skill_title} 研究完成！已自动归档至 reports/ 目录", state="complete", expanded=False)
                    else:
                        status_box.update(label=f"⚠️ {skill_title} 遇到网络中断", state="error", expanded=True)
                except Exception as e:
                    status_box.update(label=f"❌ 执行异常: {str(e)[:50]}", state="error", expanded=True)
                    st.error(f"研报生成中途发生异常: {e}")

                st.download_button(
                    f"📥 下载「{skill_title}」完整研报 (.md)",
                    data=full_text,
                    file_name=f"{target_name}_{selected_skill_id}.md",
                    mime="text/markdown"
                )

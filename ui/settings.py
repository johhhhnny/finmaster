"""
FinMaster UI 系统与数据源设置中心 (Settings & Data Hub Console)
提供大模型推理、联网搜索引擎、官方证券与宏观底座 (yfinance/SEC/FRED)、高阶金融插件 (Finnhub/FMP/Adanos/Tiingo) 配置与全链路连通性体检。
"""
import os
import time
import requests
from typing import Dict, Any, List
import streamlit as st

from engine.config import (
    get_current_config,
    get_search_config,
    get_sec_email,
    get_fred_key,
    get_plugin_keys,
    save_env_config
)
from engine.llm import GeminiClient
from engine.search_provider import search_manager
from engine.data_sources.yfinance_source import yfinance_source
from engine.data_sources.sec_edgar_source import sec_edgar_source
from engine.data_sources.fred_source import fred_source
from engine.data_sources.finnhub_source import finnhub_source
from engine.data_sources.fmp_source import fmp_source
from engine.data_sources.adanos_source import adanos_source
from engine.data_sources.tiingo_source import tiingo_source


def render_settings():
    """渲染系统与数据中台设置控制台主界面"""
    # 1. 获取当前系统配置与环境变量
    saved_key, saved_model, saved_temp = get_current_config()
    saved_provider, saved_tavily = get_search_config()
    saved_sec_email = get_sec_email()
    saved_fred_key = get_fred_key()
    plugin_keys = get_plugin_keys()

    # 初始化 session state 用于存储表单变更状态
    if "cfg_gemini_key" not in st.session_state:
        st.session_state["cfg_gemini_key"] = saved_key
    if "cfg_model" not in st.session_state:
        st.session_state["cfg_model"] = saved_model
    if "cfg_temp" not in st.session_state:
        st.session_state["cfg_temp"] = saved_temp
    if "cfg_provider" not in st.session_state:
        st.session_state["cfg_provider"] = saved_provider
    if "cfg_tavily_key" not in st.session_state:
        st.session_state["cfg_tavily_key"] = saved_tavily
    if "cfg_sec_email" not in st.session_state:
        st.session_state["cfg_sec_email"] = saved_sec_email
    if "cfg_fred_key" not in st.session_state:
        st.session_state["cfg_fred_key"] = saved_fred_key
    if "cfg_finnhub_key" not in st.session_state:
        st.session_state["cfg_finnhub_key"] = plugin_keys.get("finnhub", "")
    if "cfg_fmp_key" not in st.session_state:
        st.session_state["cfg_fmp_key"] = plugin_keys.get("fmp", "")
    if "cfg_adanos_key" not in st.session_state:
        st.session_state["cfg_adanos_key"] = plugin_keys.get("adanos", "")
    if "cfg_tiingo_key" not in st.session_state:
        st.session_state["cfg_tiingo_key"] = plugin_keys.get("tiingo", "")

    # 统计插件就绪状态
    active_plugins = sum(1 for k in ["finnhub", "fmp", "adanos", "tiingo"] if plugin_keys.get(k) and len(plugin_keys[k].strip()) > 3)

    # 2. 顶部控制台 Hero 标题卡片
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%); border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px 24px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.03);">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 16px;">
            <div>
                <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 6px;">
                    <span style="font-size: 1.8rem; line-height: 1;">⚙️</span>
                    <span style="font-size: 1.45rem; font-weight: 800; color: #0f172a; letter-spacing: -0.02em;">系统与金融数据中台控制台</span>
                    <span style="font-size: 0.72rem; background: #e0f2fe; color: #0284c7; padding: 3px 8px; border-radius: 9999px; font-weight: 600;">Data Hub Console</span>
                </div>
                <div style="font-size: 0.85rem; color: #475569; line-height: 1.5;">
                    集中管理大模型推理引擎、互联网搜索调度、三大官方硬核底座 (yfinance/SEC/FRED) 与四大华尔街机构数据插件。所有更改持久化至本地 <code>.env</code> 文件。
                </div>
            </div>
            <div style="display: flex; gap: 10px; align-items: center;">
                <div style="text-align: right; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 6px 14px; box-shadow: 0 1px 2px rgba(0,0,0,0.02);">
                    <div style="font-size: 0.68rem; color: #64748b; font-weight: 600;">核心底座状态</div>
                    <div style="font-size: 0.82rem; font-weight: 700; color: #166534;">🟢 yfinance + SEC + FRED 直连</div>
                </div>
                <div style="text-align: right; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 6px 14px; box-shadow: 0 1px 2px rgba(0,0,0,0.02);">
                    <div style="font-size: 0.68rem; color: #64748b; font-weight: 600;">高阶扩展插件</div>
                    <div style="font-size: 0.82rem; font-weight: 700; color: #0284c7;">🔌 已激活 {active_plugins} / 4</div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 3. 5 个主功能选项卡
    tab_llm, tab_search, tab_core, tab_plugins, tab_health = st.tabs([
        "🤖 大模型推理配置",
        "🌐 联网与搜索引擎",
        "🏛️ 官方硬核数据底座",
        "🔌 高阶金融插件",
        "🩺 全链路连通性体检"
    ])

    # ----------------------------------------------------
    # TAB 1: 大模型推理配置
    # ----------------------------------------------------
    with tab_llm:
        st.markdown('<div style="font-size: 1.05rem; font-weight: 700; color: #0f172a; margin-bottom: 8px;">🤖 Google Gemini 大语言模型与推理超参</div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size: 0.82rem; color: #64748b; margin-bottom: 16px;">配置投研核心推理大脑，支持自定义模型接入与多样性温度调节。</div>', unsafe_allow_html=True)

        col_l1, col_l2 = st.columns([7, 5])
        with col_l1:
            gemini_key_input = st.text_input(
                "Gemini API Key",
                value=st.session_state["cfg_gemini_key"],
                type="password",
                help="前往 Google AI Studio (https://aistudio.google.com/) 免费申请",
                placeholder="AIzaSy..."
            )
            st.session_state["cfg_gemini_key"] = gemini_key_input

            preset_models = [
                "gemini-3.5-flash-lite",
                "gemini-2.5-flash",
                "gemini-2.5-flash-lite",
                "✏️ 自定义模型代码..."
            ]
            current_model = st.session_state["cfg_model"]
            if current_model in preset_models:
                m_idx = preset_models.index(current_model)
            else:
                preset_models.insert(0, current_model)
                m_idx = 0

            selected_m = st.selectbox(
                "推理模型 (推荐 gemini-3.5-flash-lite / gemini-2.5-flash)",
                preset_models,
                index=m_idx,
                help="gemini-3.5-flash-lite 响应极快且推理吞吐量高；gemini-2.5-flash 逻辑更深。"
            )
            if selected_m == "✏️ 自定义模型代码...":
                custom_model_val = st.text_input(
                    "输入自定义 Gemini 模型代码",
                    value=current_model if current_model not in preset_models else "gemini-3.5-flash-lite",
                    placeholder="例如: gemini-3.5-flash-lite"
                )
                st.session_state["cfg_model"] = custom_model_val
            else:
                st.session_state["cfg_model"] = selected_m

        with col_l2:
            st.markdown("""
            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 14px 16px; margin-bottom: 14px;">
                <div style="font-weight: 700; font-size: 0.85rem; color: #1e293b; margin-bottom: 4px;">💡 模型选型与参数建议</div>
                <div style="font-size: 0.78rem; color: #475569; line-height: 1.5;">
                    • <strong>gemini-3.5-flash-lite</strong>: 适合实时四大师辩论与高频财报抽取，兼顾速度与准确度。<br>
                    • <strong>gemini-2.5-flash</strong>: 适合长篇年报深挖与复杂逻辑推演。<br>
                    • <strong>Temperature</strong>: 金融财报与估值分析推荐 <strong>0.1~0.25</strong>，保持数据严谨性与反幻觉。
                </div>
            </div>
            """, unsafe_allow_html=True)

            temp_val = st.slider(
                "多样性温度 (Temperature)",
                min_value=0.0,
                max_value=1.0,
                value=float(st.session_state["cfg_temp"]),
                step=0.05,
                help="值越低，财报计算与推理越严谨客观；值越高，战略发散性越强。"
            )
            st.session_state["cfg_temp"] = temp_val

        st.markdown('<div style="margin-top: 10px;"></div>', unsafe_allow_html=True)
        col_t1, col_t2 = st.columns([3, 9])
        with col_t1:
            if st.button("🔌 单独测试 Gemini 连通性", key="btn_test_gemini", use_container_width=True):
                client = GeminiClient(
                    api_key=st.session_state["cfg_gemini_key"],
                    model=st.session_state["cfg_model"],
                    temperature=st.session_state["cfg_temp"]
                )
                with st.spinner(f"正在测试模型 {st.session_state['cfg_model']} 连通性..."):
                    res = client.test_connection()
                    if res["success"]:
                        st.success(f"✅ {res['message']} (耗时: {res.get('latency_ms', 0):.0f}ms)")
                    else:
                        st.error(f"❌ {res['message']}")
                        with st.expander("详细诊断信息", expanded=True):
                            st.caption(res.get("details", ""))

    # ----------------------------------------------------
    # TAB 2: 联网与搜索引擎
    # ----------------------------------------------------
    with tab_search:
        st.markdown('<div style="font-size: 1.05rem; font-weight: 700; color: #0f172a; margin-bottom: 8px;">🌐 实时互联网财务与新闻搜索引擎</div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size: 0.82rem; color: #64748b; margin-bottom: 16px;">智能多级调度引擎，规避 Gemini 免费层每日 20 次搜索限制，确保投研不中断。</div>', unsafe_allow_html=True)

        provider_map = {
            "auto": "🤖 智能多级调度 (Auto 优先Tavily/原生Google/DDG - 强烈推荐)",
            "tavily": "⚡ Tavily AI 搜索 (推荐 · 1,000次/月 独立免限配额)",
            "google": "🌐 Gemini 原生 Google Search (每日限20次配额)",
            "duckduckgo": "🦆 DuckDuckGo 免费搜索 (免Key极简)",
            "none": "🚫 关闭联网搜索 (仅基于官方底座与模型离线推演)"
        }
        prov_keys = list(provider_map.keys())
        current_p = st.session_state["cfg_provider"]
        p_idx = prov_keys.index(current_p) if current_p in prov_keys else 0

        col_s1, col_s2 = st.columns([7, 5])
        with col_s1:
            selected_prov = st.selectbox(
                "搜索引擎调度策略",
                options=prov_keys,
                format_func=lambda k: provider_map[k],
                index=p_idx,
                help="当 Google Search 每日 20 次用完时，选择 Tavily 或 Auto 调度可彻底摆脱限流！"
            )
            st.session_state["cfg_provider"] = selected_prov

            tavily_key_input = st.text_input(
                "Tavily API Key",
                value=st.session_state["cfg_tavily_key"],
                type="password",
                placeholder="tvly-xxxxxxxxxxxxxxxxxxxx",
                help="前往 https://tavily.com 免费注册获取"
            )
            st.session_state["cfg_tavily_key"] = tavily_key_input

            if selected_prov in ("auto", "tavily") and not tavily_key_input:
                st.warning("⚠️ 推荐配置 Tavily API Key：每月提供 1,000 次免费深度金融检索，且支持 AI 自动摘要生成。")

        with col_s2:
            st.markdown("""
            <div style="background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px; padding: 14px 16px;">
                <div style="font-weight: 700; font-size: 0.85rem; color: #166534; margin-bottom: 4px;">🚀 为什么推荐 Tavily？</div>
                <div style="font-size: 0.78rem; color: #15803d; line-height: 1.5;">
                    • <strong>配额充足</strong>: 免费提供 1,000 次/月，是 Google 每日 20 次的 50 倍！<br>
                    • <strong>零信用卡门槛</strong>: 注册即用，无任何扣费隐患。<br>
                    • <strong>专业金融清洗</strong>: 内置反污染机制，自动过滤无用广告与低质量营销页面。<br>
                    👉 <a href="https://tavily.com" target="_blank" style="color: #0284c7; font-weight: 600;">点击前往 Tavily 官网免费获取 Key</a>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('<div style="margin-top: 10px;"></div>', unsafe_allow_html=True)
        col_st1, col_st2 = st.columns([3, 9])
        with col_st1:
            if st.button("⚡ 测试 Tavily 搜索引擎", key="btn_test_tavily", use_container_width=True):
                if not st.session_state["cfg_tavily_key"]:
                    st.warning("请先填入 Tavily API Key")
                else:
                    with st.spinner("正在向 Tavily 发起测试检索..."):
                        t_res = search_manager.tavily.test_connection(st.session_state["cfg_tavily_key"])
                        if t_res["success"]:
                            st.success(f"⚡ {t_res['message']} (耗时: {t_res.get('latency_ms', 0):.0f}ms)")
                        else:
                            st.error(f"❌ {t_res['message']}")
                            with st.expander("Tavily 错误详情", expanded=True):
                                st.caption(t_res.get("details", ""))

    # ----------------------------------------------------
    # TAB 3: 官方硬核数据底座 (yfinance + SEC EDGAR + FRED)
    # ----------------------------------------------------
    with tab_core:
        st.markdown('<div style="font-size: 1.05rem; font-weight: 700; color: #0f172a; margin-bottom: 8px;">🏛️ 官方硬核数据底座 (yfinance + SEC EDGAR + FRED 联储宏观)</div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size: 0.82rem; color: #64748b; margin-bottom: 16px;">FinMaster 的坚实财务与宏观基石：直接连通全球各大交易所行情、美国证监会披露底稿与美联储主权级利率基准。</div>', unsafe_allow_html=True)

        col_c1, col_c2, col_c3 = st.columns(3)
        with col_c1:
            st.markdown("""
            <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 16px 18px; height: 100%; box-shadow: 0 1px 2px rgba(0,0,0,0.02);">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
                    <div style="font-size: 0.95rem; font-weight: 700; color: #0f172a;">📊 yfinance 实时金融底座</div>
                    <span style="font-size: 0.68rem; background: #ecfdf5; color: #059669; padding: 2px 7px; border-radius: 9999px; font-weight: 600;">🟢 免Key直连</span>
                </div>
                <div style="font-size: 0.76rem; color: #475569; line-height: 1.55;">
                    • <strong>覆盖范围</strong>: 美股 (NYSE/NASDAQ)、港股 (HKEX)、A股 (沪深) 等全球主要市场。<br>
                    • <strong>核心数据</strong>: 实时报价、市值、总股本、流通盘、企业价值 (EV)、52周价格区间。<br>
                    • <strong>三张表透视</strong>: 自动抓取最近 4 个季度的资产负债表、利润表与现金流量表核心科目。<br>
                    • <strong>双通道可靠性</strong>: 内置 <code>fast_info</code> 快速通道降级保护，抵御 Yahoo 服务器波动。
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col_c2:
            st.markdown("""
            <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 16px 18px; height: 100%; box-shadow: 0 1px 2px rgba(0,0,0,0.02);">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
                    <div style="font-size: 0.95rem; font-weight: 700; color: #0f172a;">🏛️ SEC EDGAR 官方披露</div>
                    <span style="font-size: 0.68rem; background: #ecfdf5; color: #059669; padding: 2px 7px; border-radius: 9999px; font-weight: 600;">🟢 免Key直连</span>
                </div>
                <div style="font-size: 0.76rem; color: #475569; line-height: 1.55;">
                    • <strong>官方权威</strong>: 直连美国证券交易委员会 (SEC) 官方公开披露系统，杜绝二次转述偏差。<br>
                    • <strong>法定文件</strong>: 实时抓取上市公司最新 <strong>10-K</strong> (年报)、<strong>10-Q</strong> (季报)、<strong>8-K</strong> (重大公告)。<br>
                    • <strong>官方文件链</strong>: 生成直接跳转 SEC.gov 的真实原始文件链接。<br>
                    • <strong>合规机制</strong>: 内置 SEC 标准 User-Agent 请求头，完全满足官方访问要求。
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col_c3:
            st.markdown("""
            <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 16px 18px; height: 100%; box-shadow: 0 1px 2px rgba(0,0,0,0.02);">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
                    <div style="font-size: 0.95rem; font-weight: 700; color: #0f172a;">🇺🇸 FRED 圣路易斯联储宏观</div>
                    <span style="font-size: 0.68rem; background: #ecfdf5; color: #059669; padding: 2px 7px; border-radius: 9999px; font-weight: 600;">🟢 免Key直连</span>
                </div>
                <div style="font-size: 0.76rem; color: #475569; line-height: 1.55;">
                    • <strong>主权级宏观底座</strong>: 圣路易斯联储官方主权经济数据库 (80万+时序)。<br>
                    • <strong>估值折现锚 (Rf)</strong>: 实时追踪美国 <strong>10年期国债收益率</strong> (DGS10)，作为 DCF 权威折现率。<br>
                    • <strong>宏观衰退雷达</strong>: 监控 <strong>10Y-2Y 美债利差倒挂</strong> (T10Y2Y)，提供经济周期前瞻预警。<br>
                    • <strong>货币定价基准</strong>: 美联储联邦基金有效利率 (FEDFUNDS) 与核心 CPI 通胀。
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('<div style="margin-top: 16px;"></div>', unsafe_allow_html=True)
        col_in1, col_in2 = st.columns(2)
        with col_in1:
            st.markdown('**🛡️ SEC EDGAR 联络声明配置 (可选 · 提升访问优先级)**')
            sec_email_input = st.text_input(
                "SEC 申报联系邮箱",
                value=st.session_state["cfg_sec_email"],
                placeholder="例如: your_name@domain.com (留空则默认使用系统内置合规声明)",
                help="美国 SEC 要求第三方调用方在 User-Agent 中声明机构或个人联系邮箱，用于在系统维护或异常频次时发送友好提醒。"
            )
            st.session_state["cfg_sec_email"] = sec_email_input

        with col_in2:
            st.markdown('**🇺🇸 FRED 专属 API Key (可选 · 留空默认走官方直连通道)**')
            fred_key_input = st.text_input(
                "FRED API Key",
                value=st.session_state["cfg_fred_key"],
                type="password",
                placeholder="例如: 32位十六进制 Key (留空默认启用免密直连通道)",
                help="前往 https://fred.stlouisfed.org/docs/api/api_key.html 免费申请"
            )
            st.session_state["cfg_fred_key"] = fred_key_input

        col_ct1, col_ct2 = st.columns(2)
        with col_ct1:
            if st.button("🧪 测试 yfinance 与 SEC EDGAR 基础数据抓取", key="btn_test_core_data", use_container_width=True):
                with st.spinner("正在连通 yfinance 与 SEC EDGAR 抓取 Apple Inc. 数据..."):
                    t_start = time.time()
                    q_snap = yfinance_source.fetch_data("AAPL")
                    sec_res = sec_edgar_source.fetch_filings("AAPL")
                    dur = (time.time() - t_start) * 1000

                    if q_snap.get("success") and sec_res.get("success"):
                        st.success(f"✅ 股票与证监会底座正常！耗时: {dur:.0f}ms | 股价: ${q_snap.get('price')} | CIK: {sec_res.get('cik')}")
                    else:
                        st.warning(f"⚠️ 抓取完成：yfinance成功={q_snap.get('success')}, SEC成功={sec_res.get('success')}")

        with col_ct2:
            if st.button("🇺🇸 测试 FRED 圣路易斯联储宏观数据通道", key="btn_test_fred", use_container_width=True):
                with st.spinner("正在连通 FRED 宏观底座抓取 10 年期美债收益率与利差..."):
                    f_res = fred_source.test_connection(st.session_state["cfg_fred_key"])
                    if f_res["success"]:
                        st.success(f"✅ {f_res['message']} ({f_res.get('latency_ms', 0):.0f}ms)")
                        if f_res.get("details"):
                            st.caption(f_res["details"])
                    else:
                        st.error(f"❌ {f_res['message']}")

    # ----------------------------------------------------
    # TAB 4: 高阶金融插件 (Finnhub / FMP / Adanos / Tiingo)
    # ----------------------------------------------------
    with tab_plugins:
        st.markdown('<div style="font-size: 1.05rem; font-weight: 700; color: #0f172a; margin-bottom: 8px;">🔌 高阶扩展金融插件 (选配 · 填 Key 即刻激活)</div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size: 0.82rem; color: #64748b; margin-bottom: 16px;">通过接入专业金融 API，将研报维度扩展至华尔街投行一致预期、ROIC 深度拆解、散户情绪/预测盘口及高精度量化复权行情。</div>', unsafe_allow_html=True)

        col_p1, col_p2, col_p3, col_p4 = st.columns(4)

        # 插件 1: Finnhub
        with col_p1:
            st.markdown("""
            <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 14px 16px; margin-bottom: 10px;">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px;">
                    <span style="font-weight: 700; font-size: 0.92rem; color: #0f172a;">🎯 Finnhub 共识</span>
                    <span style="font-size: 0.65rem; background: #f1f5f9; color: #475569; padding: 2px 5px; border-radius: 4px;">60次/分 免费</span>
                </div>
                <div style="font-size: 0.74rem; color: #64748b; line-height: 1.45; min-height: 75px;">
                    • 华尔街买入/持有/卖出评级<br>
                    • 投行目标价中枢与预测区间<br>
                    • 近4季 EPS 财报超预期记录
                </div>
            </div>
            """, unsafe_allow_html=True)
            finnhub_val = st.text_input(
                "Finnhub Key",
                value=st.session_state["cfg_finnhub_key"],
                type="password",
                placeholder="例如: cxxxxxxxxxxxxxxx",
                help="前往 https://finnhub.io 免费注册"
            )
            st.session_state["cfg_finnhub_key"] = finnhub_val
            st.caption("👉 [前往 finnhub.io 注册](https://finnhub.io)")

            if st.button("测试 Finnhub", key="test_finnhub_btn", use_container_width=True):
                if not finnhub_val:
                    st.warning("请先填入 Finnhub Key")
                else:
                    with st.spinner("测试 Finnhub 连通性..."):
                        res_fh = finnhub_source.test_connection(finnhub_val)
                        if res_fh["success"]:
                            st.success(f"✅ {res_fh['message']} ({res_fh.get('latency_ms', 0):.0f}ms)")
                        else:
                            st.error(f"❌ {res_fh['message']}")
                            if res_fh.get("details"):
                                st.caption(res_fh["details"])

        # 插件 2: FMP
        with col_p2:
            st.markdown("""
            <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 14px 16px; margin-bottom: 10px;">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px;">
                    <span style="font-weight: 700; font-size: 0.92rem; color: #0f172a;">🧮 FMP 估值/ROIC</span>
                    <span style="font-size: 0.65rem; background: #f1f5f9; color: #475569; padding: 2px 5px; border-radius: 4px;">250次/天 免费</span>
                </div>
                <div style="font-size: 0.74rem; color: #64748b; line-height: 1.45; min-height: 75px;">
                    • 资本回报率 ROIC 与 ROE<br>
                    • 自动化现金流折现 (DCF) 估值<br>
                    • 业务产品分部营收拆解
                </div>
            </div>
            """, unsafe_allow_html=True)
            fmp_val = st.text_input(
                "FMP Key",
                value=st.session_state["cfg_fmp_key"],
                type="password",
                placeholder="例如: xxxxxxxxxxxxxxxxxxxxxxxx",
                help="前往 https://financialmodelingprep.com 免费注册"
            )
            st.session_state["cfg_fmp_key"] = fmp_val
            st.caption("👉 [前往 financialmodelingprep.com](https://financialmodelingprep.com)")

            if st.button("测试 FMP", key="test_fmp_btn", use_container_width=True):
                if not fmp_val:
                    st.warning("请先填入 FMP Key")
                else:
                    with st.spinner("测试 FMP 连通性 (Stable API)..."):
                        res_fmp = fmp_source.test_connection(fmp_val)
                        if res_fmp["success"]:
                            st.success(f"✅ {res_fmp['message']} ({res_fmp.get('latency_ms', 0):.0f}ms)")
                        else:
                            st.error(f"❌ {res_fmp['message']}")
                            if res_fmp.get("details"):
                                st.caption(res_fmp["details"])

        # 插件 3: Adanos
        with col_p3:
            st.markdown("""
            <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 14px 16px; margin-bottom: 10px;">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px;">
                    <span style="font-weight: 700; font-size: 0.92rem; color: #0f172a;">🔮 Adanos 情绪</span>
                    <span style="font-size: 0.65rem; background: #f1f5f9; color: #475569; padding: 2px 5px; border-radius: 4px;">社区免费</span>
                </div>
                <div style="font-size: 0.74rem; color: #64748b; line-height: 1.45; min-height: 75px;">
                    • Reddit / X 散户讨论热度<br>
                    • 社区看多/看空情绪占比<br>
                    • Polymarket 真实预测市场盘口
                </div>
            </div>
            """, unsafe_allow_html=True)
            adanos_val = st.text_input(
                "Adanos Key",
                value=st.session_state["cfg_adanos_key"],
                type="password",
                placeholder="例如: adanos_xxxxxxxxxxxxxxxx",
                help="前往 https://adanos.org 免费注册"
            )
            st.session_state["cfg_adanos_key"] = adanos_val
            st.caption("👉 [前往 adanos.org 注册](https://adanos.org)")

            if st.button("测试 Adanos", key="test_adanos_btn", use_container_width=True):
                if not adanos_val:
                    st.warning("请先填入 Adanos Key")
                else:
                    with st.spinner("测试 Adanos 连通性..."):
                        res_ad = adanos_source.test_connection(adanos_val)
                        if res_ad["success"]:
                            st.success(f"✅ {res_ad['message']} ({res_ad.get('latency_ms', 0):.0f}ms)")
                        else:
                            st.error(f"❌ {res_ad['message']}")
                            if res_ad.get("details"):
                                st.caption(res_ad["details"])

        # 插件 4: Tiingo
        with col_p4:
            st.markdown("""
            <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 14px 16px; margin-bottom: 10px;">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px;">
                    <span style="font-weight: 700; font-size: 0.92rem; color: #0f172a;">📈 Tiingo 量化复权</span>
                    <span style="font-size: 0.65rem; background: #f1f5f9; color: #475569; padding: 2px 5px; border-radius: 4px;">1000次/天 免费</span>
                </div>
                <div style="font-size: 0.74rem; color: #64748b; line-height: 1.45; min-height: 75px;">
                    • 30年高精度严密清洗日K线<br>
                    • 现金分红与拆股全量除权校正<br>
                    • 充当 yfinance 第二高可靠备用链路
                </div>
            </div>
            """, unsafe_allow_html=True)
            tiingo_val = st.text_input(
                "Tiingo Key",
                value=st.session_state["cfg_tiingo_key"],
                type="password",
                placeholder="例如: xxxxxxxxxxxxxxxxxxxxxxxx",
                help="前往 https://www.tiingo.com 免费注册获取"
            )
            st.session_state["cfg_tiingo_key"] = tiingo_val
            st.caption("👉 [前往 tiingo.com 注册](https://www.tiingo.com)")

            if st.button("测试 Tiingo", key="test_tiingo_btn", use_container_width=True):
                if not tiingo_val:
                    st.warning("请先填入 Tiingo Key")
                else:
                    with st.spinner("测试 Tiingo 连通性..."):
                        res_ti = tiingo_source.test_connection(tiingo_val)
                        if res_ti["success"]:
                            st.success(f"✅ {res_ti['message']} ({res_ti.get('latency_ms', 0):.0f}ms)")
                        else:
                            st.error(f"❌ {res_ti['message']}")
                            if res_ti.get("details"):
                                st.caption(res_ti["details"])

    # ----------------------------------------------------
    # TAB 5: 全链路连通性体检
    # ----------------------------------------------------
    with tab_health:
        st.markdown('<div style="font-size: 1.05rem; font-weight: 700; color: #0f172a; margin-bottom: 8px;">🩺 全链路数据源连通性体检中心</div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size: 0.82rem; color: #64748b; margin-bottom: 16px;">一键测试模型、搜索引擎、三大核心财务与宏观底座及四大高阶插件，出具全景健康体检报告。</div>', unsafe_allow_html=True)

        if st.button("🩺 立即执行全链路一键体检", key="btn_run_full_health_check", type="primary"):
            progress_bar = st.progress(0, text="正在启动全链路健康诊断...")
            results: List[Dict[str, Any]] = []

            # 1. Gemini
            progress_bar.progress(12, text="[1/8] 测试 Gemini 大模型推理连通性...")
            client = GeminiClient(
                api_key=st.session_state["cfg_gemini_key"],
                model=st.session_state["cfg_model"],
                temperature=0.0
            )
            res_gemini = client.test_connection()
            results.append({
                "name": "Gemini 推理模型",
                "target": st.session_state["cfg_model"],
                "success": res_gemini["success"],
                "latency_ms": res_gemini.get("latency_ms", 0),
                "msg": res_gemini["message"],
                "badge": "LLM 推理"
            })

            # 2. Tavily Search
            progress_bar.progress(25, text="[2/8] 测试 Tavily 搜索引擎连通性...")
            if st.session_state["cfg_tavily_key"]:
                res_tavily = search_manager.tavily.test_connection(st.session_state["cfg_tavily_key"])
                results.append({
                    "name": "Tavily AI 搜索",
                    "target": "tavily.com",
                    "success": res_tavily["success"],
                    "latency_ms": res_tavily.get("latency_ms", 0),
                    "msg": res_tavily["message"],
                    "badge": "联网检索"
                })
            else:
                results.append({
                    "name": "Tavily AI 搜索",
                    "target": "tavily.com",
                    "success": None,
                    "latency_ms": 0,
                    "msg": "未配置 TAVILY_API_KEY (可选用)",
                    "badge": "联网检索"
                })

            # 3. yfinance
            progress_bar.progress(38, text="[3/8] 测试 yfinance 官方行情与财报底座...")
            t_s = time.time()
            try:
                yf_snap = yfinance_source.fetch_data("AAPL")
                yf_lat = (time.time() - t_s) * 1000
                results.append({
                    "name": "yfinance 财务底座",
                    "target": "query1.finance.yahoo.com",
                    "success": yf_snap.get("success", False),
                    "latency_ms": yf_lat,
                    "msg": f"实时报价成功: ${yf_snap.get('price')} (AAPL)" if yf_snap.get("success") else "行情抓取异常",
                    "badge": "行情与三张表"
                })
            except Exception as e:
                results.append({
                    "name": "yfinance 财务底座",
                    "target": "query1.finance.yahoo.com",
                    "success": False,
                    "latency_ms": (time.time() - t_s) * 1000,
                    "msg": str(e)[:80],
                    "badge": "行情与三张表"
                })

            # 4. SEC EDGAR
            progress_bar.progress(50, text="[4/8] 测试 SEC EDGAR 美国证监会披露系统...")
            t_s = time.time()
            try:
                sec_snap = sec_edgar_source.fetch_filings("AAPL")
                sec_lat = (time.time() - t_s) * 1000
                results.append({
                    "name": "SEC EDGAR 披露引擎",
                    "target": "data.sec.gov",
                    "success": sec_snap.get("success", False),
                    "latency_ms": sec_lat,
                    "msg": f"抓取成功: CIK {sec_snap.get('cik')} (最新 10-K/10-Q 正常)" if sec_snap.get("success") else "SEC 抓取异常",
                    "badge": "官方披露"
                })
            except Exception as e:
                results.append({
                    "name": "SEC EDGAR 披露引擎",
                    "target": "data.sec.gov",
                    "success": False,
                    "latency_ms": (time.time() - t_s) * 1000,
                    "msg": str(e)[:80],
                    "badge": "官方披露"
                })

            # 5. FRED
            progress_bar.progress(62, text="[5/8] 测试 FRED 圣路易斯联储主权宏观底座...")
            res_fred = fred_source.test_connection(st.session_state["cfg_fred_key"])
            results.append({
                "name": "FRED 联储宏观底座",
                "target": "stlouisfed.org",
                "success": res_fred["success"],
                "latency_ms": res_fred.get("latency_ms", 0),
                "msg": res_fred["message"],
                "badge": "宏观基准Rf"
            })

            # 6. Finnhub
            progress_bar.progress(72, text="[6/8] 测试 Finnhub 投行共识插件...")
            if st.session_state["cfg_finnhub_key"]:
                res_fh = finnhub_source.test_connection(st.session_state["cfg_finnhub_key"])
                results.append({
                    "name": "Finnhub 投行共识",
                    "target": "finnhub.io",
                    "success": res_fh["success"],
                    "latency_ms": res_fh.get("latency_ms", 0),
                    "msg": res_fh["message"],
                    "badge": "高阶插件"
                })
            else:
                results.append({
                    "name": "Finnhub 投行共识",
                    "target": "finnhub.io",
                    "success": None,
                    "latency_ms": 0,
                    "msg": "未配置 Key (选配)",
                    "badge": "高阶插件"
                })

            # 7. FMP
            progress_bar.progress(82, text="[7/8] 测试 FMP ROIC 与 DCF 插件...")
            if st.session_state["cfg_fmp_key"]:
                res_fmp = fmp_source.test_connection(st.session_state["cfg_fmp_key"])
                results.append({
                    "name": "FMP ROIC/DCF",
                    "target": "financialmodelingprep.com",
                    "success": res_fmp["success"],
                    "latency_ms": res_fmp.get("latency_ms", 0),
                    "msg": res_fmp["message"],
                    "badge": "高阶插件"
                })
            else:
                results.append({
                    "name": "FMP ROIC/DCF",
                    "target": "financialmodelingprep.com",
                    "success": None,
                    "latency_ms": 0,
                    "msg": "未配置 Key (选配)",
                    "badge": "高阶插件"
                })

            # 8. Adanos
            progress_bar.progress(92, text="[8/8] 测试 Adanos 情绪与预测盘口插件...")
            if st.session_state["cfg_adanos_key"]:
                res_ad = adanos_source.test_connection(st.session_state["cfg_adanos_key"])
                results.append({
                    "name": "Adanos 情绪与预测",
                    "target": "api.adanos.org",
                    "success": res_ad["success"],
                    "latency_ms": res_ad.get("latency_ms", 0),
                    "msg": res_ad["message"],
                    "badge": "高阶插件"
                })
            else:
                results.append({
                    "name": "Adanos 情绪与预测",
                    "target": "api.adanos.org",
                    "success": None,
                    "latency_ms": 0,
                    "msg": "未配置 Key (选配)",
                    "badge": "高阶插件"
                })

            # 9. Tiingo (若配置)
            if st.session_state["cfg_tiingo_key"]:
                res_ti = tiingo_source.test_connection(st.session_state["cfg_tiingo_key"])
                results.append({
                    "name": "Tiingo 量化复权行情",
                    "target": "api.tiingo.com",
                    "success": res_ti["success"],
                    "latency_ms": res_ti.get("latency_ms", 0),
                    "msg": res_ti["message"],
                    "badge": "高阶插件"
                })

            progress_bar.progress(100, text="✅ 全链路体检完成！")
            time.sleep(0.3)
            progress_bar.empty()

            # 渲染体检仪表盘
            st.markdown('<div style="margin-top: 16px;"></div>', unsafe_allow_html=True)
            for r in results:
                if r["success"] is True:
                    status_badge = '<span style="color: #166534; background: #dcfce7; border: 1px solid #bbf7d0; padding: 2px 8px; border-radius: 9999px; font-size: 0.75rem; font-weight: 700;">🟢 正常</span>'
                elif r["success"] is False:
                    status_badge = '<span style="color: #991b1b; background: #fee2e2; border: 1px solid #fecaca; padding: 2px 8px; border-radius: 9999px; font-size: 0.75rem; font-weight: 700;">🔴 异常</span>'
                else:
                    status_badge = '<span style="color: #64748b; background: #f1f5f9; border: 1px solid #e2e8f0; padding: 2px 8px; border-radius: 9999px; font-size: 0.75rem; font-weight: 700;">⚪ 未启用</span>'

                lat_str = f"{r['latency_ms']:.0f} ms" if r["latency_ms"] > 0 else "-"

                st.markdown(f"""
                <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px 16px; margin-bottom: 8px; display: flex; align-items: center; justify-content: space-between;">
                    <div style="display: flex; align-items: center; gap: 12px;">
                        <span style="font-weight: 700; font-size: 0.88rem; color: #0f172a; min-width: 140px;">{r['name']}</span>
                        <span style="font-size: 0.72rem; background: #f8fafc; color: #64748b; padding: 2px 6px; border-radius: 4px; border: 1px solid #e2e8f0;">{r['badge']}</span>
                        <span style="font-size: 0.8rem; color: #334155;">{r['msg']}</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 16px;">
                        <span style="font-size: 0.78rem; color: #64748b; font-family: monospace;">{lat_str}</span>
                        {status_badge}
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # 4. 底部统一保存浮动/固定操作栏 (Save Action Bar)
    st.markdown('<hr style="margin: 24px 0 16px 0; border: none; border-top: 1px solid #e2e8f0;">', unsafe_allow_html=True)
    save_col1, save_col2, save_col3 = st.columns([6, 3, 3])
    with save_col1:
        st.markdown("""
        <div style="font-size: 0.8rem; color: #64748b; line-height: 1.5; padding-top: 6px;">
            💾 点击右侧按钮将当前所有选项卡配置同步持久化至本地 <code>finmaster/.env</code> 并刷新运行内存。
        </div>
        """, unsafe_allow_html=True)

    with save_col2:
        if st.button("🔄 放弃修改并重置", use_container_width=True):
            st.session_state["cfg_gemini_key"] = saved_key
            st.session_state["cfg_model"] = saved_model
            st.session_state["cfg_temp"] = saved_temp
            st.session_state["cfg_provider"] = saved_provider
            st.session_state["cfg_tavily_key"] = saved_tavily
            st.session_state["cfg_sec_email"] = saved_sec_email
            st.session_state["cfg_fred_key"] = saved_fred_key
            st.session_state["cfg_finnhub_key"] = plugin_keys.get("finnhub", "")
            st.session_state["cfg_fmp_key"] = plugin_keys.get("fmp", "")
            st.session_state["cfg_adanos_key"] = plugin_keys.get("adanos", "")
            st.session_state["cfg_tiingo_key"] = plugin_keys.get("tiingo", "")
            st.toast("已重置为上次保存的状态")
            st.rerun()

    with save_col3:
        if st.button("💾 保存全部配置并生效", type="primary", use_container_width=True):
            save_env_config(
                key=st.session_state["cfg_gemini_key"],
                model=st.session_state["cfg_model"],
                temp=float(st.session_state["cfg_temp"]),
                tavily_key=st.session_state["cfg_tavily_key"],
                search_provider=st.session_state["cfg_provider"],
                sec_email=st.session_state["cfg_sec_email"],
                finnhub_key=st.session_state["cfg_finnhub_key"],
                fmp_key=st.session_state["cfg_fmp_key"],
                adanos_key=st.session_state["cfg_adanos_key"],
                fred_key=st.session_state["cfg_fred_key"],
                tiingo_key=st.session_state["cfg_tiingo_key"]
            )
            st.toast("✅ 全局配置已成功保存至 .env 并立即生效！", icon="🎉")
            time.sleep(0.4)
            st.rerun()

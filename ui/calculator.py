"""
FinMaster UI 金融严谨性计算器模块
基于 tools/financial_rigor.py 的高精度纯十进制数学运算，杜绝浮点误差与大模型心算漂移。
"""
from decimal import Decimal

import streamlit as st

from tools.calculator_math import (
    calculate_market_cap_check,
    calculate_scenario,
    calculate_valuation_metrics,
    decimal_value,
)

def render_calculator():
    """渲染金融严谨性计算器主界面"""
    # 1. 顶部整合式计算器看板卡片 (Hero Banner Card)
    st.markdown("""
    <div class="skill-hero-card">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 16px;">
            <div style="flex: 1;">
                <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 6px;">
                    <span style="font-size: 1.6rem; line-height: 1;">🧮</span>
                    <span style="font-size: 1.32rem; font-weight: 700; color: #0f172a; letter-spacing: -0.01em;">金融严谨性计算器</span>
                    <span style="font-size: 0.72rem; background: #f1f5f9; color: #475569; padding: 2px 8px; border-radius: 9999px; font-weight: 600;">确定性纯十进制 Decimal 引擎</span>
                </div>
                <div style="font-size: 0.83rem; color: #475569; line-height: 1.45;">
                    <strong style="color: #1e293b;">计算器定位：</strong>严格基于 <code>tools/calculator_math.py</code> 的纯十进制确定性数学验算。涵盖核心主营扣现金市盈率测算、市值总股本配比稽核及三情景收益推演，彻底杜绝浮点误差与大模型心算漂移。
                </div>
            </div>
            <div style="display: flex; flex-direction: column; align-items: flex-end; gap: 6px;">
                <span style="font-size: 0.72rem; font-weight: 600; color: #047857; background: #ecfdf5; border: 1px solid #a7f3d0; padding: 3px 8px; border-radius: 6px;">
                    🧮 纯十进制 Decimal 运算
                </span>
                <span style="font-size: 0.72rem; color: #1d4ed8; background: #eff6ff; border: 1px solid #bfdbfe; padding: 3px 8px; border-radius: 6px; font-weight: 600;">
                    🛡️ 杜绝浮点误差与心算幻觉
                </span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    calc_tab1, calc_tab2, calc_tab3 = st.tabs([
        "📊 核心估值与扣现金市盈率 (Ex-Cash PE)",
        "🌐 市值与总股本严谨匹配稽核",
        "🎯 未来三年目标股价推演 (Three-Scenario Model)"
    ])

    # -------------------------------------------------------------------------
    # TAB 1: 核心估值与扣现金市盈率 (Ex-Cash PE) 验算
    # -------------------------------------------------------------------------
    with calc_tab1:
        try:
            tab1_box = st.container(border=True)
        except TypeError:
            tab1_box = st.container()

        with tab1_box:
            # 顶部快捷载入栏
            h1_col1, h1_col2 = st.columns([1.5, 3.5])
            with h1_col1:
                st.markdown('<div style="font-size: 0.94rem; font-weight: 700; color: #0f172a; margin-top: 3px;">📝 输入估值测算参数</div>', unsafe_allow_html=True)
            with h1_col2:
                st.caption("⚡ **1 键载入标的基准财务数据**：")
                q_cols = st.columns(5)
                presets = [
                    ("🔍 谷歌 GOOGL", 295.77, 10.90, 55.00, 8.10),
                    ("🍎 苹果 AAPL", 228.50, 6.08, 4.80, 4.10),
                    ("⚡ 特斯拉 TSLA", 214.00, 2.14, 21.00, 9.20),
                    ("🍶 贵州茅台", 1450.00, 61.20, 190.00, 145.00),
                    ("🐧 腾讯控股", 410.00, 19.50, 115.00, 38.00)
                ]
                for p_idx, (p_name, p_p, p_eps, p_bvps, p_cash) in enumerate(presets):
                    with q_cols[p_idx]:
                        if st.button(p_name, key=f"calc_p_{p_idx}", use_container_width=True):
                            st.session_state["calc_p"] = p_p
                            st.session_state["calc_eps"] = p_eps
                            st.session_state["calc_bvps"] = p_bvps
                            st.session_state["calc_cash"] = p_cash
                            st.rerun()

            # 输入表单行
            c_in1, c_in2, c_in3, c_in4 = st.columns(4)
            with c_in1:
                p_val = st.number_input("最新收盘股价 ($)", value=st.session_state.get("calc_p", 295.77), step=1.0)
            with c_in2:
                eps_val = st.number_input("真实核心主营 EPS ($)", value=st.session_state.get("calc_eps", 10.90), step=0.1)
            with c_in3:
                bvps_val = st.number_input("每股净资产 BVPS ($)", value=st.session_state.get("calc_bvps", 55.00), step=1.0)
            with c_in4:
                cash_val = st.number_input("每股纯流动现金 ($)", value=st.session_state.get("calc_cash", 8.10), step=0.1)

            st.markdown('<div style="height: 1px; background: #e2e8f0; margin: 14px 0 16px 0;"></div>', unsafe_allow_html=True)

            # KPI 指标卡片
            try:
                metrics = calculate_valuation_metrics(p_val, eps_val, bvps_val, cash_val)
            except ValueError as exc:
                st.error(f"无法计算估值指标：{exc}")
            else:
                pe = metrics["pe"]
                ex_cash_pe = metrics["ex_cash_pe"]
                pb = metrics["pb"]
                roe = metrics["roe"]
                ey = metrics["earnings_yield"]
                cash_discount = metrics["cash_discount"]

                st.markdown('<div style="font-size: 0.9rem; font-weight: 700; color: #0f172a; margin-bottom: 10px;">📊 核心估值与造血指标矩阵</div>', unsafe_allow_html=True)
                m1, m2, m3, m4, m5 = st.columns(5)
                m1.metric("名义主营 PE", f"{pe:.2f}x")
                m2.metric("扣现金核心 PE (Ex-Cash)", f"{ex_cash_pe:.2f}x", delta=f"-{cash_discount:.2f}x (现金增厚)")
                m3.metric("盈利收益率 (E/P)", f"{ey:.2f}%")
                m4.metric("市净率 PB", f"{pb:.2f}x")
                m5.metric("核心经营 ROE", f"{roe:.2f}%")

                # 巴菲特安全边际透视卡片
                ev_per_share = metrics["enterprise_value_per_share"]
                if ex_cash_pe <= 22:
                    safety_status = "🟢 显著具备安全边际 · 处于公道偏低价值区间（强力增持/买入观察）"
                    status_color = "#047857"
                    status_bg = "#ecfdf5"
                    status_border = "#a7f3d0"
                elif ex_cash_pe <= 28:
                    safety_status = "🔵 估值公道合理 · 符合巴菲特「以公道价格买入卓越公司」理念"
                    status_color = "#1d4ed8"
                    status_bg = "#eff6ff"
                    status_border = "#bfdbfe"
                else:
                    safety_status = "🟡 估值充分定价或偏高 · 建议保持耐心，等待更充裕的安全边际"
                    status_color = "#b45309"
                    status_bg = "#fffbeb"
                    status_border = "#fde68a"

                st.markdown(f"""
                <div style="background: {status_bg}; border: 1px solid {status_border}; border-radius: 8px; padding: 14px 18px; margin-top: 14px;">
                    <div style="font-weight: 700; font-size: 0.88rem; color: {status_color}; margin-bottom: 6px;">
                        🛡️ 巴菲特安全边际透视结论：{safety_status}
                    </div>
                    <div style="font-size: 0.78rem; color: #334155; line-height: 1.6;">
                        • <strong>扣现金企业价值（EV per share）</strong>: <strong>${ev_per_share:.2f}</strong>（股票总价 ${p_val:.2f} 扣除账面可立即清偿现金 ${cash_val:.2f}）<br>
                        • <strong>扣现金市盈率（Ex-Cash PE）</strong>: <strong>{ex_cash_pe:.2f}x</strong>，比名义 PE 压低 <strong>{cash_discount:.2f}x</strong>，大幅还原企业真实造血倍数<br>
                        • <strong>资本配置逻辑</strong>: 若企业持续进行防稀释股票回购，扣现金估值的安全垫将逐季自动增厚。
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # TAB 2: 市值与总股本严谨匹配稽核
    # -------------------------------------------------------------------------
    with calc_tab2:
        try:
            tab2_box = st.container(border=True)
        except TypeError:
            tab2_box = st.container()

        with tab2_box:
            st.markdown('<div style="font-size: 0.94rem; font-weight: 700; color: #0f172a; margin-bottom: 6px;">🌐 股票单价与总股本推导稽核</div>', unsafe_allow_html=True)
            st.markdown("""
            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 10px 14px; font-size: 0.78rem; color: #475569; margin-bottom: 14px;">
                📐 <strong>稽核公式</strong>：理论精确推导市值 = 股票单价 (Price) × 稀释总股本数 (Diluted Shares)。偏差阈值严守 <strong>≤ 1.0%</strong>。
            </div>
            """, unsafe_allow_html=True)

            col_mc1, col_mc2, col_mc3 = st.columns(3)
            with col_mc1:
                m_price = st.number_input("股票单价 ($)", value=295.77, step=1.0, key="mc_p")
            with col_mc2:
                m_shares = st.number_input("总股本数 (股)", value=12350000000, step=10000000, key="mc_s")
            with col_mc3:
                m_reported = st.number_input("报告披露市值 ($)", value=3653000000000, step=1000000000, key="mc_r")

            try:
                calc_cap, diff_pct = calculate_market_cap_check(m_price, m_shares, m_reported)
            except ValueError as exc:
                st.error(f"无法完成市值稽核：{exc}")
            else:
                st.markdown('<div style="height: 1px; background: #e2e8f0; margin: 12px 0 14px 0;"></div>', unsafe_allow_html=True)

                res_col1, res_col2 = st.columns(2)
                res_col1.metric("精确数学推导市值", f"${calc_cap / Decimal('1e12'):.3f} 万亿")
                reported_cap = decimal_value(m_reported)
                res_col2.metric("报告披露市值", f"${reported_cap / Decimal('1e12'):.3f} 万亿", delta=f"偏差率 {diff_pct:.2f}%")

                if diff_pct <= Decimal("1.0"):
                    st.markdown(f"""
                    <div style="background: #ecfdf5; border: 1px solid #a7f3d0; border-radius: 6px; padding: 10px 14px; color: #047857; font-size: 0.78rem; font-weight: 600; margin-top: 10px;">
                        ✅ 稽核通过：推导市值与披露市值高度契合（偏差 {diff_pct:.2f}% ≤ 1.0%），请仍以原始披露来源为准。
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="background: #fffbeb; border: 1px solid #fde68a; border-radius: 6px; padding: 10px 14px; color: #b45309; font-size: 0.78rem; font-weight: 600; margin-top: 10px;">
                        ⚠️ 稽核提示：计算偏差达 {diff_pct:.2f}% > 1.0%，请重点核查：1) 股本是否使用了未稀释 Basic Shares 代替了 Diluted Shares；2) 标的近期是否存在拆股、反向拆股或大规模回购注销。
                    </div>
                    """, unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # TAB 3: 未来三年目标股价推演 (Three-Scenario Model)
    # -------------------------------------------------------------------------
    with calc_tab3:
        try:
            tab3_box = st.container(border=True)
        except TypeError:
            tab3_box = st.container()

        with tab3_box:
            st.markdown('<div style="font-size: 0.94rem; font-weight: 700; color: #0f172a; margin-bottom: 6px;">🎯 未来收益率多情景预测模型 (Bull / Base / Bear)</div>', unsafe_allow_html=True)

            sc_col1, sc_col2 = st.columns(2)
            with sc_col1:
                base_p = st.number_input("基准当前价格 ($)", value=295.77, step=1.0, key="sc_p")
                base_eps = st.number_input("基准当前主营 EPS ($)", value=10.90, step=0.1, key="sc_eps")
            with sc_col2:
                sc_years = st.slider("预测退出年限 (年)", 1, 5, 3)

            sc_data = [
                {"情景": "🟢 乐观 (Bull)", "年化增速": "0.20", "目标PE": "30", "描述": "核心主营超预期增长，高毛利业务占比提升，估值中枢扩张"},
                {"情景": "🔵 中性 (Base)", "年化增速": "0.14", "目标PE": "24", "描述": "稳态成长，资本开支良性转化，估值维持历史5年中枢"},
                {"情景": "🔴 悲观 (Bear)", "年化增速": "0.05", "目标PE": "18", "描述": "竞争加剧份额承压，技术换代带来折旧压力，估值压缩"}
            ]

            st.markdown(f'<div style="font-size: 0.88rem; font-weight: 700; color: #0f172a; margin-top: 14px; margin-bottom: 8px;">未来 {sc_years} 年预期收益矩阵 (Compound Growth Matrix)：</div>', unsafe_allow_html=True)
            try:
                sc_rows = []
                for scenario in sc_data:
                    growth = decimal_value(scenario["年化增速"])
                    exit_pe = decimal_value(scenario["目标PE"])
                    result = calculate_scenario(base_p, base_eps, growth, exit_pe, sc_years)
                    gain_pct = result["gain_pct"]
                    cagr_pct = result["cagr_pct"]
                    sc_rows.append({
                        "情景": scenario["情景"],
                        "年均 EPS 复合增速": f"{growth * Decimal('100'):.1f}%",
                        "退出目标 PE": f"{exit_pe:.0f}x",
                        f"{sc_years}年后预期 EPS": f"${result['future_eps']:.2f}",
                        "推导目标股价": f"${result['target_price']:.2f}",
                        "累计涨跌幅": f"{'+' if gain_pct > 0 else ''}{gain_pct:.1f}%",
                        "年化预期回报 (CAGR)": f"{'+' if cagr_pct > 0 else ''}{cagr_pct:.1f}%"
                    })
            except ValueError as exc:
                st.error(f"无法完成情景推演：{exc}")
            else:
                st.table(sc_rows)

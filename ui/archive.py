"""
FinMaster UI 历史研报知识库模块
负责穿透检索、分级浏览与多格式导出本地已归档的投研报告。
"""
import os
import datetime
import streamlit as st

from engine.archive_manager import archive_manager

def render_archive():
    """渲染历史研报知识库主界面"""
    all_raw_data = archive_manager.scan_all_reports()
    total_cos = all_raw_data.get("total_companies", 0)
    total_files = all_raw_data.get("total_files", 0)

    # 1. 顶部整合式知识库看板卡片 (Hero Banner Card)
    st.markdown(f"""
    <div class="skill-hero-card">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 16px;">
            <div style="flex: 1;">
                <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 6px;">
                    <span style="font-size: 1.6rem; line-height: 1;">📂</span>
                    <span style="font-size: 1.32rem; font-weight: 700; color: #0f172a; letter-spacing: -0.01em;">历史研报知识库</span>
                    <span style="font-size: 0.72rem; background: #f1f5f9; color: #475569; padding: 2px 8px; border-radius: 9999px; font-weight: 600;">覆盖 {total_cos} 家核心公司 · 收录 {total_files} 份完整研报</span>
                </div>
                <div style="font-size: 0.83rem; color: #475569; line-height: 1.45;">
                    <strong style="color: #1e293b;">知识库定位：</strong>全景检索、分级浏览与穿透查阅已归档的公司专项研究备忘录、四大师分部研报及宏观专题长文。支持一键导出 Markdown 原件。
                </div>
            </div>
            <div style="display: flex; flex-direction: column; align-items: flex-end; gap: 6px;">
                <span style="font-size: 0.72rem; font-weight: 600; color: #1d4ed8; background: #eff6ff; border: 1px solid #bfdbfe; padding: 3px 8px; border-radius: 6px;">
                    📚 本地沉淀资产
                </span>
                <span style="font-size: 0.72rem; color: #059669; background: #ecfdf5; border: 1px solid #a7f3d0; padding: 3px 8px; border-radius: 6px; font-weight: 600;">
                    🔒 严防数据污染 · 只读沉淀档案
                </span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 2. 检索控制台与高频核心标的快捷筛选 (Search & Filter Card)
    try:
        search_card = st.container(border=True)
    except TypeError:
        search_card = st.container()

    with search_card:
        sc_col1, sc_col2 = st.columns([3, 1])
        with sc_col1:
            search_val = st.session_state.get("archive_search_kw", "")
            search_kw = st.text_input(
                "🔍 全局全文与标的检索",
                value=search_val,
                placeholder="输入标的代码、公司名称或研报议题关键字（例如: 谷歌, 腾讯, 苹果, AI基建...）",
                label_visibility="collapsed"
            )
        with sc_col2:
            st.markdown(f"""
            <div style="display: flex; justify-content: flex-end; align-items: center; height: 100%; font-size: 0.76rem; color: #64748b; padding-top: 4px;">
                <span>已索引档案：<strong style="color: #0f172a;">{total_cos}</strong> 家</span>
                <span style="margin: 0 6px;">·</span>
                <span>研报总量：<strong style="color: #1d4ed8;">{total_files}</strong> 份</span>
            </div>
            """, unsafe_allow_html=True)

        # 高频核心公司快捷筛选胶囊
        st.caption("⚡ **高频核心标的快速穿透**：")
        q_cols = st.columns(7)
        quick_chips = [
            ("全部标的", ""),
            ("谷歌 GOOGL", "谷歌"),
            ("苹果 AAPL", "苹果"),
            ("特斯拉 TSLA", "特斯拉"),
            ("贵州茅台", "贵州茅台"),
            ("腾讯控股", "腾讯"),
            ("伯克希尔", "伯克希尔")
        ]
        for idx, (chip_label, chip_val) in enumerate(quick_chips):
            with q_cols[idx]:
                if st.button(chip_label, key=f"arc_chip_{idx}", use_container_width=True):
                    st.session_state["archive_search_kw"] = chip_val
                    st.rerun()

    archive_data = archive_manager.filter_reports(search_kw)

    # 3. 左右分栏：左侧标的与研报列表，右侧沉浸式研报阅读器
    list_col, view_col = st.columns([1.1, 2.3])

    with list_col:
        try:
            tree_box = st.container(border=True)
        except TypeError:
            tree_box = st.container()

        with tree_box:
            st.markdown('<div style="font-size: 0.92rem; font-weight: 700; color: #0f172a; margin-bottom: 8px;">📁 标的档案与研报列表</div>', unsafe_allow_html=True)
            companies = list(archive_data["company_reports"].keys())

            if not companies and not archive_data["topic_reports"]:
                st.info("🔍 未找到匹配的归档研报，请调整搜索关键字。")
                selected_file_path = None
            else:
                default_target = "谷歌" if "谷歌" in companies else (companies[0] if companies else "")
                selected_company = st.selectbox(
                    "选择目标公司或专题合辑",
                    options=companies + (["【专题长文合辑】"] if archive_data["topic_reports"] else []),
                    index=companies.index(default_target) if default_target in companies else 0,
                    label_visibility="collapsed"
                )

                if selected_company == "【专题长文合辑】":
                    files_to_show = archive_data["topic_reports"]
                else:
                    files_to_show = archive_data["company_reports"].get(selected_company, [])

                st.markdown(f'<div style="font-size: 0.74rem; color: #64748b; margin-top: 8px; margin-bottom: 4px;">收录 <strong>{len(files_to_show)}</strong> 份专项研究文件：</div>', unsafe_allow_html=True)

                def format_file_label(f_item: dict) -> str:
                    fn = f_item["name"]
                    sz = f_item["size_kb"]
                    if f_item.get("is_final") or "最终" in fn:
                        prefix = "⭐ 最终决策备忘录"
                    elif "01" in fn or "段永平" in fn:
                        prefix = "🟢 段永平视角"
                    elif "02" in fn or "巴菲特" in fn:
                        prefix = "🔵 巴菲特视角"
                    elif "03" in fn or "芒格" in fn:
                        prefix = "🟠 芒格视角"
                    elif "04" in fn or "李录" in fn:
                        prefix = "🟣 李录视角"
                    elif "baseline" in fn.lower():
                        prefix = "📊 数据基线核验"
                    else:
                        prefix = "📑 专题研究"
                    return f"{prefix} · {fn} ({sz} KB)"

                file_options = {f["path"]: format_file_label(f) for f in files_to_show}

                selected_file_path = st.radio(
                    "选择具体研报",
                    options=list(file_options.keys()),
                    format_func=lambda x: file_options[x],
                    index=0,
                    label_visibility="collapsed"
                )

    with view_col:
        try:
            reader_box = st.container(border=True)
        except TypeError:
            reader_box = st.container()

        with reader_box:
            if selected_file_path and os.path.exists(selected_file_path):
                fname = os.path.basename(selected_file_path)
                content = archive_manager.read_report_content(selected_file_path)
                fstat = os.stat(selected_file_path)
                mtime_str = datetime.datetime.fromtimestamp(fstat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")

                top_h_col1, top_h_col2 = st.columns([2.8, 1.2])
                with top_h_col1:
                    st.markdown(f"""
                    <div style="font-size: 1.15rem; font-weight: 700; color: #0f172a; margin-bottom: 4px;">📑 {fname}</div>
                    <div style="font-size: 0.74rem; color: #64748b; display: flex; align-items: center; gap: 8px;">
                        <span>📦 大小: <strong>{round(fstat.st_size/1024, 1)} KB</strong></span>
                        <span>·</span>
                        <span>🕒 归档时间: <strong>{mtime_str}</strong></span>
                        <span>·</span>
                        <span style="color: #059669; font-weight: 600;">🔒 只读存档</span>
                    </div>
                    """, unsafe_allow_html=True)
                with top_h_col2:
                    st.download_button(
                        "📥 下载当前研报 (.md)",
                        data=content,
                        file_name=fname,
                        mime="text/markdown",
                        use_container_width=True
                    )

                st.markdown('<div style="height: 1px; background: #e2e8f0; margin: 12px 0 16px 0;"></div>', unsafe_allow_html=True)
                st.markdown(content)
            else:
                st.info("👈 请在左侧列表中选择要查阅的研报文档。")

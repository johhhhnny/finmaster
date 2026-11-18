"""桌面端历史研报库：快速筛选归档、定位报告并阅读或下载原文。"""
import datetime
import os
import re

import streamlit as st

from engine.archive_manager import archive_manager


def _clear_archive_filters():
    st.session_state["archive_search_input"] = ""
    st.session_state["archive_type_filter"] = "全部类型"
    st.session_state["archive_company_filter"] = "全部标的"
    st.session_state["archive_selected_path"] = ""


def _report_kind(report: dict, is_topic: bool = False) -> str:
    if is_topic:
        return "专题研究"

    name = report["name"].lower()
    if report.get("is_final") or "最终" in name or "综合" in name:
        return "最终备忘录"
    if "baseline" in name:
        return "数据核验"
    if "earnings" in name or "财报" in name:
        return "财报研究"
    for role in ("段永平", "巴菲特", "芒格", "李录"):
        if role in report["name"]:
            return f"{role}视角"
    return "专项研究"


def _report_label(report: dict) -> str:
    is_topic = report.get("is_topic", False)
    kind = _report_kind(report, is_topic)
    icon = {
        "最终备忘录": "⭐",
        "数据核验": "📊",
        "财报研究": "📈",
        "段永平视角": "🟢",
        "巴菲特视角": "🔵",
        "芒格视角": "🟠",
        "李录视角": "🟣",
        "专题研究": "📑",
        "专项研究": "📄",
    }.get(kind, "📄")
    title = os.path.splitext(report["name"])[0]
    company = "专题" if is_topic else report["company"]
    if kind in {
        "最终备忘录",
        "数据核验",
        "财报研究",
        "段永平视角",
        "巴菲特视角",
        "芒格视角",
        "李录视角",
    }:
        return f"{icon} {kind} · {company}"
    if len(title) > 24:
        title = f"{title[:21]}..."
    return f"{icon} {company} · {title}"


def render_archive():
    """渲染历史研报知识库。"""
    all_data = archive_manager.scan_all_reports()
    total_companies = all_data["total_companies"]
    total_files = all_data["total_files"]
    companies = list(all_data["company_reports"])

    st.markdown(
        f"""
        <div class="archive-header">
            <div>
                <div class="archive-eyebrow">RESEARCH LIBRARY</div>
                <h1>历史研报库</h1>
                <p>按标的浏览归档研究，或搜索报告正文中的关键观点。</p>
            </div>
            <div class="archive-stats">
                <div><span>标的档案</span><strong>{total_companies}</strong></div>
                <div><span>归档报告</span><strong>{total_files}</strong></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        search_col, type_col, company_col, clear_col = st.columns([5, 1.8, 2.2, 1.1])
        with search_col:
            search_kw = st.text_input(
                "搜索研报",
                placeholder="搜索标的、标题或正文关键词，例如：现金流、AI 基建",
                key="archive_search_input",
            )
        with type_col:
            type_options = ["全部类型", "公司研报", "专题研报"]
            if st.session_state.get("archive_type_filter") not in type_options:
                st.session_state["archive_type_filter"] = type_options[0]
            report_type = st.selectbox(
                "报告类型",
                type_options,
                key="archive_type_filter",
            )
        with company_col:
            company_options = ["全部标的"] if report_type == "专题研报" else ["全部标的", *companies]
            if st.session_state.get("archive_company_filter") not in company_options:
                st.session_state["archive_company_filter"] = company_options[0]
            company_filter = st.selectbox(
                "标的",
                company_options,
                key="archive_company_filter",
            )
        with clear_col:
            st.markdown('<div class="archive-clear-spacer"></div>', unsafe_allow_html=True)
            st.button(
                "重置",
                key="archive_clear_filters",
                on_click=_clear_archive_filters,
                use_container_width=True,
            )

    filtered_data = archive_manager.filter_reports(search_kw, data=all_data)
    if report_type == "公司研报":
        filtered_data["topic_reports"] = []
    elif report_type == "专题研报":
        filtered_data["company_reports"] = {}
    if company_filter != "全部标的":
        filtered_data["company_reports"] = {
            company_filter: filtered_data["company_reports"].get(company_filter, [])
        }

    reports = []
    for company, company_reports in filtered_data["company_reports"].items():
        reports.extend(
            {**report, "company": company, "is_topic": False}
            for report in company_reports
        )
    reports.extend(
        {**report, "is_topic": True}
        for report in filtered_data["topic_reports"]
    )
    reports.sort(
        key=lambda report: (
            -report["mtime"],
            report["company"].casefold(),
            report["name"].casefold(),
        )
    )

    st.caption(
        f"显示 {len(reports)} 份报告 · 共 {total_files} 份归档"
        + (f" · 搜索：{search_kw.strip()}" if search_kw.strip() else "")
    )

    if not reports:
        if total_files:
            st.info("没有找到匹配的研报。试试其他关键词，或重置筛选条件。")
        else:
            st.info("暂时还没有归档研报。完成一次分析后，报告会出现在这里。")
        return

    list_col, reader_col = st.columns([1.2, 2.8])
    report_paths = [report["path"] for report in reports]
    if st.session_state.get("archive_selected_path") not in report_paths:
        st.session_state["archive_selected_path"] = report_paths[0]

    with list_col:
        with st.container(border=True):
            st.markdown("#### 研报列表")
            st.caption(f"{len(reports)} 份 · 最近归档优先")
            report_by_path = {report["path"]: report for report in reports}
            with st.container(height=680, key="archive_report_list"):
                selected_path = st.radio(
                    "选择研报",
                    options=report_paths,
                    format_func=lambda path: _report_label(report_by_path[path]),
                    key="archive_selected_path",
                    label_visibility="collapsed",
                )

    selected_report = report_by_path[selected_path]
    with reader_col:
        with st.container(border=True):
            if not os.path.exists(selected_path):
                st.warning("这份研报可能已被移动或删除，请重新选择其他报告。")
                return

            filename = selected_report["name"]
            display_title = re.sub(
                r"^\d+[_-]", "", os.path.splitext(filename)[0]
            ).replace("_", " ").replace("-", " ")
            modified_at = datetime.datetime.fromtimestamp(
                selected_report["mtime"]
            ).strftime("%Y-%m-%d %H:%M")
            title_col, download_col = st.columns([5, 1.35])
            with title_col:
                st.markdown(f"### {display_title}")
                company = "专题研究" if selected_report["is_topic"] else selected_report["company"]
                st.caption(
                    f"{company}  ·  {_report_kind(selected_report, selected_report['is_topic'])}"
                    f"  ·  更新于 {modified_at}"
                    f"  ·  {selected_report['size_kb']:.1f} KB"
                )
            with download_col:
                content = archive_manager.read_report_content(selected_path)
                st.download_button(
                    "下载 Markdown",
                    data=content,
                    file_name=filename,
                    mime="text/markdown",
                    use_container_width=True,
                )

            st.divider()
            with st.container(key="archive_reader"):
                st.markdown(content)

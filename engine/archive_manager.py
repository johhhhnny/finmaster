"""
FinMaster Archive Manager
历史研报知识库管理器：扫描、检索与读取 finmaster/reports 与现有 reports/ 归档研报。
"""
import os
import glob
from typing import Dict, List, Any, Optional

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
FINMASTER_REPORTS = os.path.abspath(os.path.join(CURRENT_DIR, "..", "reports"))
PARENT_REPORTS = os.path.abspath(os.path.join(CURRENT_DIR, "..", "..", "reports"))


class ArchiveManager:
    """研报归档库管理器"""

    def __init__(self):
        self.search_dirs = [FINMASTER_REPORTS]
        if os.path.exists(PARENT_REPORTS) and PARENT_REPORTS != FINMASTER_REPORTS:
            self.search_dirs.append(PARENT_REPORTS)

    def scan_all_reports(self) -> Dict[str, Any]:
        """
        扫描归档库，返回结构化分类：
        - company_reports: {公司/标的名称: [{name, path, size_kb, mtime, is_final}, ...]}
        - topic_reports: [{name, path, size_kb, mtime}, ...] (专题/独立长文)
        """
        company_reports: Dict[str, List[Dict[str, Any]]] = {}
        topic_reports: List[Dict[str, Any]] = []

        seen_paths = set()

        for base_dir in self.search_dirs:
            if not os.path.exists(base_dir):
                continue

            for entry in os.scandir(base_dir):
                # 1. 文件夹形式（通常为公司专项研究包，如 reports/谷歌/）
                if entry.is_dir() and not entry.name.startswith("."):
                    company_name = entry.name
                    md_files = glob.glob(os.path.join(entry.path, "*.md"))
                    for fpath in md_files:
                        if fpath in seen_paths:
                            continue
                        seen_paths.add(fpath)

                        fname = os.path.basename(fpath)
                        fstat = os.stat(fpath)
                        item = {
                            "name": fname,
                            "path": fpath,
                            "company": company_name,
                            "size_kb": round(fstat.st_size / 1024, 1),
                            "mtime": fstat.st_mtime,
                            "is_final": "最终" in fname or "README" in fname or "综合" in fname
                        }
                        company_reports.setdefault(company_name, []).append(item)

                # 2. 根目录下的独立专题 Markdown 研报
                elif entry.is_file() and entry.name.endswith(".md") and not entry.name.startswith("."):
                    if entry.path in seen_paths or entry.name in ("README.md", "SUMMARY.md"):
                        continue
                    seen_paths.add(entry.path)
                    fstat = os.stat(entry.path)
                    topic_reports.append({
                        "name": entry.name,
                        "path": entry.path,
                        "size_kb": round(fstat.st_size / 1024, 1),
                        "mtime": fstat.st_mtime,
                        "company": "专题长文"
                    })

        # 对每个公司的文件排序（最终报告排在最前）
        for cname, flist in company_reports.items():
            flist.sort(key=lambda x: (not x["is_final"], x["name"]))

        company_reports = dict(
            sorted(
                company_reports.items(),
                key=lambda item: (
                    -max(report["mtime"] for report in item[1]),
                    item[0].casefold(),
                ),
            )
        )

        # 专题按修改时间倒序
        topic_reports.sort(key=lambda x: x["mtime"], reverse=True)

        return {
            "company_reports": company_reports,
            "topic_reports": topic_reports,
            "total_companies": len(company_reports),
            "total_files": len(seen_paths)
        }

    def filter_reports(
        self, keyword: str, data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """按标的、文件名或研报正文搜索，可复用已扫描的档案数据。"""
        all_data = data if data is not None else self.scan_all_reports()
        if not keyword or not keyword.strip():
            return all_data

        kw = keyword.strip().casefold()
        filtered_companies = {}
        for cname, flist in all_data["company_reports"].items():
            if kw in cname.casefold():
                filtered_companies[cname] = flist
            else:
                matched_files = [
                    report for report in flist
                    if kw in report["name"].casefold()
                    or kw in self.read_report_content(report["path"]).casefold()
                ]
                if matched_files:
                    filtered_companies[cname] = matched_files

        filtered_topics = [
            t for t in all_data["topic_reports"]
            if kw in t["name"].casefold()
            or kw in self.read_report_content(t["path"]).casefold()
        ]

        return {
            "company_reports": filtered_companies,
            "topic_reports": filtered_topics,
            "total_companies": len(filtered_companies),
            "total_files": sum(len(fl) for fl in filtered_companies.values()) + len(filtered_topics)
        }

    def read_report_content(self, file_path: str) -> str:
        """安全读取研报内容"""
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                return f.read()
        return "❌ 研报文件未找到或已被移除。"


archive_manager = ArchiveManager()

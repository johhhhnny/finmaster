import os
import tempfile
import unittest
from unittest.mock import patch

from engine.archive_manager import ArchiveManager


class ArchiveManagerTests(unittest.TestCase):
    def test_filter_reports_searches_report_body_case_insensitively(self):
        with tempfile.TemporaryDirectory() as reports_dir:
            company_dir = os.path.join(reports_dir, "Example")
            os.makedirs(company_dir)
            report_path = os.path.join(company_dir, "company-review.md")
            with open(report_path, "w", encoding="utf-8") as report:
                report.write("# Company review\n\nA durable pricing moat.")

            manager = ArchiveManager()
            manager.search_dirs = [reports_dir]

            results = manager.filter_reports("PRICING MOAT")

        self.assertEqual(
            [report["name"] for report in results["company_reports"]["Example"]],
            ["company-review.md"],
        )
        self.assertEqual(results["total_files"], 1)

    def test_filter_reports_reuses_scanned_data(self):
        with tempfile.TemporaryDirectory() as reports_dir:
            manager = ArchiveManager()
            manager.search_dirs = [reports_dir]
            scanned_data = manager.scan_all_reports()

            with patch.object(manager, "scan_all_reports", side_effect=AssertionError):
                results = manager.filter_reports("missing", data=scanned_data)

        self.assertEqual(results["total_files"], 0)

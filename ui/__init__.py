"""
FinMaster UI 包导出模块
对外统一暴露视图渲染函数、侧边栏状态与全局定制样式注入接口。
"""
from ui.styles import inject_custom_css
from ui.sidebar import render_sidebar, SidebarState
from ui.workbench import render_workbench
from ui.archive import render_archive
from ui.calculator import render_calculator
from ui.settings import render_settings

__all__ = [
    "inject_custom_css",
    "render_sidebar",
    "SidebarState",
    "render_workbench",
    "render_archive",
    "render_calculator",
    "render_settings",
]

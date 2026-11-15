#!/usr/bin/env python3
"""
FinMaster（价值投资大师工作站）快速启动脚本
支持直接使用 `python3 finmaster/start.py` 或 `cd finmaster && python3 start.py` 一键启动 Web 界面。
"""
import os
import sys
import subprocess
import shutil

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
APP_PATH = os.path.join(CURRENT_DIR, "app.py")

# 优先寻找项目自带的 .venv 虚拟环境中的 streamlit
venv_streamlit = os.path.join(CURRENT_DIR, ".venv", "bin", "streamlit")
if os.path.exists(venv_streamlit):
    streamlit_bin = venv_streamlit
else:
    # 寻找系统 PATH 中的 streamlit 可执行文件
    streamlit_bin = shutil.which("streamlit")
    if not streamlit_bin:
        # 尝试用户默认安装路径
        user_bin = os.path.expanduser("~/Library/Python/3.9/bin/streamlit")
        if os.path.exists(user_bin):
            streamlit_bin = user_bin

if not streamlit_bin:
    # 尝试作为 python 模块调用
    cmd = [sys.executable, "-m", "streamlit", "run", APP_PATH]
else:
    cmd = [streamlit_bin, "run", APP_PATH]

print("=" * 60)
print("🦅 正在启动 FinMaster 价值投资大师工作站...")
print(f"执行命令: {' '.join(cmd)}")
print("=" * 60)

try:
    subprocess.run(cmd, check=True)
except KeyboardInterrupt:
    print("\n👋 FinMaster 已正常退出。")
except Exception as e:
    print(f"\n❌ 启动发生错误: {e}")
